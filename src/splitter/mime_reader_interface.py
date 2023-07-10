from typing import Protocol, IO


class IMimeReader(Protocol):
    def get_mime_type(self, filepath: str, file_stream: IO) -> str:
        raise NotImplementedError()
