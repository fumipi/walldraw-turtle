import cv2
import numpy as np
from PIL import Image
from typing import Union, BinaryIO

def load_image(path_or_buffer: Union[str, bytes, BinaryIO]) -> np.ndarray:
    """
    画像ファイル（PNG/JPEG/WebP 等）をグレースケールで読み込む。
    まず OpenCV で試し、失敗したら Pillow へフォールバック。
    """
    # ファイルパス／バイナリデータの場合
    if isinstance(path_or_buffer, (str, bytes)):
        img = cv2.imread(path_or_buffer, cv2.IMREAD_GRAYSCALE)
        if img is None:
            pil = Image.open(path_or_buffer).convert("L")
            img = np.array(pil)
        return img

    # ファイルライクオブジェクトの場合
    pil = Image.open(path_or_buffer).convert("L")
    return np.array(pil)

def save_text(filename: str, text: str) -> None:
    """
    汎用テキスト保存 (SVG, CSV, G-code など)。
    """
    with open(filename, "w") as f:
        f.write(text)
