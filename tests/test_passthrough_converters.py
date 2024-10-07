from __future__ import annotations
import logging
import time
import unittest
from pathlib import Path
from typing import TypedDict

from splitter.file_handler import FileHandler

BASE_PATH = Path(__file__).parent / "inputs"


class ExpectedType(TypedDict):
    metadata: dict[str, str | int | float]
    relative_path: str


def run_test(
    self: TestPassthroughConverters,
    file_handler: FileHandler,
    file_path: Path,
    expected_results: list[ExpectedType],
) -> None:
    start = time.time()
    results = file_handler.split_document(str(file_path))
    file_results = [result.unwrap() for result in results]

    end = time.time()
    self.logger.debug("time: " + str(end - start))

    self.assertEqual(len(file_results), len(expected_results))
    for index, result in enumerate(file_results):
        metadata = result.metadata
        self.assertEqual(metadata, expected_results[index]["metadata"])


class TestPassthroughConverters(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def test_extract_image(self) -> None:
        file_handler = FileHandler(target_extensions=[".png"])
        expected_results: list[ExpectedType] = [
            {
                "metadata": {"original_filename": "specimen.png", "total_pages": 1},
                "relative_path": "specimen.png",
            }
        ]
        run_test(self, file_handler, BASE_PATH / "specimen.png", expected_results)


if __name__ == "__main__":
    unittest.main()
