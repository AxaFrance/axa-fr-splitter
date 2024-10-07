from __future__ import annotations

import logging
import time
import unittest
from pathlib import Path
from typing import TypedDict

from splitter.file_handler import FileHandler
from splitter.mime_reader.mime_reader import MimeReader
from splitter.image.tiff_handler import TifHandler


BASE_PATH = Path(__file__).parent / "inputs"


class ExpectedType(TypedDict):
    metadata: dict[str, str | int | float]
    relative_path: str


def run_test(
    self: TestTIFConverters,
    file_handler: FileHandler,
    file_path: Path,
    expected_results: list[ExpectedType],
) -> None:
    start = time.time()
    results = file_handler.split_document(file_path)
    file_results = [result.unwrap() for result in results]

    end = time.time()
    self.logger.debug("time: " + str(end - start))

    self.assertEqual(len(file_results), len(expected_results))

    for index, expected_result in enumerate(expected_results):
        metadata = file_results[index].metadata
        self.assertEqual(metadata, expected_result["metadata"])


class TestTIFConverters(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def test_extract_fitz(self) -> None:
        file_handler = FileHandler(MimeReader())
        tiff_handler = TifHandler(max_pages=2, max_size=2200)
        file_handler.register_converter(tiff_handler, [".tiff", ".tif"])
        expected_results: list[ExpectedType] = [
            {
                "metadata": {
                    "original_filename": "specimen.tiff",
                    "page_number": 1,
                    "total_pages": 4,
                    "width": 1554,
                    "height": 2200,
                    "resized_ratio": 0.9405728943993159,
                },
                "relative_path": "specimen.tiff-0.png",
            },
            {
                "metadata": {
                    "original_filename": "specimen.tiff",
                    "page_number": 2,
                    "total_pages": 4,
                    "width": 1554,
                    "height": 2200,
                    "resized_ratio": 0.9405728943993159,
                },
                "relative_path": "specimen.tiff-1.png",
            },
        ]
        run_test(self, file_handler, BASE_PATH / "specimen.tiff", expected_results)

    def test_extract_tiff(self) -> None:
        file_handler = FileHandler(MimeReader())
        tiff_handler = TifHandler(max_pages=1, max_size=2200)
        file_handler.register_converter(tiff_handler, [".tif", ".tiff"])
        expected_results: list[ExpectedType] = [
            {
                "metadata": {
                    "original_filename": "specimen.tiff",
                    "page_number": 1,
                    "total_pages": 4,
                    "width": 1554,
                    "height": 2200,
                    "resized_ratio": 0.9405728943993159,
                },
                "relative_path": "specimen.tiff-0.png",
            },
        ]
        run_test(self, file_handler, BASE_PATH / "specimen.tiff", expected_results)


if __name__ == "__main__":
    unittest.main()
