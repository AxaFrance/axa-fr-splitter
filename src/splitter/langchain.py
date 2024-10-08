import tempfile
from pathlib import Path
from typing import Protocol
from collections.abc import Iterable, Callable

from langchain_core.documents import Document

from returns.result import Success

from splitter import IExtensionHandler
from splitter.file import File, FileOrError, TextContent


__all__ = ["LangchainAdapter"]


class LangchainLoader(Protocol):
    def load(self) -> list[Document]:
        ...


class LangchainAdapter(IExtensionHandler):
    def __init__(self, loader: Callable[[str], LangchainLoader]):
        self.loader = loader

    def to_files(self, file: File) -> Iterable[FileOrError]:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_file = Path(temp_dir).joinpath(Path(file.vpath).name)
            tmp_file.write_bytes(file.stream.read())
            file.stream.seek(0)

            vpath = Path(file.vpath)
            for idx, document in enumerate(
                self.loader(tmp_file.as_posix()).load(), start=1
            ):
                text = TextContent(document.page_content, source="metadata")

                file_name = vpath.parent / f"{vpath.stem}-{idx}{vpath.suffix}"

                yield Success(
                    File(
                        vpath=file_name.as_posix(),
                        stream=file.stream,
                        contents=[text],
                        metadata=document.metadata,
                    )
                )
