from io import BytesIO
from pathlib import Path
from typing import Literal, TypeAlias, TypedDict, BinaryIO, Any, cast
from dataclasses import dataclass, field

from returns.result import ResultE, safe


@dataclass
class TextContent:
    text: str
    source: Literal["ocr", "metadata"] = "metadata"
    content_type: Literal["text"] = "text"


@dataclass
class ImageContent:
    image: Any
    framework: Literal["opencv", "pillow"]
    content_type: Literal["image"] = "image"


class MetadataType(TypedDict, total=False):
    path: str
    mime_type: str | None


FileOrError: TypeAlias = ResultE["File"]
FileContent: TypeAlias = TextContent | ImageContent


@dataclass
class File:
    vpath: str  # virtual_path
    stream: BinaryIO
    contents: list[FileContent] = field(default_factory=list)
    metadata: MetadataType | None = field(
        default_factory=lambda: cast(MetadataType, {})
    )

    @property
    def text_contents(self) -> list[TextContent]:
        return [
            content for content in self.contents if isinstance(content, TextContent)
        ]

    def __repr__(self) -> str:
        class_name = type(self).__name__
        params = [
            f"{attr_name}={getattr(self, attr_name)}"
            for attr_name in ("vpath", "metadata")
        ]

        params.append("stream=None" if self.stream is None else "stream=...")
        params.append("contents=None" if self.contents is None else "contents=...")

        return f"{class_name}({', '.join(params)})"


@safe
def build_file(
    filepath: str,
    file_bytes: bytes | None,
    contents: list[FileContent] | None = None,
    metadata: MetadataType | None = None,
) -> File:
    return File(
        Path(filepath).name,
        metadata=metadata or {},
        contents=contents or [],
        stream=BytesIO(file_bytes or b""),
    )
