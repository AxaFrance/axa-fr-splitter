import time
import logging
from pathlib import Path

from splitter.file_handler import FileHandler

import unittest

from splitter.mime_reader import MimeReader
from splitter.tiff_handler import TifHandler

BASE_PATH = Path(__file__).parent / "inputs"


def run_test(self, file_handler: FileHandler, file_path: Path, expected_results):
    start = time.time()
    with Path(file_path).open("rb") as file_stream:
        results = file_handler.split_document(str(file_path), file_stream)
        results = list(results)
    end = time.time()
    self.logger.debug("time: " + str(end - start))
    for index, expected_result in enumerate(expected_results):
        metadata = results[index].metadata
        self.assertEqual(metadata, expected_result["metadata"])


class TestTIFConverters(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def test_extract_fitz(self):
        file_handler = FileHandler(MimeReader())
        tiff_handler = TifHandler()
        file_handler.register_converter(tiff_handler, [".tiff", ".tif"])
        expected_results = [
            {
                "metadata": {
                    'original_filename': 'specimen.tiff',
                    'page_number': 1,
                    'total_pages': 4,
                    'width': 1554,
                    'height': 2200,
                    'resized_ratio': 0.9405728943993159,
                },
                "relative_path": 'specimen.tiff-0.png',
            },
            {
                "metadata": {
                    'original_filename': 'specimen.tiff',
                    'page_number': 2,
                    'total_pages': 4,
                    'width': 1554,
                    'height': 2200,
                    'resized_ratio': 0.9405728943993159,
                },
                "relative_path": 'specimen.tiff-1.png',
            },
        ]
        run_test(self, file_handler, BASE_PATH / "specimen.tiff", expected_results)

    def test_extract_tiff(self):
        file_handler = FileHandler(MimeReader(self.logger))
        tiff_handler = TifHandler(limit_number_page=1)
        file_handler.register_converter(tiff_handler, [".tif", ".tiff"])
        expected_results = [
            {
                "metadata": {
                    'original_filename': 'specimen.tiff',
                    'page_number': 1,
                    'total_pages': 4,
                    'width': 1554,
                    'height': 2200,
                    'resized_ratio': 0.9405728943993159,
                },
                "relative_path": 'specimen.tiff-0.png',
            },
        ]
        run_test(self, file_handler, BASE_PATH / "specimen.tiff", expected_results)


if __name__ == "__main__":
    unittest.main()
