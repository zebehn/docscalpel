"""
PDF processor module for validating and loading PDF documents.

This module handles PDF file validation, loading, and Document creation
using PyMuPDF (fitz) for efficient PDF processing.
"""

import os
from pathlib import Path
from typing import Optional, List

try:
    import fitz  # PyMuPDF
except ImportError:
    raise ImportError(
        "PyMuPDF (fitz) is required. Install with: pip install PyMuPDF"
    )

from .models import (
    Document,
    Page,
    ValidationResult,
    InvalidPDFError,
    CorruptedPDFError,
    EncryptedPDFError,
)


def validate_pdf(pdf_path: str) -> ValidationResult:
    """
    Validate a PDF file without fully loading it.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        ValidationResult indicating whether the file is a valid PDF,
        with error details if validation fails

    Example:
        >>> result = validate_pdf("paper.pdf")
        >>> if result.is_valid:
        ...     print(f"Valid PDF with {result.page_count} pages")
    """
    # Check if file exists
    if not os.path.exists(pdf_path):
        return ValidationResult(
            is_valid=False,
            error_message=f"File not found: {pdf_path}",
            page_count=None,
            is_encrypted=False
        )

    # Check if file is empty
    file_size = os.path.getsize(pdf_path)
    if file_size == 0:
        return ValidationResult(
            is_valid=False,
            error_message=f"File is empty: {pdf_path}",
            page_count=None,
            is_encrypted=False
        )

    # Try to open with PyMuPDF
    try:
        doc = fitz.open(pdf_path)

        # Check if encrypted
        if doc.is_encrypted:
            doc.close()
            return ValidationResult(
                is_valid=False,
                error_message=f"PDF is encrypted/password-protected: {pdf_path}",
                page_count=None,
                is_encrypted=True
            )

        # Get page count
        page_count = len(doc)

        # Check if document is valid (has at least one page)
        if page_count == 0:
            doc.close()
            return ValidationResult(
                is_valid=False,
                error_message=f"PDF has no pages: {pdf_path}",
                page_count=0,
                is_encrypted=False
            )

        doc.close()

        return ValidationResult(
            is_valid=True,
            error_message=None,
            page_count=page_count,
            is_encrypted=False
        )

    except fitz.FileDataError as e:
        # Corrupted or invalid PDF structure
        return ValidationResult(
            is_valid=False,
            error_message=f"Corrupted or invalid PDF structure: {str(e)}",
            page_count=None,
            is_encrypted=False
        )

    except Exception as e:
        # Other errors (e.g., not a PDF file)
        error_msg = str(e).lower()
        if "not a valid pdf" in error_msg or "not a pdf" in error_msg:
            return ValidationResult(
                is_valid=False,
                error_message=f"File is not a valid PDF: {pdf_path}",
                page_count=None,
                is_encrypted=False
            )
        else:
            return ValidationResult(
                is_valid=False,
                error_message=f"Error opening PDF: {str(e)}",
                page_count=None,
                is_encrypted=False
            )


def load_document(
    pdf_path: str,
    max_pages: Optional[int] = None
) -> Document:
    """
    Load a PDF document and create a Document object with all pages.

    Args:
        pdf_path: Path to the PDF file
        max_pages: Maximum number of pages to load (None = all pages)

    Returns:
        Document object with populated pages and metadata

    Raises:
        InvalidPDFError: If file doesn't exist or is not a valid PDF
        CorruptedPDFError: If PDF is damaged or incomplete
        EncryptedPDFError: If PDF is password-protected
        ConfigurationError: If max_pages is invalid

    Example:
        >>> doc = load_document("paper.pdf")
        >>> print(f"Loaded {doc.page_count} pages")
    """
    # Validate max_pages parameter
    if max_pages is not None and max_pages <= 0:
        from .models import ConfigurationError
        raise ConfigurationError("max_pages must be greater than 0")

    # First validate the PDF
    validation = validate_pdf(pdf_path)

    if not validation.is_valid:
        # Raise appropriate error based on validation result
        if validation.is_encrypted:
            raise EncryptedPDFError(
                f"Cannot load encrypted PDF: {pdf_path}. "
                "Please decrypt the file first."
            )
        elif "corrupted" in validation.error_message.lower():
            raise CorruptedPDFError(validation.error_message)
        else:
            raise InvalidPDFError(validation.error_message)

    # Open the PDF document
    try:
        doc = fitz.open(pdf_path)

        # Get file size
        file_size = os.path.getsize(pdf_path)

        # Extract metadata
        metadata = {}
        if doc.metadata:
            # Common metadata fields
            metadata_fields = [
                'title', 'author', 'subject', 'keywords',
                'creator', 'producer', 'creationDate', 'modDate'
            ]
            for field in metadata_fields:
                value = doc.metadata.get(field)
                if value:
                    metadata[field] = value

        # Determine how many pages to load
        total_pages = len(doc)
        pages_to_load = min(total_pages, max_pages) if max_pages else total_pages

        # Create Page objects for each page
        pages: List[Page] = []
        for page_num in range(pages_to_load):
            fitz_page = doc[page_num]

            # Get page dimensions
            rect = fitz_page.rect
            width = rect.width
            height = rect.height

            # Get page rotation
            rotation = fitz_page.rotation

            # Create Page object
            page = Page(
                page_number=page_num + 1,  # 1-indexed
                width=width,
                height=height,
                rotation=rotation,
                elements=[]  # Will be populated by detectors
            )
            pages.append(page)

        doc.close()

        # Create and return Document object
        document = Document(
            file_path=pdf_path,
            page_count=total_pages,
            pages=pages,
            metadata=metadata,
            file_size_bytes=file_size,
            is_encrypted=False
        )

        return document

    except fitz.FileDataError as e:
        raise CorruptedPDFError(
            f"PDF file is corrupted or incomplete: {pdf_path}. Error: {str(e)}"
        )

    except fitz.FileNotFoundError:
        raise InvalidPDFError(f"PDF file not found: {pdf_path}")

    except Exception as e:
        # Handle other unexpected errors
        raise InvalidPDFError(
            f"Failed to load PDF document '{pdf_path}': {str(e)}"
        )
