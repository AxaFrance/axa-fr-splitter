from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, IO

from splitter import IExtensionHandler
from splitter.mime_reader_interface import IMimeReader
from splitter.file import File, build_file


class UnsupportedFormat(Exception):
    pass


class FileHandler:
    def __init__(
        self,
        mime_reader: IMimeReader,
        target_extensions: Optional[set[str]] = None,
        target_mime_types: Optional[set[str]] = None,
    ):
        self._target_extensions = set(target_extensions or {})
        self._target_mime_types = set(target_mime_types or {})
        self._mime_reader = mime_reader
        self._converters = {}
        self._mime_converters = {}

    @property
    def supported_extensions(self) -> set[str]:
        return self._target_extensions | set(self._converters.keys())

    @property
    def supported_mime_types(self) -> set[str]:
        return self._target_mime_types | set(self._mime_converters.keys())

    def split_document(self, filepath: str, file_stream: IO) -> Iterable[File]:
        if not self.is_supported(filepath, file_stream):
            extension = get_file_extension(filepath)
            mime_type = self._mime_reader.get_mime_type(filepath, file_stream)
            raise UnsupportedFormat(
                f"Unknown File extension: {extension} / mime type: {mime_type}"
            )

        files = self.__convert(filepath, file_stream)
        return (file for file in files if file is not None)

    def is_supported(self, path, file_stream: IO) -> bool:
        return _check_filename(self.supported_extensions, path) or _check_mime_type(
            self._mime_reader, self.supported_mime_types, path, file_stream
        )

    def register_converter(
        self,
        handler: IExtensionHandler,
        extensions: Iterable[str] = None,
        mime_types: Iterable[str] = None,
    ):
        for extension in extensions or ():
            self._converters[extension] = handler

        for mime_type in mime_types or ():
            self._mime_converters[mime_type] = handler

    def __get_converter(
        self, path: str, file_stream: IO
    ) -> Optional[IExtensionHandler]:
        extension = get_file_extension(path)
        converter = self._converters.get(extension, None)

        if converter is None:
            mime_type = self._mime_reader.get_mime_type(path, file_stream)
            converter = self._mime_converters.get(mime_type, None)

        return converter

    def __convert(
        self,
        filename: str,
        file_stream: IO,
    ) -> Iterable[File]:
        converter = self.__get_converter(filename, file_stream)
        if converter:
            return converter.to_files(filename, file_stream)

        return (
            build_file(
                filename,
                file_stream,
                metadata={
                    "original_filename": Path(filename).name,
                    "total_pages": 1,
                },
            ),
        )


def get_file_extension(filename):
    return Path(filename).suffix.lower()


def _check_filename(supported_extensions, filename: str) -> bool:
    return get_file_extension(filename) in supported_extensions


def _check_mime_type(
    mime_reader: IMimeReader, supported_mime_types, filepath, file_stream: IO
) -> bool:
    return mime_reader.get_mime_type(filepath, file_stream) in supported_mime_types
