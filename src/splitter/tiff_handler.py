from pathlib import Path
from typing import IO
import cv2
import numpy as np

from splitter.errors import ConvertError
from splitter.extension_handler_interface import IExtensionHandler
from splitter.file import build_file
from splitter.image import normalize_size


class ConvertTiffError(ConvertError):
    pass


class TifHandler(IExtensionHandler):
    def __init__(self, limit_number_page=2, resize_image_size_max=2200):
        self.limit_number_page = limit_number_page
        self.resize_image_size_max = resize_image_size_max

    def to_files(self, filepath: str, file_stream: IO):
        filename = Path(filepath).name
        images_numpy_array = np.frombuffer(file_stream.read(), np.uint8)
        success, images_cv = cv2.imdecodemulti(images_numpy_array, cv2.IMREAD_ANYCOLOR)
        if not success:
            raise ConvertTiffError("Error while converting tiff to png")
        total_pages = len(images_cv)
        number_images = min(self.limit_number_page, total_pages)

        for index in range(number_images):
            image_cv = images_cv[index]
            image_filename = f"{filename}-{index}.png"
            image_cv_resized, resized_ratio = normalize_size(
                image_cv, self.resize_image_size_max
            )
            (height, width) = image_cv_resized.shape[:2]
            yield build_file(
                image_filename,
                file_bytes=cv2.imencode(".png", image_cv_resized)[1].tobytes(),
                metadata={
                    "original_filename": filename,
                    "page_number": index + 1,
                    "total_pages": total_pages,
                    "width": width,
                    "height": height,
                    "resized_ratio": resized_ratio,
                },
            )
