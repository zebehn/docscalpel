"""
PDF cropping module for extracting elements as separate PDF files.

This module handles cropping bounding box regions from PDF pages
and saving them as individual PDF files using PyMuPDF.
"""

import os
from pathlib import Path
import logging

try:
    import fitz  # PyMuPDF
except ImportError:
    raise ImportError(
        "PyMuPDF (fitz) is required. Install with: pip install PyMuPDF"
    )

from .models import Element, BoundingBox, ExtractionFailedError

logger = logging.getLogger(__name__)


def crop_element(
    pdf_path: str,
    element: Element,
    output_path: str,
    overwrite: bool = False
) -> bool:
    """
    Crop an element from a PDF page and save as a separate PDF file.

    Args:
        pdf_path: Path to the source PDF file
        element: Element object with bounding box information
        output_path: Path where the cropped PDF should be saved
        overwrite: Whether to overwrite existing files

    Returns:
        True if cropping succeeded, False otherwise

    Raises:
        ExtractionFailedError: If cropping fails critically
        FileExistsError: If output file exists and overwrite=False

    Example:
        >>> element = Element(...)  # Element with bounding box
        >>> success = crop_element("paper.pdf", element, "figure_01.pdf")
        >>> print(f"Cropping {'succeeded' if success else 'failed'}")
    """
    # Check if output file already exists
    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(
            f"Output file already exists: {output_path}. "
            "Use overwrite=True to replace it."
        )

    try:
        # Open source PDF
        doc = fitz.open(pdf_path)

        # Get the specific page (0-indexed in PyMuPDF)
        page_index = element.page_number - 1
        if page_index < 0 or page_index >= len(doc):
            raise ExtractionFailedError(
                f"Invalid page number {element.page_number} "
                f"for PDF with {len(doc)} pages"
            )

        page = doc[page_index]

        # Get bounding box with padding
        bbox = element.bounding_box
        padding = bbox.padding

        # Calculate crop rect with padding
        x0 = max(0, bbox.x - padding)
        y0 = max(0, bbox.y - padding)
        x1 = min(page.rect.width, bbox.x + bbox.width + padding)
        y1 = min(page.rect.height, bbox.y + bbox.height + padding)

        # Create crop rectangle
        crop_rect = fitz.Rect(x0, y0, x1, y1)

        # Validate crop dimensions
        if crop_rect.width <= 0 or crop_rect.height <= 0:
            logger.warning(
                f"Invalid crop dimensions for element {element.element_id}: "
                f"width={crop_rect.width}, height={crop_rect.height}"
            )
            return False

        # Set page crop box
        page.set_cropbox(crop_rect)

        # Create output PDF with just this cropped page
        output_doc = fitz.open()  # New empty PDF
        output_doc.insert_pdf(
            doc,
            from_page=page_index,
            to_page=page_index,
            start_at=-1
        )

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Save cropped PDF
        output_doc.save(output_path)
        output_doc.close()
        doc.close()

        logger.debug(f"Successfully cropped element to {output_path}")
        return True

    except FileExistsError:
        # Re-raise file exists error
        raise

    except Exception as e:
        logger.error(f"Failed to crop element {element.element_id}: {e}")
        raise ExtractionFailedError(
            f"Failed to crop element from page {element.page_number}: {str(e)}"
        )


def validate_cropped_pdf(output_path: str) -> bool:
    """
    Validate that a cropped PDF file contains exactly one page/element.

    Args:
        output_path: Path to the cropped PDF file

    Returns:
        True if valid (single page), False otherwise
    """
    try:
        doc = fitz.open(output_path)
        page_count = len(doc)
        doc.close()

        if page_count != 1:
            logger.warning(
                f"Cropped PDF has {page_count} pages, expected 1: {output_path}"
            )
            return False

        return True

    except Exception as e:
        logger.error(f"Failed to validate cropped PDF {output_path}: {e}")
        return False
