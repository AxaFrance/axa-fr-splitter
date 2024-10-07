from typing import BinaryIO

import mimetypes

from splitter.mime_reader.mime_reader_interface import IMimeReader


class MimeReader(IMimeReader):
    def get_mime_type(self, filepath: str, file_stream: BinaryIO) -> str:
        return (
            mimetypes.guess_type(filepath, strict=False)[0]
            or "application/octet-stream"
        )
