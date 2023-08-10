from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class File:
    relative_path: str
    file_bytes: Optional[bytes] = None
    metadata: Optional[dict] = field(default_factory=dict)


def build_file(filename: str, file_bytes: bytes, metadata=None):
    return File(Path(filename).name, metadata=metadata or {}, file_bytes=file_bytes)
