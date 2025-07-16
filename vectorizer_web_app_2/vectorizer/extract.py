import cv2
import numpy as np
from skimage.morphology import skeletonize
import sknw

def preprocess(
    img: np.ndarray,
    blur_ksize: int,
    canny_low: int,
    canny_high: int
) -> np.ndarray:
    """
    入力グレースケール画像 → GaussianBlur → Canny → Skeleton (scikit-image)
    戻り値: uint8 の 0/255 スケルトンマスク
    """
    blurred = cv2.GaussianBlur(img, (blur_ksize, blur_ksize), 0)
    edges = cv2.Canny(blurred, canny_low, canny_high)
    bn = edges > 0
    sk = skeletonize(bn)
    return (sk.astype(np.uint8) * 255)

def image_to_polyline(mask: np.ndarray) -> list[np.ndarray]:
    """
    スケルトンマスク (0/255) から sknw でグラフ化 → 生ポリライン取得。
    戻り値: list of (N,2) ndarray in (x, y) order, pixel coordinates
    """
    graph = sknw.build_sknw(mask > 0, multi=True)
    polylines: list[np.ndarray] = []
    for u, v, key, data in graph.edges(keys=True, data=True):
        pts = np.array(data['pts'])  # shape=(N,2) as (row, col)
        xs = pts[:, 1]
        ys = pts[:, 0]
        polylines.append(np.vstack([xs, ys]).T)
    return polylines
