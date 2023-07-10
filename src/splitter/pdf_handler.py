import re
from dataclasses import dataclass
from pathlib import Path
from typing import IO

import cv2
import fitz
import numpy as np
from fitz import Pixmap

from splitter.file import build_file
from splitter.errors import ConvertError
from splitter.extension_handler_interface import IExtensionHandler

from .image import normalize_size


def convert_pixmap_to_rgb(pixmap) -> Pixmap:
    """Convert to rgb in order to write on png"""
    # check if it is already on rgb
    if pixmap.n < 4:
        return pixmap
    else:
        return fitz.Pixmap(fitz.csRGB, pixmap)


def clean_text_for_redis(text):
    if len(text) == 0:
        return ""
    text_cleaned = re.sub(r"[^a-zA-Z \n\réèçàùô\'ëî,\./@0-9:]", "", text)
    text_cleaned = "\n".join([line.strip() for line in text_cleaned.splitlines()])
    text_cleaned = re.sub(r"\n\s*\n", "\n", text_cleaned, re.MULTILINE)
    if len(text_cleaned) > 0 and len(text) / len(text_cleaned) >= 1.5:
        return ""
    return text_cleaned


@dataclass
class PdfHandlerParams:
    is_always_extract_image: bool = False
    limit_number_page: int = 3
    limit_number_page_when_image: int = 2
    is_try_to_extract_image_instead_of_dpi_extraction: bool = True
    try_to_extract_threshold_min_image_size: int = 1400
    resize_image_size_max: int = 2200
    text_size_min_before_fallback_to_extract_images: int = 40
    default_dpi: int = 300


def _get_pix(document, page, params: PdfHandlerParams):
    if params.is_try_to_extract_image_instead_of_dpi_extraction:
        # Optimization gain rapidité, beaucoup de PDF contiennent 1 image (la page complete scannée)
        images = page.get_images()
        number_images = len(images)
        if number_images == 1:
            # On extrait les images de la page on met un seuil car certain
            # scanner et word découpe une unique image en plein de petite image
            xref = images[0][0]
            pix = fitz.Pixmap(document, xref)
            if (
                pix.width > params.try_to_extract_threshold_min_image_size
                and pix.height > params.try_to_extract_threshold_min_image_size
            ):
                return pix
            else:
                return None

    defaut_dpi = params.default_dpi
    dpi = defaut_dpi / 72
    matrix = fitz.Matrix(dpi, dpi)
    pix = page.get_pixmap(matrix=matrix)
    coefficient = max(pix.width, pix.height) / params.resize_image_size_max
    # Optimization gain en rapidité pour réduire la taille des images car la conversion en numpyarray est très longue
    # plus longue que le temps de convertion de la page en 300 dpi
    if coefficient > 1:
        dpi = defaut_dpi / (72 * coefficient)
        matrix = fitz.Matrix(dpi, dpi)
        pix = page.get_pixmap(matrix=matrix)
    return pix


def is_extract_image_required(metadatas, number_page: int, params: PdfHandlerParams):
    if params.is_always_extract_image:
        return True
    text = ""
    for metadata in metadatas:
        text += metadata["content"] + "\n"

    is_extract_image = (
        len(text)
        <= params.text_size_min_before_fallback_to_extract_images * number_page
    )
    return is_extract_image


def _get_pages(read_pdf, file_stream: IO, params: PdfHandlerParams):
    with read_pdf(file_stream) as document:
        total_pages = len(document)
        min_page = min(total_pages, params.limit_number_page)

        metadata_list = []
        for index in range(min_page):
            page = document[index]
            metadata = {
                "page_number": page.number + 1,
                "total_pages": total_pages,
                "content": clean_text_for_redis(page.get_textpage().extractText()),
            }
            metadata_list.append(metadata)

        if is_extract_image_required(metadata_list, min_page, params):
            min_page_when_image = min(min_page, params.limit_number_page_when_image)
            for index in range(min_page_when_image):
                page = document[index]
                pix = _get_pix(document, page, params=params)
                if pix is None:
                    yield metadata_list[index], None
                    continue
                np_array = np.frombuffer(convert_pixmap_to_rgb(pix).tobytes(), np.uint8)
                image_cv = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
                image_cv_resized, resized_ratio = normalize_size(
                    image_cv, params.resize_image_size_max
                )
                (height, width) = image_cv_resized.shape[:2]
                metadata = {
                    "width": width,
                    "height": height,
                    "resized_ratio": resized_ratio,
                    **metadata_list[index],
                }
                yield metadata, cv2.imencode(".png", image_cv_resized)[1].tobytes()
        else:
            for metadata in metadata_list:
                yield metadata, None


class ConvertPdfError(ConvertError):
    pass


class FitzPdfHandler(IExtensionHandler):
    _exception = ConvertPdfError

    def __init__(self, params: PdfHandlerParams):
        self.params = params

    def to_files(self, basename: str, file_stream: IO):
        pages = _get_pages(self._read_pdf, file_stream, self.params)
        for metadata, image_bytes in pages:
            page_number = metadata["page_number"]
            name = Path(basename).name
            filename = f"{name}-{page_number}.png"
            metadata["original_filename"] = name
            yield build_file(filename, file_bytes=image_bytes, metadata=metadata)

    @staticmethod
    def _read_pdf(file_stream: IO):
        return fitz.open(stream=file_stream, filetype="pdf")
