import time
import logging
from pathlib import Path

from splitter.file_handler import FileHandler

import unittest

from splitter.image_handler import ImageHandler
from splitter.mime_reader import MimeReader

BASE_PATH = Path(__file__).parent / "inputs"


def run_test(self, file_handler: FileHandler, file_path: Path, expected_results):
    start = time.time()
    with Path(file_path).open("rb") as file_stream:
        results = file_handler.split_document(str(file_path), file_stream)
        results = list(results)
    end = time.time()
    self.logger.debug("time: " + str(end - start))
    for index, result in enumerate(results):
        metadata = result.metadata
        self.assertEqual(metadata, expected_results[index]["metadata"])


class TestTIFConverters(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def test_extract_image(self):
        file_handler = FileHandler(MimeReader())
        image_handler = ImageHandler()
        file_handler.register_converter(image_handler, [".png"])
        expected_results = [
            {
                "metadata": {
                    'total_pages': 1,
                    'original_filename': 'specimen.png',
                    'page_number': 1,
                    'width': 863,
                    'height': 443,
                    'resized_ratio': 1,
                },
                "relative_path": 'specimen.png',
            },
        ]
        run_test(self, file_handler, BASE_PATH / "specimen.png", expected_results)


if __name__ == "__main__":
    unittest.main()
