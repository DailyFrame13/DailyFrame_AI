import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 폴더 생성
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

# ============================
# 1) YOLO Detection 시각화
# ============================

def draw_yolo_detections(image_path, detections, save_path):
    """
    detections = [
        { "label": "...", "bbox": [x1,y1,x2,y2], "confidence": 0.88 },
        ...
    ]
    """

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(image_path)

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        label = det["label"]
        conf = det["confidence"]

        cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(
            img,
            f"{label} {conf:.2f}",
            (x1, y1-5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0,255,0),
            2
        )

    ensure_dir(os.path.dirname(save_path))
    cv2.imwrite(save_path, img)
    return save_path


# ============================
# 2) Cutout(RGBA) 시각화
# ============================

def visualize_cutout(rgba_path, save_path):
    """
    RGBA 누끼 이미지의 투명 영역을 체크하기 위해
    checkerboard 배경 위에 합성해 시각화
    """
    rgba = Image.open(rgba_path).convert("RGBA")
    w, h = rgba.size

    # 체커보드 배경 만들기
    checker = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(checker)
    tile = 40
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            if (x // tile + y // tile) % 2 == 0:
                draw.rectangle([x, y, x+tile, y+tile], fill=(200,200,200))

    # 합성
    composed = checker.copy()
    composed.paste(rgba, (0,0), rgba)

    ensure_dir(os.path.dirname(save_path))
    composed.save(save_path)
    return save_path


# ============================
# 3) Background Zone 시각화
# ============================

def visualize_background_zones(bg_image_path, metadata, save_path):
    """
    metadata = BACKGROUND_TEMPLATES[key]["metadata"]
    safe_zones = [ (x1,y1,x2,y2,"zone_name"), ... ]
    """

    img = cv2.imread(bg_image_path)
    if img is None:
        raise FileNotFoundError(bg_image_path)

    zones = metadata.get("safe_zones", [])

    for (x1,y1,x2,y2,zone_name) in zones:
        cv2.rectangle(img, (x1,y1), (x2,y2), (255,0,0), 2)
        cv2.putText(
            img,
            zone_name,
            (x1 + 5, y1 + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,0,0),
            2
        )

    ensure_dir(os.path.dirname(save_path))
    cv2.imwrite(save_path, img)
    return save_path