"""Extract plain text from uploaded medical documents.

Supported formats and strategy:

- PDF   : text is read with ``pdfplumber``; pages that yield little or no text
          (typically scanned documents) are rendered to an image with PyMuPDF
          and passed through Tesseract OCR.
- DOCX  : paragraphs are read with ``python-docx``.
- TXT   : decoded directly.
- Images: PNG/JPG/JPEG are read with Tesseract OCR.

All work here is synchronous and CPU-bound, so callers should run it in a worker
thread to avoid blocking the async event loop.
"""

import io
import logging
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from docx import Document as DocxDocument
from PIL import Image

from app.core.config import settings

logger = logging.getLogger(__name__)

# A PDF page with fewer than this many extractable characters is treated as
# scanned and routed through OCR instead.
MIN_PDF_TEXT_CHARS = 20
# Render resolution for OCR; higher is more accurate but slower.
OCR_RENDER_DPI = 200

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# Point pytesseract at an explicit binary if one is configured (useful on
# Windows where Tesseract is often not on PATH).
if settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


class UnsupportedDocumentError(ValueError):
    """Raised when a file extension cannot be processed."""


class TextExtractor:
    def extract(self, path: Path, extension: str) -> str:
        extension = extension.lower()
        if extension == ".pdf":
            return self._extract_pdf(path)
        if extension == ".docx":
            return self._extract_docx(path)
        if extension == ".txt":
            return self._extract_txt(path)
        if extension in _IMAGE_EXTENSIONS:
            return self._extract_image(path)
        raise UnsupportedDocumentError(f"Cannot extract text from '{extension}' files.")

    def _extract_pdf(self, path: Path) -> str:
        pages: list[str] = []
        # PyMuPDF is opened once and reused for OCR rendering of scanned pages.
        fitz_doc = fitz.open(path)
        try:
            with pdfplumber.open(path) as pdf:
                for index, page in enumerate(pdf.pages):
                    text = (page.extract_text() or "").strip()
                    if len(text) < MIN_PDF_TEXT_CHARS:
                        text = self._ocr_pdf_page(fitz_doc, index)
                    if text:
                        pages.append(text)
        finally:
            fitz_doc.close()
        return "\n\n".join(pages).strip()

    def _ocr_pdf_page(self, fitz_doc: "fitz.Document", index: int) -> str:
        page = fitz_doc.load_page(index)
        pixmap = page.get_pixmap(dpi=OCR_RENDER_DPI)
        image = Image.open(io.BytesIO(pixmap.tobytes("png")))
        return self._ocr_image(image)

    def _extract_docx(self, path: Path) -> str:
        document = DocxDocument(str(path))
        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        return "\n".join(paragraphs).strip()

    def _extract_txt(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="ignore").strip()

    def _extract_image(self, path: Path) -> str:
        with Image.open(path) as image:
            return self._ocr_image(image)

    def _ocr_image(self, image: Image.Image) -> str:
        return pytesseract.image_to_string(image).strip()
