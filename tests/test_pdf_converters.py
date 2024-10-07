from __future__ import annotations

import logging
import time
import unittest
from pathlib import Path
from typing import TypedDict

from splitter import File
from splitter.file import TextContent
from splitter.file_handler import FileHandler
from splitter.mime_reader.mime_reader import MimeReader
from splitter.pdf.pdf_handler import FitzPdfHandler, PdfHandlerParams

BASE_PATH = Path(__file__).parent / "inputs"


class ExpectedType(TypedDict):
    metadata: dict[str, str | int | float]
    relative_path: str
    contents: list[str]


def run_test(
    self: TestPDFConverters,
    file_path: str,
    file_handler: FileHandler,
    expected_results: list[ExpectedType],
) -> None:
    start = time.time()

    results = file_handler.split_document(file_path)
    file_results: list[File] = [result.unwrap() for result in results]

    end = time.time()
    self.logger.debug("time: " + str(end - start))

    self.assertEqual(len(expected_results), len(file_results))

    for result, expected in zip(file_results, expected_results):
        self.assertEqual(expected["metadata"], result.metadata)
        self.assertEqual(len(expected["contents"]), len(result.text_contents))
        for content, expected_content in zip(result.text_contents, expected["contents"]):
            self.assertTrue(isinstance(content, TextContent))
            self.assertEqual(expected_content, content.text)

    print("end")


class TestPDFConverters(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxDiff = None

    def test_extract_fitz_force_extract_images(self) -> None:
        file_name = "specimen"
        file_handler = FileHandler(MimeReader())
        expected_results: list[ExpectedType] = [
            {
                "relative_path": f"{file_name}.pdf-1.png",
                "contents": [
                    'AANND 571330\nAssurance\nRetraite\nAuvergne\nCARSAT AUV'
                    'ERGNE\n63036 CLERMONT-FERRAND CEDEX 9 988QN2163P-903'
                    '13- 903132617-0014-01748\nA rappeler dans tous vos c'
                    'ourriers\nN° de sécurité sociale : . M. John Doe\n259'
                    ' 05 12 063 053 2 RUE DES FLEURS\n99000 D AUVERGNE\nTé'
                    'léphone : 2060 (service 0,06 €/min + prix appel)\nFa'
                    'x : 04.73.42.88.09\nWww. laseuranceretraite. fr\nNoti'
                    'fication de retraite\n"Extrait d\'inscription au regi'
                    'stre des refraîtes”\nMonsieur, Le 12 mars 2019\nAprès'
                    ' étude de votre dossier, nous vous informons que :\n'
                    '5 à compter du 01 mai 2019 nous vous attribuons une'
                    ' retraite personnelle.\nElle est calculée avec les é'
                    'léments suivants :\nrevenu de base (en euro) : 30 69'
                    '4,34\ntaux applicable au calcul de votre retraite : '
                    "50 %\ndurée d'assurance -{*) : 167-{maximum autorisé"
                    ')\n(”) pour les activités que vous avez pu exercer e'
                    'n tant que salarié, salarié agricole, artisan ou\nco'
                    'mmerçant.\nà compter du 01 mai 2019 nous prélevons l'
                    'a contribution sociale généralisée (part \nimposable'
                    ' et\nnon imposable), la contribution de solidarité p'
                    "our l'autonomie et la contribution pour le \nrembour"
                    'sement\nde la dette sociale sur votre retraite en ra'
                    'ison de votre situation fiscale.\nVoici le détail de'
                    ' vos mensualités :\nELEMENTS DE LA RETRAITE |\n[01/05'
                    '/2019]\n1278,93\n \n \n \n \n \n \n'
                ],
                "metadata": {
                    "width": 1555,
                    "height": 2200,
                    "resized_ratio": 1.0,
                    "page_number": 1,
                    "total_pages": 2,
                    "original_filename": f"{file_name}.pdf",
                },
            },
            {
                "relative_path": "specimen.pdf-2.png",
                "contents": [],
                "metadata": {
                    "width": 1555,
                    "height": 2200,
                    "resized_ratio": 1.0,
                    "page_number": 2,
                    "total_pages": 2,
                    "original_filename": f"{file_name}.pdf",
                },
            },
        ]
        params = PdfHandlerParams(always_extract_image=True)
        file_handler.register_converter(
            FitzPdfHandler(params=params),
            [".pdf"],
        )
        file_path = BASE_PATH / f"{file_name}.pdf"
        run_test(self, str(file_path), file_handler, expected_results)

    def test_extract_fitz(self) -> None:
        file_name = "specimen"
        file_handler = FileHandler(MimeReader())
        expected_results: list[ExpectedType] = [
            {
                "relative_path": f"{file_name}.pdf-1.png",
                "contents": [
                    'AANND 571330\nAssurance\nRetraite\nAuvergne\nCARSAT AUV'
                    'ERGNE\n63036 CLERMONT-FERRAND CEDEX 9 988QN2163P-903'
                    '13- 903132617-0014-01748\nA rappeler dans tous vos c'
                    'ourriers\nN° de sécurité sociale : . M. John Doe\n259'
                    ' 05 12 063 053 2 RUE DES FLEURS\n99000 D AUVERGNE\nTé'
                    'léphone : 2060 (service 0,06 €/min + prix appel)\nFa'
                    'x : 04.73.42.88.09\nWww. laseuranceretraite. fr\nNoti'
                    'fication de retraite\n"Extrait d\'inscription au regi'
                    'stre des refraîtes”\nMonsieur, Le 12 mars 2019\nAprès'
                    ' étude de votre dossier, nous vous informons que :\n'
                    '5 à compter du 01 mai 2019 nous vous attribuons une'
                    ' retraite personnelle.\nElle est calculée avec les é'
                    'léments suivants :\nrevenu de base (en euro) : 30 69'
                    '4,34\ntaux applicable au calcul de votre retraite : '
                    "50 %\ndurée d'assurance -{*) : 167-{maximum autorisé"
                    ')\n(”) pour les activités que vous avez pu exercer e'
                    'n tant que salarié, salarié agricole, artisan ou\nco'
                    'mmerçant.\nà compter du 01 mai 2019 nous prélevons l'
                    'a contribution sociale généralisée (part \nimposable'
                    ' et\nnon imposable), la contribution de solidarité p'
                    "our l'autonomie et la contribution pour le \nrembour"
                    'sement\nde la dette sociale sur votre retraite en ra'
                    'ison de votre situation fiscale.\nVoici le détail de'
                    ' vos mensualités :\nELEMENTS DE LA RETRAITE |\n[01/05'
                    '/2019]\n1278,93\n \n \n \n \n \n \n'
                ],
                "metadata": {
                    "page_number": 1,
                    "total_pages": 2,
                    "original_filename": f"{file_name}.pdf",
                },
            },
            {
                "relative_path": f"{file_name}.pdf-2.png",
                "contents": [],
                "metadata": {
                    "height": 2200,
                    "original_filename": f"{file_name}.pdf",
                    "page_number": 2,
                    "resized_ratio": 1.0,
                    "total_pages": 2,
                    "width": 1555,
                },
            },
        ]

        file_handler.register_converter(
            FitzPdfHandler(params=PdfHandlerParams(always_extract_image=False)),
            [".pdf"],
        )
        file_path = BASE_PATH / f"{file_name}.pdf"
        run_test(self, str(file_path), file_handler, expected_results)

    def test_scanned_pdf(self) -> None:
        file_name = "scanned_specimen"
        expected_results: list[ExpectedType] = [
            {
                "relative_path": f"{file_name}.pdf-1.png",
                "contents": [],
                "metadata": {
                    "page_number": 1,
                    "total_pages": 1,
                    "original_filename": f"{file_name}.pdf",
                    "width": 1556,
                    "height": 2200,
                    "resized_ratio": 1.0,
                },
            },
        ]
        file_handler = FileHandler(MimeReader())

        file_handler.register_converter(
            FitzPdfHandler(params=PdfHandlerParams(always_extract_image=False)),
            [".pdf"],
        )
        file_path = BASE_PATH / f"{file_name}.pdf"
        run_test(self, str(file_path), file_handler, expected_results)


if __name__ == "__main__":
    unittest.main()
