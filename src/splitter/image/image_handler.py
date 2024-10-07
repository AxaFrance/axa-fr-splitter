from __future__ import annotations

from pathlib import Path
from collections.abc import Iterable
from typing import cast

import cv2
import numpy as np

from splitter.errors import ConvertError
from splitter.interfaces import IExtensionHandler
from splitter.file import File, ImageContent, build_file, FileOrError, MetadataType
from splitter.image.image import normalize_size


class ConvertImageError(ConvertError):
    pass


class ImageHandler(IExtensionHandler):
    def __init__(self, max_size: int | None = None) -> None:
        self.max_size = max_size

    def to_files(self, file: File) -> Iterable[FileOrError]:
        image_path = Path(file.vpath)
        filename = image_path.name
        image_filename = f"{filename}.png"

        # Decode Image
        image_numpy_array = np.frombuffer(file.stream.read(), np.uint8)
        image_cv = cv2.imdecode(image_numpy_array, cv2.IMREAD_ANYCOLOR)

        # Resize Image
        image_cv, ratio = normalize_size(image_cv, self.max_size)
        height, width = image_cv.shape[:2]

        yield build_file(
            image_filename,
            file_bytes=cv2.imencode(".png", image_cv)[1].tobytes(),
            contents=[
                ImageContent(framework="opencv", content_type="image", image=image_cv)
            ],
            metadata=cast(
                MetadataType,
                {
                    "total_pages": 1,
                    "original_filename": filename,
                    "page_number": 1,
                    "width": width,
                    "height": height,
                    "resized_ratio": ratio,
                },
            ),
        )
