import time
import logging
import unittest
import base64
import cv2

from pathlib import Path
from unittest.mock import MagicMock
from axa_fr_splitter.eml_handler import EmlHandler
from axa_fr_splitter.file_handler import FileHandler
from axa_fr_splitter.image_handler import ImageHandler
from axa_fr_splitter.mime_reader import MimeReader

BASE_PATH = Path(__file__).parent / "inputs"


def run_test(self, eml_handler: EmlHandler, file_path: Path, expected_results):
    start = time.time()
    with Path(file_path).open("rb") as file_stream:
        results = eml_handler.to_files(str(file_path), file_stream)
        results = list(results)
    end = time.time()
    self.logger.debug("time: " + str(end - start))
    for index, expected_results in enumerate(expected_results):
        metadata = results[index].metadata
        self.assertEqual(metadata, expected_results["metadata"])


class TestEmlConverters(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def test_extract_image(self):
        file_handler = FileHandler(MimeReader())
        image_handler = ImageHandler()
        file_handler.register_converter(image_handler, [".png"])
        expected_results = [
            {
                "metadata": {
                    'total_pages': 1,
                    'original_filename': 'demo.eml',
                    'page_number': 1,
                    'width': 863,
                    'height': 443,
                    'resized_ratio': 1,
                    'subject': 'test',
                    'from': 'test',
                    'to': 'test',
                    'cc': 'test',
                    'attachment_filename': 'test.png',
                }
            }
        ]

        image_cv = cv2.imread(str(BASE_PATH / "specimen.png"), cv2.IMREAD_ANYCOLOR)
        png_as_text = base64.b64encode(cv2.imencode(".png", image_cv)[1].tobytes())

        def decode_email_bytes(file_stream):
            return {
                "body": [{"content_type": "text/plain", "content": "test"}],
                "attachment": [{"filename": "test.png", "raw": png_as_text}],
                "header": {
                    "subject": "test",
                    "from": "test",
                    "to": "test",
                    "cc": "test",
                },
            }

        eml_parser = MagicMock()
        eml_parser.decode_email_bytes = decode_email_bytes
        eml_handler = EmlHandler(file_handler, True, eml_parser)
        run_test(self, eml_handler, BASE_PATH / "demo.eml", expected_results)


if __name__ == "__main__":
    unittest.main()
