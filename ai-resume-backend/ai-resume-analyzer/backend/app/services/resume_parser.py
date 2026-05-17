import io
import os
import logging
import unicodedata
from pathlib import Path
from typing import Tuple

import pdfplumber
import docx2txt
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


async def save_and_extract(
    file: UploadFile,
    candidate_id: str,
) -> Tuple[str, str, int, int]:
    """
    Save uploaded resume file and extract its text content.

    Returns:
        (file_path, raw_text, file_size_bytes, page_count)
    """
    # Validate extension
    ext = Path(file.filename or "").suffix.lower().lstrip(".")
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '.{ext}' not allowed. Use: {settings.ALLOWED_EXTENSIONS}",
        )

    # Read file into memory to check size
    content = await file.read()
    file_size = len(content)

    if file_size > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB",
        )

    # Sanitize filename and build save path
    safe_name = _sanitize_filename(file.filename or "resume")
    save_path = UPLOAD_DIR / candidate_id / safe_name
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to disk
    with open(save_path, "wb") as f:
        f.write(content)

    # Extract text
    raw_text, page_count = _extract_text(content, ext)

    return str(save_path), raw_text, file_size, page_count


def _extract_text(content: bytes, ext: str) -> Tuple[str, int]:
    """Dispatch to the right extractor based on file extension."""
    if ext == "pdf":
        return _extract_pdf(content)
    elif ext in ("doc", "docx"):
        return _extract_docx(content), 1
    else:
        raise ValueError(f"Unsupported extension: {ext}")


def _extract_pdf(content: bytes) -> Tuple[str, int]:
    """Extract text from PDF using pdfplumber (preserves layout better than PyPDF2)."""
    pages_text: list[str] = []
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=2, y_tolerance=2)
                if text:
                    pages_text.append(text)
        raw = "\n\n".join(pages_text)
        return _clean_text(raw), len(pages_text)
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not parse PDF. Ensure the file is not scanned/image-only.",
        )


def _extract_docx(content: bytes) -> str:
    """Extract text from DOCX using docx2txt."""
    try:
        text = docx2txt.process(io.BytesIO(content))
        return _clean_text(text)
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not parse DOCX file.",
        )


def _clean_text(text: str) -> str:
    """Normalize unicode, remove control chars, collapse whitespace."""
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)
    # Remove non-printable control characters (except newlines/tabs)
    text = "".join(
        ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in "\n\t"
    )
    # Collapse multiple blank lines into two
    import re
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _sanitize_filename(filename: str) -> str:
    """Remove path traversal and special characters from filename."""
    name = os.path.basename(filename)
    # Keep only safe chars
    safe = "".join(c for c in name if c.isalnum() or c in "._- ")
    return safe.strip() or "resume.pdf"


def delete_resume_file(file_path: str) -> None:
    """Delete a resume file from disk (used when re-uploading)."""
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            # Remove empty parent dir
            if not any(path.parent.iterdir()):
                path.parent.rmdir()
    except Exception as e:
        logger.warning(f"Could not delete file {file_path}: {e}")
