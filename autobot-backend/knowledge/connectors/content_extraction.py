# Copyright 2025-2026 mrveiss
# SPDX-License-Identifier: Apache-2.0
# AutoBot - AI-Powered Automation Platform
# Author: mrveiss
"""Shared content-extraction helpers for knowledge connectors.

Pure, provider-agnostic document text extraction that was byte-identical across
the Google Drive and OneDrive connectors. Extracted here so every connector
imports a single implementation (#9794 duplication sweep) instead of carrying
its own copy.
"""

import io

from autobot_shared.logging_manager import get_logger

logger = get_logger(__name__)


def extract_text_from_docx(content_bytes: bytes) -> str:
    """Extract text from Word .docx file."""
    try:
        from docx import Document

        doc = Document(io.BytesIO(content_bytes))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as exc:
        logger.warning("Failed to extract text from DOCX: %s", exc)
        return ""


def extract_text_from_pdf(content_bytes: bytes) -> str:
    """Extract text from PDF file."""
    try:
        from PyPDF2 import PdfReader

        pdf = PdfReader(io.BytesIO(content_bytes))
        pages_text = []
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text.strip():
                pages_text.append(f"## Page {page_num}\n{text}")
        return "\n\n".join(pages_text)
    except Exception as exc:
        logger.warning("Failed to extract text from PDF: %s", exc)
        return ""
