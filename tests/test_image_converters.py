from __future__ import annotations
import logging
import time
import unittest
from pathlib import Path
from typing import TypedDict

from splitter.file_handler import FileHandler
from splitter.image.image_handler import ImageHandler
from splitter.mime_reader.mime_reader import MimeReader

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

    for result, expected in zip(file_results, expected_results):
        self.assertEqual(result.metadata, expected["metadata"])


class TestTIFConverters(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def test_extract_image(self) -> None:
        file_handler = FileHandler(MimeReader())
        image_handler = ImageHandler()
        file_handler.register_converter(image_handler, [".png"])
        expected_results: list[ExpectedType] = [
            {
                "metadata": {
                    "total_pages": 1,
                    "original_filename": "specimen.png",
                    "page_number": 1,
                    "width": 863,
                    "height": 443,
                    "resized_ratio": 1,
                },
                "relative_path": "specimen.png",
            },
        ]
        run_test(self, file_handler, BASE_PATH / "specimen.png", expected_results)


if __name__ == "__main__":
    unittest.main()
