from __future__ import annotations

import logging
import time
import unittest
from pathlib import Path
from typing import TypedDict

from langchain_community.document_loaders import PDFMinerLoader

from splitter import File
from splitter.file import TextContent
from splitter.file_handler import FileHandler
from splitter.mime_reader.mime_reader import MimeReader
from splitter.langchain import LangchainAdapter


BASE_PATH = Path(__file__).parent / "inputs"


class ExpectedType(TypedDict):
    page: int
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
        self.assertEqual(expected["page"], result.metadata["page"])
        self.assertEqual(len(expected["contents"]), len(result.text_contents))
        for content, expected_content in zip(result.text_contents, expected["contents"]):
            self.assertTrue(isinstance(content, TextContent))
            self.assertEqual(expected_content, content.text.strip())

    print("end")


class TestPDFConverters(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxDiff = None

    def test_langchain_adapter(self) -> None:
        file_name = "specimen"
        file_handler = FileHandler(MimeReader())
        expected_results: list[ExpectedType] = [
            {
                "relative_path": f"{file_name}-1.pdf",
                "page": '0',
                "contents": [
                    "AANND 571330\n\nAssurance \n\nRetraite\n\nAuvergne\n\nCARSAT AUVERGNE"
                    " \n\n63036 CLERMONT-FERRAND CEDEX 9 988QN2163P-90313- 903132617-0014-0"
                    "1748\n\nA rappeler dans tous vos courriers \n\nN° de sécurité sociale "
                    ": . M. John Doe \n\n259 05 12 063 053 2 RUE DES FLEURS \n\n99000 D AUV"
                    "ERGNE\n\nTéléphone : 2060 (service 0,06 €/min + prix appel) \n\nFax : "
                    "04.73.42.88.09 \n\nWww. laseuranceretraite. fr\n\nNotification de retr"
                    "aite \n\n\"Extrait d'inscription au registre des refraîtes”\n\nMonsieu"
                    "r, Le 12 mars 2019\n\nAprès étude de votre dossier, nous vous informon"
                    "s que : \n\n5 à compter du 01 mai 2019 nous vous attribuons une retrai"
                    "te personnelle. \n\nElle est calculée avec les éléments suivants :\n\n"
                    "revenu de base (en euro) : 30 694,34\n\ntaux applicable au calcul de v"
                    "otre retraite : 50 %\n\ndurée d\'assurance -{*) : 167-{maximum autoris"
                    "é)\n\n(”) pour les activités que vous avez pu exercer en tant que sala"
                    "rié, salarié agricole, artisan ou \n\ncommerçant.\n\nà compter du 01 m"
                    "ai 2019 nous prélevons la contribution sociale généralisée (part \n\ni"
                    "mposable et \n\nnon imposable), la contribution de solidarité pour l\'"
                    "autonomie et la contribution pour le \n\nremboursement \n\nde la dette"
                    " sociale sur votre retraite en raison de votre situation fiscale.\n\nV"
                    "oici le détail de vos mensualités : \n\nELEMENTS DE LA RETRAITE |\n\n["
                    "01/05/2019]\n\n1278,93"
                ],
            },
            {
            "relative_path": f"{file_name}-2.pdf",
            "contents": [""],
            "page": '1',
        }
        ]
        pdf_handler = LangchainAdapter(
            lambda filepath: PDFMinerLoader(
                filepath,
                extract_images=False,
                concatenate_pages=False
            )
        )

        file_handler.register_converter(pdf_handler,[".pdf"])
        file_path = BASE_PATH / f"{file_name}.pdf"
        run_test(self, str(file_path), file_handler, expected_results)


if __name__ == "__main__":
    unittest.main()
