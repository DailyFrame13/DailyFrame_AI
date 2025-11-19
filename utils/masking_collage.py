import numpy as np
from typing import List, Dict, Tuple
from PIL import Image
import matplotlib.path as mpath


def generate_mask(
    polygon: List[Dict[str, float]],
    img_width: int,
    img_height: int,
) -> np.ndarray:
    """
    UI에서 넘어오는 polygon 클릭 좌표 리스트를 받아
    (H, W) 형태의 0/1 마스크로 변환.

    polygon: [{"x": 0.12, "y": 0.35}, ...]  (정규화 좌표 0~1)
    """
    if not polygon:
        # 클릭이 없으면 전체를 1로 (전체 레이어 사용)
        return np.ones((img_height, img_width), dtype=np.uint8)

    path = mpath.Path(
        [(p["x"] * img_width, p["y"] * img_height) for p in polygon]
    )

    mask = np.zeros((img_height, img_width), dtype=np.uint8)

    # 단순 for-loop 버전 (512x512 기준이면 속도 괜찮음)
    for i in range(img_height):
        for j in range(img_width):
            if path.contains_point((j, i)):
                mask[i, j] = 1

    return mask


def compute_bounding_box(mask: np.ndarray) -> Tuple[int, int, int, int]:
    """
    마스크가 1인 영역의 최소 bounding box (xmin, ymin, xmax, ymax) 반환
    """
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)

    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin, xmax = np.where(cols)[0][[0, -1]]

    return xmin, ymin, xmax, ymax


def apply_mask(
    img: Image.Image,
    mask: np.ndarray,
) -> Image.Image:
    """
    RGBA 이미지에 mask를 alpha로 곱하고,
    객체 영역만 남도록 bounding box로 crop.
    """
    arr = np.array(img)

    # RGBA 전제 (collage용 레이어는 대부분 RGBA라서 그대로 사용)
    # 혹시 RGB로 들어올 경우를 대비해 한 번 체크해도 됨.
    if arr.shape[-1] == 3:
        alpha = np.ones((*arr.shape[:2], 1), dtype=np.uint8) * 255
        arr = np.concatenate([arr, alpha], axis=-1)

    # alpha 채널에 mask 적용
    arr[:, :, 3] = arr[:, :, 3] * mask

    # bounding box 계산 & crop
    xmin, ymin, xmax, ymax = compute_bounding_box(mask)
    cropped = arr[ymin : ymax + 1, xmin : xmax + 1, :]

    return Image.fromarray(cropped)