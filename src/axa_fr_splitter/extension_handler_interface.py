from typing import Iterable, Protocol, IO

from axa_fr_splitter.file import File


class IExtensionHandler(Protocol):
    def to_files(self, filename: str, file_stream: IO) -> Iterable[File]:
        raise NotImplementedError()
