"""Lightweight text extraction utilities.

Provides `extract_text_from_file(path)` which currently supports PDF extraction
via `pdfminer.six` and simple fallbacks for plain text files. Additional
formats (docx/odt) can be added later.
"""
from pathlib import Path
import os

def _extract_text_from_pdf(path: str) -> str:
    try:
        # Local import so the module can still be imported when pdfminer isn't installed
        from pdfminer.high_level import extract_text
    except Exception as e:  # pragma: no cover - runtime import guard
        raise ImportError("pdfminer.six is required for PDF extraction") from e

    # pdfminer.extract_text returns unicode text
    try:
        text = extract_text(path)
        return text or ""
    except Exception:
        # Last-resort fallback: read bytes and try to decode
        try:
            with open(path, "rb") as fh:
                data = fh.read()
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return ""

def _extract_text_from_plain(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except Exception:
        # binary fallback
        try:
            with open(path, "rb") as fh:
                return fh.read().decode("utf-8", errors="ignore")
        except Exception:
            return ""

def extract_text_from_file(path: str) -> str:
    """Return extracted plain text for the given file path.

    Currently supports:
    - PDF files (uses pdfminer.six)
    - Plain text files (txt, md)

    Raises ImportError if a PDF is processed but pdfminer.six is not installed.
    """
    p = Path(path)
    ext = p.suffix.lower()
    if ext == ".pdf":
        return _extract_text_from_pdf(path)
    if ext in {".txt", ".md", ".markdown"}:
        return _extract_text_from_plain(path)

    # Unknown extension: try plain read then return empty
    return _extract_text_from_plain(path)
