from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO, cast
from collections.abc import Iterable, Container

from returns.result import Failure, Success, safe

from splitter.interfaces import IExtensionHandler, IFileHandler
from splitter.mime_reader import IMimeReader, MimeReader
from splitter.file import File, FileOrError, MetadataType

__all__ = ["FileHandler", "UnsupportedFormatError", "to_handler"]


class UnsupportedFormatError(Exception):
    pass


class FileHandler(IFileHandler):
    def __init__(
        self,
        mime_reader: IMimeReader | None = None,
        target_extensions: Iterable[str] | None = None,
        target_mime_types: Iterable[str] | None = None,
    ) -> None:
        self._target_extensions = set(target_extensions or {})
        self._target_mime_types = set(target_mime_types or {})
        self._mime_reader = mime_reader or MimeReader()
        self._converters: dict[str, IExtensionHandler] = {}
        self._mime_converters: dict[str, IExtensionHandler] = {}

    @property
    def supported_extensions(self) -> set[str]:
        return self._target_extensions | set(self._converters)

    @property
    def supported_mime_types(self) -> set[str]:
        return self._target_mime_types | set(self._mime_converters)

    def split_document(
        self,
        file_info: File | str | Path | BinaryIO | bytes,
        filename: str | None = None,
    ) -> Iterable[FileOrError]:
        file_or_error = _get_file(file_info, filename)

        if isinstance(file_or_error, Failure):
            return (file_or_error,)

        file = file_or_error.unwrap()

        if not self.is_supported(file):
            extension = get_file_extension(file.vpath)
            mime_type = self._mime_reader.get_mime_type(file.vpath, file.stream)
            exception = UnsupportedFormatError(
                f"Unknown File extension: {extension} / mime type: {mime_type}"
            )
            return (Failure(exception),)

        return self.__convert(file)

    def is_supported(
        self,
        file_info: File | str | Path | BinaryIO | bytes,
        filename: str | None = None,
    ) -> bool:
        file = _get_file(file_info, filename).unwrap()

        return _check_filename(
            self.supported_extensions, file.vpath
        ) or _check_mime_type(
            self._mime_reader, self.supported_mime_types, file.vpath, file.stream
        )

    def register_converter(
        self,
        handler: IExtensionHandler,
        extensions: Iterable[str] | None = None,
        mime_types: Iterable[str] | None = None,
    ) -> None:
        for extension in extensions or ():
            self._converters[extension] = handler

        for mime_type in mime_types or ():
            self._mime_converters[mime_type] = handler

    def __get_converter(
        self, path: str, file_stream: BinaryIO
    ) -> IExtensionHandler | None:
        extension = get_file_extension(path)
        if extension in self._converters:
            return self._converters[extension]

        mime_type = self._mime_reader.get_mime_type(path, file_stream)
        return self._mime_converters.get(mime_type, None)

    def __convert(
        self,
        file: File,
    ) -> Iterable[FileOrError]:
        converter = self.__get_converter(file.vpath, file.stream)
        if converter:
            return converter.to_files(file)

        metadata = file.metadata or {}
        return (
            Success(
                File(
                    file.vpath,
                    stream=file.stream,
                    contents=file.contents,
                    metadata=cast(
                        MetadataType,
                        {
                            **metadata,
                            "original_filename": Path(file.vpath).name,
                            "total_pages": 1,
                        },
                    ),
                )
            ),
        )


def to_handler(
    extension_handler: IExtensionHandler,
    mime_reader: IMimeReader | None = None,
    extensions: Iterable[str] | None = None,
    mime_types: Iterable[str] | None = None,
) -> FileHandler:
    handler = FileHandler(mime_reader=mime_reader)
    handler.register_converter(extension_handler, extensions, mime_types)

    return handler


def get_file_extension(filename: str | Path) -> str:
    return Path(filename).suffix.lower()


def _check_filename(supported_extensions: Container[str], filename: str) -> bool:
    return get_file_extension(filename) in supported_extensions


def _check_mime_type(
    mime_reader: IMimeReader,
    supported_mime_types: Container[str],
    filepath: str,
    file_stream: BinaryIO,
) -> bool:
    return mime_reader.get_mime_type(filepath, file_stream) in supported_mime_types


@safe
def _get_file(
    file_info: File | str | Path | BinaryIO | bytes, filename: str | None = None
) -> File:
    if isinstance(file_info, File):
        return file_info

    if isinstance(file_info, Path):
        file_info = str(file_info)

    vpath = file_info if isinstance(file_info, str) else filename
    if isinstance(file_info, str):
        file_info = Path(file_info).read_bytes()

    if vpath is None:
        raise ValueError("Filename must be provided if file_info is not a File object")

    file_stream = io.BytesIO(file_info) if isinstance(file_info, bytes) else file_info
    return File(vpath=vpath, stream=file_stream)
