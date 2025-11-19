import numpy as np
from PIL import Image
import cv2

def apply_mask_full(img: Image.Image, mask: np.ndarray) -> Image.Image:
    """
    YOLO segmentation mask를 원본 이미지 크기에 맞춰 리사이즈하고,
    객체 외 영역을 투명 처리하여 RGBA cutout 이미지를 생성한다.

    Args:
        img (PIL.Image): 원본 이미지 (PIL 객체, RGB 또는 RGBA)
        mask (np.ndarray): YOLO segmentation mask (h, w)

    Returns:
        PIL.Image: RGBA cutout 이미지
    """

    # 1) PIL → numpy array 변환
    img_arr = np.array(img)

    # 2) RGB → RGBA 변환
    if img_arr.shape[-1] == 3:
        alpha_channel = np.full((img_arr.shape[0], img_arr.shape[1], 1), 255, dtype=np.uint8)
        img_arr = np.concatenate([img_arr, alpha_channel], axis=-1)

    H, W = img_arr.shape[:2]

    # 3) mask 유효성 검증
    if mask.ndim != 2:
        raise ValueError(f"Mask must be 2D, got shape {mask.shape}")

    # 4) YOLO mask → 원본 해상도로 리사이즈
    mask_resized = cv2.resize(mask, (W, H), interpolation=cv2.INTER_NEAREST)

    # 5) 이진 마스크로 변환
    mask_binary = (mask_resized > 0.5).astype(np.uint8)

    # 6) 알파 채널에 적용
    #    객체 부분 = 255
    #    배경 부분 = 0  (투명)
    img_arr[:, :, 3] = img_arr[:, :, 3] * mask_binary

    # 7) numpy → PIL Image 변환
    return Image.fromarray(img_arr.astype(np.uint8))
