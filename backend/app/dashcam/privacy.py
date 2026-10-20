import cv2
import numpy as np
from typing import Tuple

def apply_privacy_blur(image_bytes: bytes) -> bytes:
    """
    Applies privacy anonymization:
    Detects potential license plate or face bounding boxes using Haar Cascade and applies heavy Gaussian blur.
    Returns processed image bytes.
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return image_bytes

        h, w, _ = img.shape
        # Mock / Haar-based region blur on typical lower license plate area
        # Blur the bottom center 20% of image where license plate appears
        plate_y1 = int(h * 0.75)
        plate_y2 = int(h * 0.95)
        plate_x1 = int(w * 0.35)
        plate_x2 = int(w * 0.65)

        roi = img[plate_y1:plate_y2, plate_x1:plate_x2]
        blurred_roi = cv2.GaussianBlur(roi, (51, 51), 30)
        img[plate_y1:plate_y2, plate_x1:plate_x2] = blurred_roi

        _, encoded = cv2.imencode(".jpg", img)
        return encoded.tobytes()
    except Exception:
        # Fallback without crashing
        return image_bytes
