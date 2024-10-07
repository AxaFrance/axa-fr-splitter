from __future__ import annotations

import io
import base64
from pathlib import Path
from typing import BinaryIO, Any, cast, TypedDict
from collections.abc import Iterable, MutableMapping

from eml_parser import EmlParser
from returns.result import safe, ResultE, Failure

from splitter import FileHandler
from splitter.errors import ReadError
from splitter.interfaces import IExtensionHandler
from splitter.file import File, FileOrError, MetadataType


class MessageType(TypedDict):
    header: MutableMapping[str, str]
    body: list[MutableMapping[str, Any]]
    attachment: list[MutableMapping[str, Any]]


class ReadEmlError(ReadError):
    pass


class EmlHandler(IExtensionHandler):
    def __init__(
        self,
        attachment_handler: FileHandler,
        include_cid: bool = True,
        eml_parser: EmlParser | None = None,
    ) -> None:
        self.attachment_handler = attachment_handler
        self.include_cid = include_cid
        self.eml_parser = eml_parser or EmlParser(
            include_raw_body=True, include_attachment_data=True
        )

    def to_files(self, file: File) -> Iterable[FileOrError]:
        message_result = _read_eml(self.eml_parser, file.stream.read())
        if isinstance(message_result, Failure):
            yield message_result
            return

        message = message_result.unwrap()
        message_metadata = cast(
            MetadataType,
            {
                key: value
                for key, value in message.get("header", {}).items()
                if key in {"subject", "from", "to", "cc"}
            },
        )

        basename = Path(file.vpath).name
        for file_data in _get_attachments(message, self.include_cid):
            if isinstance(file_data, Failure):
                yield file_data
                continue

            yield from self._split_attachment(
                file_data.unwrap(), basename, message_metadata
            )

    def _split_attachment(
        self,
        att_data: tuple[str, str, BinaryIO],
        basename: str,
        message_metadata: MetadataType,
    ) -> Iterable[FileOrError]:
        att_filename, att_path, att_stream = att_data
        for page in self.attachment_handler.split_document(att_stream, att_path):
            yield page.bind(
                lambda file: process_page(
                    file, basename, message_metadata, att_filename
                )
            )


@safe
def process_page(
    page: File, basename: str, message_metadata: MetadataType, att_filename: str
) -> File:
    page_filename = Path(page.vpath).name
    page.vpath = f"{basename}-{page_filename}"
    metadata = page.metadata or {}
    metadata.update(message_metadata)
    metadata.update(
        cast(
            MetadataType,
            {
                "original_filename": basename,
                "attachment_filename": metadata.get("original_filename", att_filename),
            },
        )
    )
    return page


@safe(exceptions=(ReadEmlError,))
def _read_eml(eml_parser: EmlParser, eml_bytes: bytes) -> MessageType:
    try:
        return cast(MessageType, eml_parser.decode_email_bytes(eml_bytes))
    except Exception as e:  # noqa BLE001
        raise ReadEmlError(f"Error parsing EML: {e}") from e


def _get_attachments(
    message: MessageType, include_cid: bool = False
) -> Iterable[ResultE[tuple[str, str, BinaryIO]]]:
    html_bodies = message.get("body", [])
    html_bodies = [
        body["content"]
        for body in html_bodies
        if body.get("content_type", "text/plain") == "text/html"
    ]

    for attachment in message.get("attachment", []):
        att_filename = attachment["filename"]

        # Exclude embedded images (or at least try)
        if not include_cid and any(
            f"cid:{att_filename}" in body for body in html_bodies
        ):
            continue

        yield _get_single_attachment(attachment, att_filename)


@safe
def _get_single_attachment(
    attachment: MutableMapping[str, str], att_filename: str
) -> tuple[str, str, BinaryIO]:
    # Replacing "/" by "-", since some attachments have "/"
    # in their filename which the os interprets as a subdirectory
    # Also Truncate name, to avoid OSError Errno 36: Name Too long
    att_filename = att_filename.replace("/", "-")[:50]
    to_decode = attachment.pop("raw")
    att_stream = io.BytesIO(base64.b64decode(to_decode))

    return (
        attachment["filename"],
        att_filename,
        att_stream,
    )
