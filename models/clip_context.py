import os
import torch
import clip
from PIL import Image
from typing import Dict, Any, List
from labels.scene_labels import (
    BACKGROUND_LABELS,
    ACTIVITY_LABELS,
    STYLE_LABELS,
)
from models.yolo_seg import load_image_with_orientation

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ---------------------------------------------------------
# 1) Lazy Loading 구조 (import 시점에 모델 로딩 X)
# ---------------------------------------------------------
_clip_model = None
_preprocess = None

def load_clip_model():
    global _clip_model, _preprocess
    if _clip_model is None:
        print("🔄 Loading CLIP (ViT-B/32) ...")
        _clip_model, _preprocess = clip.load("ViT-B/32", device=DEVICE)
    return _clip_model, _preprocess


# ---------------------------------------------------------
# 2) 텍스트 임베딩 캐싱 (속도 5~10배 향상)
# ---------------------------------------------------------
_cached_text_embeddings = {}

def get_text_features(label_list: List[str], category: str, device: str = DEVICE):
    """
    label_list + category 조합으로 텍스트 임베딩 캐시
    """
    key = f"{category}_" + ",".join(label_list)

    if key in _cached_text_embeddings:
        return _cached_text_embeddings[key]

    clip_model, _ = load_clip_model()
    text_inputs = clip.tokenize(
        [f"a {label} {category}" for label in label_list]
    ).to(device)

    with torch.no_grad():
        txt_feat = clip_model.encode_text(text_inputs)
        txt_feat /= txt_feat.norm(dim=-1, keepdim=True)

    _cached_text_embeddings[key] = txt_feat
    return txt_feat


# ---------------------------------------------------------
# 3) CLIP Scene Context Extractor Class
# ---------------------------------------------------------
class ClipContextExtractor:
    def __init__(self, device: str = DEVICE):
        self.device = device
        self.clip_model, self.preprocess = load_clip_model()

    def _get_top_label(self, image_tensor, label_list, category: str):
        txt_feats = get_text_features(label_list, category, self.device)

        with torch.no_grad():
            img_feat = self.clip_model.encode_image(image_tensor)
            img_feat /= img_feat.norm(dim=-1, keepdim=True)

            sims = (img_feat @ txt_feats.T).squeeze().cpu().numpy()

        idx = int(sims.argmax())
        return label_list[idx], float(sims[idx])

    def compute(self, image_path: str) -> Dict[str, Any]:
        """이미지에서 배경/활동/스타일을 CLIP으로 추출"""
        image = load_image_with_orientation(image_path).convert("RGB")
        image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)

        bg, bg_conf = self._get_top_label(image_tensor, BACKGROUND_LABELS, "background")
        act, act_conf = self._get_top_label(image_tensor, ACTIVITY_LABELS, "activity")
        sty, sty_conf = self._get_top_label(image_tensor, STYLE_LABELS, "style")

        return {
            "filename": os.path.basename(image_path),
            "scene_context": {
                "background": {"label": bg, "confidence": bg_conf},
                "activity": {"label": act, "confidence": act_conf},
                "style": {"label": sty, "confidence": sty_conf},
            }
        }

_extractor = ClipContextExtractor()

def compute_scene_context(image_path: str) -> Dict[str, Any]:
    """
    analyze_images에서 바로 쓰기 위한 헬퍼 함수.
    image_path를 받아서 scene_context dict만 반환.
    """
    result = _extractor.compute(image_path)
    # result 구조: { "filename": ..., "scene_context": { ... } }
    return result["scene_context"]
