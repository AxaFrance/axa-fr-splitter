# @axa-fr/axa-fr-splitter
![PyPI](https://img.shields.io/pypi/v/axa-fr-splitter)
![PyPI - License](https://img.shields.io/pypi/l/axa-fr-splitter)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/axa-fr-splitter)

![Tests](https://github.com/AxaFrance/axa-fr-splitter/actions/workflows/tests.yml/badge.svg)
![python: 3.10 (shields.io)](https://img.shields.io/badge/python-3.10-green)
![python: 3.11 (shields.io)](https://img.shields.io/badge/python-3.11-green)
![python: 3.12 (shields.io)](https://img.shields.io/badge/python-3.12-green)

[//]: # ([![Continuous Integration]&#40;https://github.com/AxaFrance/axa-fr-splitter/actions/workflows/python-publish.yml/badge.svg&#41;]&#40;https://github.com/AxaFrance/axa-fr-splitter/actions/workflows/python-publish.yml&#41;)

[//]: # ([![Quality Gate]&#40;https://sonarcloud.io/api/project_badges/measure?project=<INSERT SONAR SPLITTER PROJECT>&metric=alert_status&#41;]&#40;https://sonarcloud.io/dashboard?id=<INSERT SONAR SPLITTER PROJECT>&#41;)

[//]: # ([![Reliability]&#40;https://sonarcloud.io/api/project_badges/measure?project=<INSERT SONAR SPLITTER PROJECT>&metric=reliability_rating&#41;]&#40;https://sonarcloud.io/component_measures?id=<INSERT SONAR SPLITTER PROJECT>&metric=reliability_rating&#41;)

[//]: # ([![Security]&#40;https://sonarcloud.io/api/project_badges/measure?project=<INSERT SONAR SPLITTER PROJECT>&metric=security_rating&#41;]&#40;https://sonarcloud.io/component_measures?id=A<INSERT SONAR SPLITTER PROJECT>&metric=security_rating&#41;)

[//]: # ([![Code Coverage]&#40;https://sonarcloud.io/api/project_badges/measure?project=<INSERT SONAR SPLITTER PROJECT>&metric=coverage&#41;]&#40;https://sonarcloud.io/component_measures?id=<INSERT SONAR SPLITTER PROJECT>&metric=Coverage&#41;)

[//]: # ([![Twitter]&#40;https://img.shields.io/twitter/follow/GuildDEvOpen?style=social&#41;]&#40;https://twitter.com/intent/follow?screen_name=GuildDEvOpen&#41;)

- [About](#about)
- [How to consume](#how-to-consume)
- [Contribute](#contribute)

## About
The axa-fr-splitter package aims at providing tools to process several types of documents (pdf, tiff, ...) into images using Python.

## Quick Start
```sh
pip install axa-fr-splitter
```


```python
from pathlib import Path
from splitter import FileHandler
from splitter.image.tiff_handler import TifHandler
from splitter.pdf.pdf_handler import FitzPdfHandler


def create_file_handler() -> FileHandler:
    """Factory to create customized file handler"""

    # Create File Handler
    file_handler = FileHandler()

    # Create pdf Handler
    pdf_handler = FitzPdfHandler()

    # Create tiff Handler
    tiff_handler = TifHandler()

    # Register PDF Handler
    file_handler.register_converter(
        pdf_handler,
        extensions=['.pdf'],
        mime_types=['application/pdf']
    )

    # Register tiff Handler
    file_handler.register_converter(
        tiff_handler,
        extensions=['.tif', '.tiff'],
        mime_types=['image/tiff']
    )

    return file_handler


def main(filepath, output_path):
    file_handler = create_file_handler()
    output_path = Path(output_path)

    for file_or_exception in file_handler.split_document(filepath):
        file = file_or_exception.unwrap()

        print(file.metadata)
        # {
        #     'original_filename': 'specimen.tiff',
        #     'page_number': 1,
        #     'total_pages': 4,
        #     'width': 1554,
        #     'height': 2200,
        #     'resized_ratio': 0.9405728943993159
        # }

        # Export File file bytes:
        export_path = output_path.joinpath(file.relative_path)
        export_path.write_bytes(file.file_bytes)

if __name__ == '__main__':
    main(r"tests/inputs/specimen.tiff", MY_OUTPUT_PATH)
```

You can use the `match` statement to handle the exceptions in a different way:

``` python
from returns.result import Failure, Success

...

def main(filepath, output_path):
    file_handler = create_file_handler()
    output_path = Path(output_path)

    for file_or_exception in file_handler.split_document(filepath):
        match file_or_exception:
            case Success(file):
                print(file.metadata)
                export_path = output_path.joinpath(file.relative_path)
                export_path.write_bytes(file.file_bytes)
            case Failure(exception):
                # Handle Exception ...
                raise exception

```

## Contribute

- [How to run the solution and to contribute](./.github/CONTRIBUTING.md)
- [Please respect our code of conduct](./.github/CODE_OF_CONDUCT.md)
