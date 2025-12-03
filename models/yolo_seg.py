# models/yolo_seg.py

import os
import numpy as np
from typing import List, Dict
from PIL import Image, ImageOps

# ⚠️ safe_globals 등록 이후에 YOLO import
from ultralytics import YOLO
from utils.masks import apply_mask_full


DEVICE = "cuda" if os.environ.get("USE_GPU", "1") == "1" else "cpu"

# ------------------------------------------------------------------
# Lazy Loading YOLO Model (import 시점에 GPU 점유 X)
# ------------------------------------------------------------------
_yolo_model = None

def load_yolo_model(model_path="yolov8s-seg.pt"):
    global _yolo_model
    if _yolo_model is None:
        print(f"🔄 Loading YOLO model: {model_path}")
        _yolo_model = YOLO(model_path)
    return _yolo_model


# ------------------------------------------------------------------
# 이미지 방향 보정
# ------------------------------------------------------------------
def load_image_with_orientation(path: str):
    img = Image.open(path)
    return ImageOps.exif_transpose(img)


# ------------------------------------------------------------------
# 객체 감지 + RGBA 누끼생성
# output_dir은 main.py에서 주입
# ------------------------------------------------------------------
def detect_objects(
    image_path: str,
    output_dir: str,
    conf_threshold: float = 0.65,
    imgsz: int = 960
) -> List[Dict]:
    """
    YOLOv8 segmentation을 이용해:
    - bbox
    - mask
    - RGBA cutout (누끼)
    를 추출한다.

    Args:
        image_path: 이미지 파일 경로
        output_dir: RGBA cutouts 저장 폴더
        conf_threshold: 감지 confidence threshold
        imgsz: YOLO 입력 해상도
    """

    os.makedirs(output_dir, exist_ok=True)

    # 이미지 방향 보정
    pil_img = load_image_with_orientation(image_path).convert("RGB")
    img_np = np.array(pil_img)

    # YOLO 로드
    yolo = load_yolo_model()

    # 예측
    results = yolo.predict(img_np, imgsz=imgsz, conf=conf_threshold)

    if not results or results[0].masks is None:
        print(f"[WARN] {image_path} → 객체 감지 실패")
        return []

    # RGBA base image
    pil_rgba = pil_img.convert("RGBA")

    masks = results[0].masks.data
    boxes = results[0].boxes.xyxy.cpu().numpy()
    confs = results[0].boxes.conf.cpu().numpy()
    classes = results[0].boxes.cls.cpu().numpy()
    names = results[0].names

    base = os.path.splitext(os.path.basename(image_path))[0]
    objects = []

    for i, mask in enumerate(masks):
        conf = float(confs[i])
        if conf < conf_threshold:
            continue

        x1, y1, x2, y2 = boxes[i].astype(int).tolist()
        label = names[int(classes[i])]

        # 누끼 생성
        mask_np = mask.cpu().numpy()
        rgba_img = apply_mask_full(pil_rgba, mask_np)

        save_path = os.path.join(
            output_dir,
            f"{base}_{i}_{label}.png"
        )
        rgba_img.save(save_path)

        objects.append({
            "label": label,
            "confidence": conf,
            "rgba_path": save_path.replace("\\", "/"),
            "bbox": [x1, y1, x2, y2]
        })

    return objects