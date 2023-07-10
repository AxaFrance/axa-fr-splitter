from typing import IO

from magic import Magic

from splitter.mime_reader_interface import IMimeReader


class MagicMimeReader(IMimeReader):
    def __init__(self):
        self.magic = Magic(mime=True)

    def get_mime_type(self, filepath: str, file_stream: IO) -> str:
        return self.magic.from_buffer(file_stream.read())
