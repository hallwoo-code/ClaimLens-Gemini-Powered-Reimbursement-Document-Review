from __future__ import annotations

import mimetypes
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable, Optional

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_MIME_TYPES = {"application/pdf", "image/png", "image/jpeg"}
MAX_FILES_PER_REVIEW = 3
MAX_FILE_SIZE_MB = 30
INLINE_GEMINI_LIMIT_MB = 20


@dataclass(frozen=True)
class FilenameClaim:
    claimed_total: Optional[float]
    claimed_currency: Optional[str]
    evidence: Optional[str]


@dataclass(frozen=True)
class UploadedDocument:
    name: str
    mime_type: str
    data: bytes

    @property
    def suffix(self) -> str:
        return Path(self.name).suffix.lower()

    @property
    def size_mb(self) -> float:
        return len(self.data) / (1024 * 1024)

    @property
    def requires_files_api(self) -> bool:
        return self.mime_type == "application/pdf" and self.size_mb > INLINE_GEMINI_LIMIT_MB


def parse_filename_claim(filename: str) -> FilenameClaim:
    """Parse explicit total markers such as total_1990_20 as 1990.20."""
    stem = Path(filename).stem.lower()
    match = re.search(r"(?:^|_)(?:(?P<prefix>[a-z]{3})_)?total_(?P<whole>\d+)_(?P<cents>\d{2})(?:_(?P<suffix>[a-z]{3}))?(?:_|$)", stem)
    if not match:
        return FilenameClaim(None, None, None)
    amount = float(f"{int(match.group('whole'))}.{match.group('cents')}")
    currency = match.group("prefix") or match.group("suffix")
    return FilenameClaim(amount, currency.upper() if currency else None, match.group(0).strip("_"))


def guess_mime_type(filename: str) -> str:
    guessed, _ = mimetypes.guess_type(filename)
    if guessed == "image/jpg":
        return "image/jpeg"
    return guessed or "application/octet-stream"


def validate_file_name_and_size(filename: str, size_bytes: int, mime_type: Optional[str] = None) -> list[str]:
    errors: list[str] = []
    suffix = Path(filename).suffix.lower()
    resolved_mime = mime_type or guess_mime_type(filename)
    if suffix not in ALLOWED_EXTENSIONS:
        errors.append(f"Unsupported file extension: {suffix or '(none)'}")
    if resolved_mime not in ALLOWED_MIME_TYPES:
        errors.append(f"Unsupported MIME type: {resolved_mime}")
    if size_bytes <= 0:
        errors.append("File is empty.")
    if size_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
        errors.append(f"File exceeds {MAX_FILE_SIZE_MB} MB public demo limit.")
    return errors


def validate_upload_batch(files: Iterable[UploadedDocument]) -> list[str]:
    files = list(files)
    errors: list[str] = []
    if len(files) > MAX_FILES_PER_REVIEW:
        errors.append(f"Upload at most {MAX_FILES_PER_REVIEW} files per review.")
    for file in files:
        errors.extend(validate_file_name_and_size(file.name, len(file.data), file.mime_type))
    return errors


def write_temp_upload(upload: UploadedDocument) -> Path:
    suffix = Path(upload.name).suffix.lower()
    fd, tmp_path = tempfile.mkstemp(prefix="reimband_gemini_", suffix=suffix)
    with open(fd, "wb", closefd=True) as handle:
        handle.write(upload.data)
    return Path(tmp_path)
