import os
import json
from typing import Dict, List, Tuple

from PIL import Image

import torch

from models.collage_diffusion import (
    load_collage_pipeline,
    Control,
)


def _build_layers_from_plan(
    plan: Dict,
    canvas_size: Tuple[int, int] = (512, 512),
) -> Tuple[List[Dict], str, List[float], List[float], str]:
    """
    composition_plan.json 을 Collage Diffusion의 preprocess_layers 에 들어가는
    layers 리스트 형식으로 변환.

    예상하는 composition_plan.json 구조 예시:

    {
      "background": {
        "key": "sns_upload_cozy",
        "image_path": "data/backgrounds/sns업로드_cozy.png",
        "metadata": {...}   # (optional)
      },
      "objects": [
        {
          "object_label": "cup",
          "source_image": "img1.jpg",
          "rgba_path": "data/cutouts/img1_0_cup.png",
          "target_zone": "table_area",
          "coordinates": {
            "x": 300,
            "y": 900,
            "width": 200,
            "height": 200
          },
          "priority": 5,
          "scale": 0.8
        },
        ...
      ],
      "collage_prompt": "A cozy cafe table with a cup and dessert..."
    }
    """

    bg_info = plan["background"]
    bg_path = bg_info["image_path"]

    # 배경 이미지 크기 얻기 (좌표 → 정규화에 사용)
    bg_img = Image.open(bg_path).convert("RGB")
    bg_w, bg_h = bg_img.size

    objects = plan.get("objects", [])

    layers: List[Dict] = []
    noise_strengths: List[float] = []
    neg_strengths: List[float] = []

    # 간단하게 object_label들을 묶어서 전체 collage 프롬프트를 만들 수도 있음
    collage_prompt = plan.get(
        "collage_prompt",
        "a photo of " + ", ".join(o["object_label"] for o in objects),
    )

    for obj in objects:
        rgba_path = obj["rgba_path"]
        coords = obj["coordinates"]
        label = obj["object_label"]

        # 중심 좌표 (배경 기준) → 0~1 정규화
        cx = coords["x"] + coords["width"] / 2
        cy = coords["y"] + coords["height"] / 2

        pos_x_norm = cx / bg_w
        pos_y_norm = cy / bg_h

        # 상대적인 스케일 (대충 최대 변 기준으로 비율만 맞추는 정도)
        max_bg_dim = max(bg_w, bg_h)
        obj_max_dim = max(coords["width"], coords["height"])
        scale_norm = obj_max_dim / max_bg_dim

        # Collage UI 형식에 맞춘 layer dict
        layers.append(
            {
                # 원래는 URL을 기대하지만, file:// 로 로컬 경로도 urlopen 가능
                "originalImgUrl": f"file://{os.path.abspath(rgba_path)}",
                # 우리는 polygon이 없으므로 빈 리스트 → 전체 마스크로 처리
                "polygon": [],
                # 이 레이어를 설명하는 짧은 텍스트 (토큰 매칭용)
                "textPrompt": label,
                "transform": {
                    # 0~1 정규화 좌표 (Collage 코드 안에서 512배 해서 사용)
                    "position": {"x": float(pos_x_norm), "y": float(pos_y_norm)},
                    "scale": float(scale_norm),
                    "rotation": 0.0,
                },
                # 레이어별 노이즈 강도 (일단 전부 1.0으로 두고 시작)
                "noiseStrength": 1.0,
                "wordEmbedding": None,
            }
        )

        noise_strengths.append(1.0)
        # CAC negative strength: 배경으로 퍼지는 부분을 어느 정도 억제할지
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

    Args:
        composition_plan_path: run_background_selection 에서 만든 composition_plan.json 경로
        paths: PATHS 딕셔너리 (setup_env 의 반환값)
        device: "cuda" 혹은 "cpu"
        torch_dtype: torch.float16, bfloat16, float32 등

    Returns:
        최종 콜라주 이미지 파일 경로 (str)
    """

    # ---------------------------------------------------
    # 0) composition_plan.json 로드
    # ---------------------------------------------------
    with open(composition_plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)

    layers, bg_path, noise_strengths, neg_strengths, collage_prompt = _build_layers_from_plan(plan)

    # ---------------------------------------------------
    # 1) Collage Diffusion 파이프라인 로드
    # ---------------------------------------------------
    pipe = load_collage_pipeline(device=device, dtype=torch_dtype)

    # 배경 이미지는 512x512로 리사이즈해서 Collage 캔버스로 사용
    bg_img = Image.open(bg_path).convert("RGB").resize((512, 512))

    # ---------------------------------------------------
    # 2) 레이어 전처리 (ImageLayer + mask pyramid + attention_mod)
    # ---------------------------------------------------
    composite_image, mask_layers, attention_mod, collage_prompt = pipe.preprocess_layers(
        layers=layers,
        cac_strengths=noise_strengths,
        cac_negative_strengths=neg_strengths,
        collage_prompt=collage_prompt,
        use_cac=True,
        collage_src=bg_img,
    )

    # ---------------------------------------------------
    # 3) 마스크 생성 (어디를 얼마나 강하게 재그리느냐)
    # ---------------------------------------------------
    collage_mask = pipe.generate_mask(
        mask_layers=mask_layers,
        img2img_strength=0.8,          # 전체 inpainting 강도
        noise_strengths=noise_strengths,
        noise_blur=10,
    )

    # 디버그 저장 (선택 사항)
    os.makedirs(paths["debug"], exist_ok=True)
    composite_image.save(os.path.join(paths["debug"], "collage_composite_input.png"))
    collage_mask.save(os.path.join(paths["debug"], "collage_mask.png"))

    # ---------------------------------------------------
    # 4) Collage Diffusion 본체 실행
    # ---------------------------------------------------
    out = pipe.collage(
        prompt=collage_prompt,
        image=composite_image,
        mask_image=collage_mask,
        controls=[Control.CANNY],      # Canny 기반 ControlNet 사용
        attention_mod=attention_mod,   # CAC attention 수정
        strength=0.8,
        num_inference_steps=30,
        guidance_scale=7.5,
        output_type="pil",
    )

    final_img = out.images[0]

    # ---------------------------------------------------
    # 5) 최종 결과 저장
    # ---------------------------------------------------
    os.makedirs(paths["outputs"], exist_ok=True)
    out_path = os.path.join(paths["outputs"], "final_collage.png")
    final_img.save(out_path)

    return out_path
