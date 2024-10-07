from typing import BinaryIO

from magic import Magic

from splitter.mime_reader.mime_reader_interface import IMimeReader


class MagicMimeReader(IMimeReader):
    def __init__(self) -> None:
        self.magic = Magic(mime=True)

    def get_mime_type(self, filepath: str, file_stream: BinaryIO) -> str:
        file_bytes = file_stream.read()
        file_stream.seek(0)
        return self.magic.from_buffer(file_bytes)
