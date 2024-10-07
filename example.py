from pathlib import Path
from pprint import pprint

from splitter import FileHandler
from splitter.image.tiff_handler import TifHandler
from splitter.pdf.pdf_handler import FitzPdfHandler

from returns.result import Failure, Success


def create_file_handler() -> FileHandler:
    """Create customized file handler."""

    # Create File Handler
    file_handler = FileHandler()

    # Create pdf Handler
    pdf_handler = FitzPdfHandler()

    # Create tiff Handler
    tiff_handler = TifHandler()

    # Register PDF Handler
    file_handler.register_converter(
        pdf_handler, extensions=[".pdf"], mime_types=["application/pdf"]
    )

    # Register tiff Handler
    file_handler.register_converter(
        tiff_handler, extensions=[".tif", ".tiff"], mime_types=["image/tiff"]
    )

    return file_handler


def main(filepath: str, output: str) -> None:
    file_handler = create_file_handler()
    output_path = Path(output)

    metadata_list = []

    for file_or_exception in file_handler.split_document(filepath):
        # Python >= 3.10 Syntax:
        match file_or_exception:
            case Success(file):
                metadata_list.append(file.metadata)
                export_path = output_path.joinpath(file.relative_path)
                export_path.write_bytes(file.file_bytes)
            case Failure(exception):
                print(exception)
                continue

        # Alternatively:
        try:
            file = file_or_exception.unwrap()
        except Exception as e:  # noqa BLE001
            # Handle Exception here
            print(e)
            continue

        metadata_list.append(file.metadata)
        if file.file_bytes is None:
            continue

        export_path = output_path.joinpath(file.relative_path)
        export_path.write_bytes(file.file_bytes)

    pprint(metadata_list)


if __name__ == "__main__":
    Path("out").mkdir(exist_ok=True)
    main(r"tests/inputs/specimen.pdf", "out")
