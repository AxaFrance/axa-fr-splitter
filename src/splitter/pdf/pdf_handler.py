from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, cast, TypedDict
from collections.abc import Iterable

import cv2
import fitz
import numpy as np
from fitz import Pixmap

from splitter.file import (
    File,
    build_file,
    FileOrError,
    MetadataType,
    TextContent,
    ImageContent,
    FileContent,
)
from splitter.errors import ConvertError
from splitter.interfaces import IExtensionHandler
from splitter.image.image import normalize_size


class PDFMetadataType(TypedDict, total=False):
    page_number: int
    total_pages: int
    content: str
    width: int
    height: int
    resized_ratio: float
    original_filename: str


class ConvertPdfError(ConvertError):
    pass


@dataclass
class PdfHandlerParams:
    always_extract_image: bool = True
    optimize_scans: bool = True
    dpi: int = 300

    image_size_threshold: int = 1400
    image_max_size: int = 2200
    text_size_min_before_fallback_to_extract_images: int = 40
    normalize_text: bool = False


class FitzPdfHandler(IExtensionHandler):
    _exception = ConvertPdfError

    def __init__(self, params: PdfHandlerParams | None = None) -> None:
        self.params = params or PdfHandlerParams()

    def to_files(self, file: File) -> Iterable[FileOrError]:
        with self._read_pdf(file.stream) as document:
            name = Path(file.vpath).name

            for metadata, contents, image_bytes in _get_pages(document, self.params):
                page_number = metadata["page_number"]
                filename = f"{name}-{page_number}.png"
                metadata["original_filename"] = name

                yield build_file(
                    filename,
                    file_bytes=image_bytes,
                    contents=contents,
                    metadata=cast(MetadataType, metadata),
                )

    @staticmethod
    def _read_pdf(file_stream: BinaryIO) -> fitz.Document:
        return fitz.open(stream=file_stream.read(), filetype="pdf")


def convert_pixmap_to_rgb(pixmap: Pixmap) -> Pixmap:
    """Convert to rgb in order to write on png."""
    # check if it is already on rgb
    if pixmap.n < 4:
        return pixmap
    else:
        return fitz.Pixmap(fitz.csRGB, pixmap)


def get_normalized_text(text: str) -> str:
    """Normalize text. This is useful for redis."""
    if len(text) == 0:
        return ""
    text_cleaned = re.sub(r"[^a-zA-Z \n\réèçàùô\'ëî,./@0-9:]", "", text)
    text_cleaned = "\n".join([line.strip() for line in text_cleaned.splitlines()])
    text_cleaned = re.sub(r"\n\s*\n", "\n", text_cleaned, flags=re.MULTILINE)
    if len(text_cleaned) > 0 and len(text) / len(text_cleaned) >= 1.5:
        return ""
    return text_cleaned


def _get_scan_pix(
    optimize_scans: bool,
    document: fitz.Document,
    page: fitz.Page,
    image_size_threshold: int,
) -> Pixmap | None:
    if not optimize_scans:
        return None

    # Optimization gain rapidité:
    # beaucoup de PDF contiennent 1 image (la page complete scannée)
    images = page.get_images()
    number_images = len(images)
    if number_images != 1:
        return None

    # On extrait les images de la page on met un seuil car certain
    # scanner et word découpe une unique image en plein de petite image
    xref = images[0][0]
    pix = fitz.Pixmap(document, xref)

    if pix.width > image_size_threshold and pix.height > image_size_threshold:
        return pix

    return None


def _get_pix(
    document: fitz.Document, page: fitz.Page, params: PdfHandlerParams
) -> Pixmap:
    pix = _get_scan_pix(
        params.optimize_scans, document, page, params.image_size_threshold
    )

    if pix is not None:
        return pix

    dpi = params.dpi / 72
    matrix = fitz.Matrix(dpi, dpi)
    pix = page.get_pixmap(matrix=matrix)
    coefficient = max(pix.width, pix.height) / params.image_max_size

    if coefficient <= 1:
        return pix

    # Optimization gain en rapidité pour réduire la taille des images car
    # la conversion en numpyarray est très longue
    # plus longue que le temps de convertion de la page en 300 dpi
    dpi = dpi / coefficient
    matrix = fitz.Matrix(dpi, dpi)
    return page.get_pixmap(matrix=matrix)


def _get_pages(
    document: fitz.Document, params: PdfHandlerParams
) -> Iterable[tuple[PDFMetadataType, list[FileContent], bytes | None]]:
    max_size = params.text_size_min_before_fallback_to_extract_images
    pages_info = _get_metadata(document, params.normalize_text, max_size)

    for (page_metadata, page_content), page in zip(
        pages_info, document.pages(), strict=True
    ):
        if not params.always_extract_image and page_content:
            yield page_metadata, page_content, None
            continue

        pix = _get_pix(document, page, params=params)

        # Transform ?
        np_array = np.frombuffer(convert_pixmap_to_rgb(pix).tobytes(), np.uint8)
        image_cv = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        image_cv, resized_ratio = normalize_size(image_cv, params.image_max_size)
        height, width = image_cv.shape[:2]

        page_content.append(
            ImageContent(framework="opencv", content_type="image", image=image_cv)
        )
        metadata: PDFMetadataType = cast(
            PDFMetadataType,
            {
                "width": width,
                "height": height,
                "resized_ratio": resized_ratio,
                **page_metadata,
            },
        )
        yield metadata, page_content, cv2.imencode(".png", image_cv)[1].tobytes()


def _get_metadata(
    document: fitz.Document,
    normalize_text: bool = False,
    text_length_threshold: int | None = None,
) -> Iterable[tuple[PDFMetadataType, list[FileContent]]]:
    total_pages = len(document)

    for index in range(total_pages):
        page = document[index]
        text = page.get_textpage().extractText()
        text_content = TextContent(
            get_normalized_text(text) if normalize_text else text
        )
        metadata = cast(
            PDFMetadataType,
            {
                "page_number": page.number + 1,
                "total_pages": total_pages,
            },
        )

        if text_length_threshold is not None and len(text) <= text_length_threshold:
            yield metadata, []
        else:
            yield metadata, [text_content]
