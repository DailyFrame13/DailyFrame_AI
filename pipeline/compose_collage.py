# pipeline/compose_collage.py

import os
import json
from typing import Dict, List, Tuple

from PIL import Image
import torch

from models.collage_diffusion import load_collage_pipeline, Control

# 🔥 metadata.py 안에서 우리가 만든 BACKGROUND_TEMPLATES import
#  - metadata.py 안에 BACKGROUND_TEMPLATES = build_background_templates() 가 있어야 함
from background.metadata import BACKGROUND_TEMPLATES



def _build_layers_from_plan(
    plan: Dict,
    canvas_size: Tuple[int, int] = (512, 512),
) -> Tuple[List[Dict], str, List[float], List[float], str]:
    """
    현재 사용하는 composition_plan.json 구조에 맞춘 변환 함수.

    예상 구조:

    {
      "plan": {
        "selected_background": "sns_upload__cozy",
        "reasoning": "...",
        "overall_mood": "cozy",
        "object_placement": [ ... ]   # (좌표는 없음)
      },
      "coordinates": [               # (좌표 포함 최종 배치)
        {
          "object_label": "apple",
          "source_image": "coco10.jpg",
          "rgba_path": "./data/cutouts/coco10_2_apple.png",
          "target_zone": "sns_upload__cozy__cup",
          "coordinates": { "x": 545, "y": 995, "width": 200, "height": 200 },
          "priority": 5
        },
        ...
      ]
    }
    """

    # 1) plan / coordinates 분리
    base_plan = plan["plan"]
    objects = plan["coordinates"]

    # 2) 배경 키 → 실제 경로
    bg_key = base_plan["selected_background"]  # ex) "sns_upload__cozy"
    if bg_key not in BACKGROUND_TEMPLATES:
        raise KeyError(f"Unknown background key from plan: {bg_key}")

    bg_entry = BACKGROUND_TEMPLATES[bg_key]    # { "path": ..., "metadata": ... }
    bg_path = bg_entry["path"]

    # 3) 콜라주 프롬프트
    collage_prompt = base_plan.get(
        "collage_prompt",
        "a photo of " + ", ".join(o["object_label"] for o in objects),
    )

    # 4) 배경 크기 (좌표 정규화용)
    bg_img = Image.open(bg_path).convert("RGB")
    bg_w, bg_h = bg_img.size

    layers: List[Dict] = []
    noise_strengths: List[float] = []
    neg_strengths: List[float] = []

    # 5) coordinates 기반으로 Collage 레이어 구성
    for obj in objects:
        rgba_path = obj["rgba_path"]
        coords = obj["coordinates"]
        label = obj["object_label"]

        # 중심 좌표
        cx = coords["x"] + coords["width"] / 2
        cy = coords["y"] + coords["height"] / 2

        pos_x_norm = cx / bg_w
        pos_y_norm = cy / bg_h

        max_bg_dim = max(bg_w, bg_h)
        obj_max_dim = max(coords["width"], coords["height"])
        scale_norm = obj_max_dim / max_bg_dim

        layers.append(
            {
                "originalImgUrl": f"file://{os.path.abspath(rgba_path)}",
                "polygon": [],
                "textPrompt": label,
                "transform": {
                    "position": {"x": float(pos_x_norm), "y": float(pos_y_norm)},
                    "scale": float(scale_norm),
                    "rotation": 0.0,
                },
                "noiseStrength": 1.0,
                "wordEmbedding": None,
            }
        )

        noise_strengths.append(1.0)
        neg_strengths.append(0.3)

    return layers, bg_path, noise_strengths, neg_strengths, collage_prompt


def run_collage(
    composition_plan_path: str,
    paths: Dict[str, str],
    device: str = "cuda",
    torch_dtype: torch.dtype = torch.float16,
) -> str:
    """
    1) composition_plan.json 로드
    2) plan → Collage Diffusion용 layers / mask / attention
    3) pipeline.collage(...) 실행
    4) 최종 이미지를 outputs 에 저장하고 경로 반환
    """

    # 0) composition_plan.json 로드
    with open(composition_plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)

    # ✅ 여기서 'background'라는 key는 전혀 사용하지 않음
    layers, bg_path, noise_strengths, neg_strengths, collage_prompt = _build_layers_from_plan(plan)

    # 1) Collage Diffusion 파이프라인 로드
    pipe = load_collage_pipeline(device=device, dtype=torch_dtype)

    # 배경 이미지는 512x512로 리사이즈해서 Collage 캔버스로 사용
    bg_img = Image.open(bg_path).convert("RGB").resize((512, 512))

    # 2) 레이어 전처리
    composite_image, mask_layers, attention_mod, collage_prompt = pipe.preprocess_layers(
        layers=layers,
        cac_strengths=noise_strengths,
        cac_negative_strengths=neg_strengths,
        collage_prompt=collage_prompt,
        use_cac=True,
        collage_src=bg_img,
    )

    # 3) 마스크 생성
    collage_mask = pipe.generate_mask(
        mask_layers=mask_layers,
        img2img_strength=0.5,
        noise_strengths=noise_strengths,
        noise_blur=10,
    )

    os.makedirs(paths["debug"], exist_ok=True)
    composite_image.save(os.path.join(paths["debug"], "collage_composite_input.png"))
    collage_mask.save(os.path.join(paths["debug"], "collage_mask.png"))

    # 4) Collage Diffusion 실행
    out = pipe.collage(
        prompt=collage_prompt,
        image=composite_image,
        mask_image=collage_mask,
        controls=[Control.CANNY],
        attention_mod=attention_mod,
        strength=0.45,
        num_inference_steps=30,
        guidance_scale=5.5,
        output_type="pil",
    )

    final_img = out.images[0]

    # 5) 결과 저장
    os.makedirs(paths["outputs"], exist_ok=True)
    out_path = os.path.join(paths["outputs"], "final_collage.png")
    final_img.save(out_path)

    return out_path
