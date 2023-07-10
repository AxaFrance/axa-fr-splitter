from pathlib import Path
from typing import IO

import cv2
import numpy as np

from splitter.errors import ConvertError
from splitter.extension_handler_interface import IExtensionHandler
from splitter.file import build_file
from splitter.image import normalize_size


class ConvertImageError(ConvertError):
    pass


class ImageHandler(IExtensionHandler):
    def __init__(self, resize_image_size_max=2200):
        self.resize_image_size_max = resize_image_size_max

    def to_files(self, filepath: str, file_stream: IO):
        image_path = Path(filepath)
        filename = image_path.name
        image_numpy_array = np.frombuffer(file_stream.read(), np.uint8)
        image_cv = cv2.imdecode(image_numpy_array, cv2.IMREAD_ANYCOLOR)
        image_filename = f"{filename}.png"
        image_cv_resized, resized_ratio = normalize_size(
            image_cv, self.resize_image_size_max
        )
        (height, width) = image_cv_resized.shape[:2]
        yield build_file(
            image_filename,
            file_bytes=cv2.imencode(".png", image_cv_resized)[1].tobytes(),
            metadata={
                "total_pages": 1,
                "original_filename": filename,
                "page_number": 1,
                "width": width,
                "height": height,
                "resized_ratio": resized_ratio,
            },
        )
