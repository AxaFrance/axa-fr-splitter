import base64
import logging
import traceback
from io import BytesIO
from pathlib import Path
from typing import Iterable, IO

from eml_parser import EmlParser

from splitter.errors import ConvertError
from splitter.extension_handler_interface import IExtensionHandler
from splitter.file import File


class ConvertEmlError(ConvertError):
    pass


def _read_eml(eml_parser, eml_bytes):
    return eml_parser.decode_email_bytes(eml_bytes)


def _get_attachments(
    message, attachment_handler, include_cid=False, logger=logging.getLogger(__name__)
):
    try:
        html_bodies = message.get("body", [])
        html_bodies = [
            body["content"]
            for body in html_bodies
            if body.get("content_type", "text/plain") == "text/html"
        ]

        for attachment in message.get("attachment", []):
            attachment_filename = attachment["filename"]

            # Exclude embedded images (or at least try)
            if not include_cid and any(
                f"cid:{attachment_filename}" in body for body in html_bodies
            ):
                continue

            try:
                # Replacing "/" by "-", since some attachments have "/" in their filename
                # which the os interprets as a subdirectory
                # Also Truncate name, to avoid OSError Errno 36: Name Too long
                attachment_filename = attachment_filename.replace("/", "-")[:50]
                to_decode = attachment.pop("raw")
                attachment_stream = BytesIO(base64.b64decode(to_decode))

                if attachment_handler.is_supported(
                    attachment_filename, attachment_stream
                ):
                    yield attachment["filename"], attachment_filename, attachment_stream
            except Exception:
                exception_traceback = traceback.format_exc()
                logger.error(f"EML: Error with decode filename: {attachment_filename}")
                logger.error(exception_traceback)
    except Exception as e:
        raise ConvertEmlError(e)


class EmlHandler(IExtensionHandler):
    def __init__(
        self,
        attachment_handler,
        include_cid=True,
        eml_parser=EmlParser(include_raw_body=True, include_attachment_data=True),
        logger=logging.getLogger(__name__),
    ):
        self.attachment_handler = attachment_handler
        self.include_cid = include_cid
        self.eml_parser = eml_parser
        self.logger = logger

    def to_files(self, path: str, file_stream: IO) -> Iterable[File]:
        logger = self.logger
        message = _read_eml(self.eml_parser, file_stream.read())

        message_metadata = {
            key: value
            for key, value in message.get("header", {}).items()
            if key in {"subject", "from", "to", "cc"}
        }

        basename = Path(path).name
        for att_filename, att_path, att_stream in _get_attachments(
            message, self.attachment_handler, self.include_cid, logger
        ):
            try:
                yield from self.split_document(
                    att_filename, att_path, att_stream, basename, message_metadata
                )
            except Exception:
                exception_traceback = traceback.format_exc()
                logger.error(
                    f"EML: Error with filename: {att_filename} and path: {att_path}:\n"
                )
                logger.error(exception_traceback)

    def split_document(
        self, att_filename, att_path, att_stream, basename, message_metadata
    ):
        for page in self.attachment_handler.split_document(att_path, att_stream):
            page_filename = Path(page.relative_path).name
            page.relative_path = f"{basename}-{page_filename}".replace("/", "-")
            metadata = page.metadata
            metadata.update(message_metadata)
            metadata.update(
                {
                    "original_filename": basename,
                    "attachment_filename": metadata.get(
                        "original_filename", att_filename
                    ),
                }
            )
            yield page
