# @axa-fr/axa-fr-splitter

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

## How to consume
```sh
pip install axa-fr-splitter
```


```python
from splitter.file_handler import FileHandler
from splitter.image_handler import ImageHandler
from splitter.magic_mime_reader import MagicMimeReader
from splitter.pdf_handler import PdfHandlerParams, FitzPdfHandler
from splitter.tiff_handler import TifHandler

file_handler = FileHandler(MagicMimeReader())
image_handler = ImageHandler()
file_handler.register_converter(
    image_handler,
    [".png", ".jpg", ".jpeg", ".bmp"],
    ['image/png', 'image/jpeg', 'image/bmp']
)
pdf_handler = FitzPdfHandler(
        PdfHandlerParams(
            limit_number_page=3,
            is_always_extract_image=True,
            limit_number_page_when_image=3,
            is_try_to_extract_image_instead_of_dpi_extraction=False,
        )
    )
tiff_handler = TifHandler(limit_number_page=3)
file_handler.register_converter(tiff_handler,
                                ['.tif', '.tiff'],
                                ['image/tiff'])
file_handler.register_converter(pdf_handler,
                                ['.pdf'],
                                ['application/pdf'])
file_handler.register_converter(image_handler,
                                [".png", ".jpg", ".jpeg", ".bmp"],
                                ['image/png', 'image/jpeg', 'image/bmp'])


with open('.path.pdf', 'w') as stream:
    files = file_handler.split_document("filename", stream)

print(files)
```

## Contribute

- [How to run the solution and to contribute](./CONTRIBUTING.md)
- [Please respect our code of conduct](./CODE_OF_CONDUCT.md)