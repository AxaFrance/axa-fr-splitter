import time
import logging
from pathlib import Path

from splitter.file_handler import FileHandler

import unittest

from splitter.mime_reader import MimeReader
from splitter.pdf_handler import PdfHandlerParams
from splitter.pdf_handler import FitzPdfHandler

BASE_PATH = Path(__file__).parent / "inputs"


def run_test(self, file_path: str, file_handler: FileHandler, expected_results=None):
    start = time.time()

    with open(file_path, "rb") as file_stream:
        results = file_handler.split_document(
            Path(file_path).name, file_stream.read()
        )
        results = list(results)

    end = time.time()
    self.logger.debug("time: " + str(end - start))

    for index, result in enumerate(results):
        metadata = result.metadata
        self.assertEqual(metadata, expected_results[index]["metadata"])

    print("end")


class TestPDFConverters(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def test_extract_fitz_force_extract_images(self):
        file_handler = FileHandler(MimeReader())
        expected_results = [
            {
                "relative_path": 'specimen.pdf-1.png',
                "metadata": {
                    'width': 1555,
                    'height': 2200,
                    'resized_ratio': 1.0,
                    'page_number': 1,
                    'total_pages': 2,
                    'content': (
                        'AANND 571330\nAssurance\nRetraite\nAuvergne\nCARSAT AUVERGN'
                        'E\n63036 CLERMONTFERRAND CEDEX 9 988QN2163P90313 9031326'
                        '17001401748\nA rappeler dans tous vos courriers\nN de séc'
                        'urité sociale : . M. John Doe\n259 05 12 063 053 2 RUE D'
                        'ES FLEURS\n99000 D AUVERGNE\nTéléphone : 2060 service 0,0'
                        '6 /min  prix appel\nFax : 04.73.42.88.09\nWww. laseurance'
                        "retraite. fr\nNotification de retraite\nExtrait d'inscrip"
                        'tion au registre des refraîtes\nMonsieur, Le 12 mars 201'
                        '9\nAprès étude de votre dossier, nous vous informons que'
                        ' :\n5 à compter du 01 mai 2019 nous vous attribuons une '
                        'retraite personnelle.\nElle est calculée avec les élémen'
                        'ts suivants :\nrevenu de base en euro : 30 694,34\ntaux a'
                        "pplicable au calcul de votre retraite : 50\ndurée d'assu"
                        'rance  : 167maximum autorisé\npour les activités que vou'
                        's avez pu exercer en tant que salarié, salarié agricole'
                        ', artisan ou\ncommerçant.\nà compter du 01 mai 2019 nous '
                        'prélevons la contribution sociale généralisée part\nimpo'
                        'sable et\nnon imposable, la contribution de solidarité p'
                        "our l'autonomie et la contribution pour le\nremboursemen"
                        't\nde la dette sociale sur votre retraite en raison de v'
                        'otre situation fiscale.\nVoici le détail de vos mensuali'
                        'tés :\nELEMENTS DE LA RETRAITE\n01/05/2019\n1278,93\n'
                    ),
                    'original_filename': 'specimen.pdf',
                },
            },
            {
                "relative_path": 'specimen.pdf-2.png',
                "metadata": {
                    'width': 1555,
                    'height': 2200,
                    'resized_ratio': 1.0,
                    'page_number': 2,
                    'total_pages': 2,
                    'content': '',
                    'original_filename': 'specimen.pdf',
                },
            },
        ]
        file_handler.register_converter(
            FitzPdfHandler(params=PdfHandlerParams(is_always_extract_image=True)),
            [".pdf"],
        )
        file_path = BASE_PATH / "specimen.pdf"
        run_test(self, str(file_path), file_handler, expected_results)

    def test_extract_fitz(self):
        file_handler = FileHandler(MimeReader())
        expected_results = [
            {
                "relative_path": 'specimen.pdf-1.png',
                "metadata": {
                    'page_number': 1,
                    'total_pages': 2,
                    'content': (
                        'AANND 571330\nAssurance\nRetraite\nAuvergne\nCARSAT AUVERGN'
                        'E\n63036 CLERMONTFERRAND CEDEX 9 988QN2163P90313 9031326'
                        '17001401748\nA rappeler dans tous vos courriers\nN de séc'
                        'urité sociale : . M. John Doe\n259 05 12 063 053 2 RUE D'
                        'ES FLEURS\n99000 D AUVERGNE\nTéléphone : 2060 service 0,0'
                        '6 /min  prix appel\nFax : 04.73.42.88.09\nWww. laseurance'
                        "retraite. fr\nNotification de retraite\nExtrait d'inscrip"
                        'tion au registre des refraîtes\nMonsieur, Le 12 mars 201'
                        '9\nAprès étude de votre dossier, nous vous informons que'
                        ' :\n5 à compter du 01 mai 2019 nous vous attribuons une '
                        'retraite personnelle.\nElle est calculée avec les élémen'
                        'ts suivants :\nrevenu de base en euro : 30 694,34\ntaux a'
                        "pplicable au calcul de votre retraite : 50\ndurée d'assu"
                        'rance  : 167maximum autorisé\npour les activités que vou'
                        's avez pu exercer en tant que salarié, salarié agricole'
                        ', artisan ou\ncommerçant.\nà compter du 01 mai 2019 nous '
                        'prélevons la contribution sociale généralisée part\nimpo'
                        'sable et\nnon imposable, la contribution de solidarité p'
                        "our l'autonomie et la contribution pour le\nremboursemen"
                        't\nde la dette sociale sur votre retraite en raison de v'
                        'otre situation fiscale.\nVoici le détail de vos mensuali'
                        'tés :\nELEMENTS DE LA RETRAITE\n01/05/2019\n1278,93\n'
                    ),
                    'original_filename': 'specimen.pdf',
                },
            },
            {
                "relative_path": 'specimen.pdf-2.png',
                "metadata": {
                    'page_number': 2,
                    'total_pages': 2,
                    'content': '',
                    'original_filename': 'specimen.pdf',
                },
            },
        ]

        file_handler.register_converter(
            FitzPdfHandler(params=PdfHandlerParams()), [".pdf"]
        )
        file_path = BASE_PATH / "specimen.pdf"
        run_test(self, str(file_path), file_handler, expected_results)


if __name__ == "__main__":
    unittest.main()
