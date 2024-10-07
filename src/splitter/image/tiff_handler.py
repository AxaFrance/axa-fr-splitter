from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO, cast
from collections.abc import Iterable
from itertools import islice

import cv2
import numpy as np
from returns.result import safe, Failure

from splitter.errors import ReadError
from splitter.interfaces import IExtensionHandler
from splitter.file import ImageContent, build_file, FileOrError, File, MetadataType
from splitter.image.image import normalize_size

if TYPE_CHECKING:
    from cv2.typing import MatLike


class ReadTiffError(ReadError):
    pass


class TifHandler(IExtensionHandler):
    def __init__(
        self, max_pages: int | None = None, max_size: int | None = None
    ) -> None:
        self.max_pages = max_pages
        self.max_size = max_size

    def to_files(self, file: File) -> Iterable[FileOrError]:
        filename = Path(file.vpath).name

        images_result = _read_tiff(file.stream)

        if isinstance(images_result, Failure):
            yield images_result
            return

        images_cv = images_result.unwrap()
        total_pages = len(images_cv)
        number_images = min(self.max_pages or total_pages, total_pages)

        images = islice(images_cv, number_images)
        for index, image_cv in enumerate(images):
            image_filename = f"{filename}-{index}.png"
            resized_image, resized_ratio = normalize_size(image_cv, self.max_size)
            height, width = resized_image.shape[:2]

            yield build_file(
                image_filename,
                file_bytes=cv2.imencode(".png", resized_image)[1].tobytes(),
                contents=[ImageContent(framework="opencv", image=resized_image)],
                metadata=cast(
                    MetadataType,
                    {
                        "original_filename": filename,
                        "page_number": index + 1,
                        "total_pages": total_pages,
                        "width": width,
                        "height": height,
                        "resized_ratio": resized_ratio,
                    },
                ),
            )


@safe(exceptions=(ReadTiffError,))
def _read_tiff(file_stream: BinaryIO) -> list[MatLike]:
    file_bytes = file_stream.read()
    images_numpy_array = np.frombuffer(file_bytes, np.uint8)
    success, images_cv = cv2.imdecodemulti(images_numpy_array, cv2.IMREAD_ANYCOLOR)

    if not success:
        raise ReadTiffError("Error while converting tiff to png")

    if TYPE_CHECKING:
        images_cv = cast(list[MatLike], images_cv)

    return images_cv
