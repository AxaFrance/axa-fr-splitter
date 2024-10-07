from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, Protocol
from collections.abc import Iterable

from splitter.file import File, FileOrError


class IFileHandler(Protocol):
    def split_document(
        self,
        file_info: File | str | Path | BinaryIO | bytes,
        filename: str | None = None,
    ) -> Iterable[FileOrError]:
        ...

    def is_supported(
        self,
        file_info: File | str | Path | BinaryIO | bytes,
        filename: str | None = None,
    ) -> bool:
        ...


class IExtensionHandler(Protocol):
    def to_files(self, file: File) -> Iterable[FileOrError]:
        ...
