from typing import BinaryIO, Protocol


class IMimeReader(Protocol):
    def get_mime_type(self, filepath: str, file_stream: BinaryIO) -> str:
        ...
