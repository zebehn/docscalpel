"""
DocScalpel Library

Surgical precision for PDF element extraction.

A standalone library for detecting and extracting figures, tables, and equations
from academic PDFs using deep learning (DocLayout-YOLO).

Public API (v1.0.0):
- extract_elements(): Main extraction function
- validate_pdf(): PDF validation function
- Data models: ElementType, ExtractionConfig, ExtractionResult, etc.
- Exceptions: All custom exceptions

Example:
    from docscalpel import extract_elements, ExtractionConfig, ElementType

    config = ExtractionConfig(element_types=[ElementType.FIGURE])
    result = extract_elements("paper.pdf", config)
    print(f"Extracted {result.figure_count} figures")
"""

from .models import (
    # Enumerations
    ElementType,
    OutputFormat,

    # Data classes
    BoundingBox,
    Element,
    Page,
    Document,
    ExtractionConfig,
    ExtractionResult,
    ValidationResult,

    # Exceptions
    PDFExtractorError,
    InvalidPDFError,
    CorruptedPDFError,
    EncryptedPDFError,
    ConfigurationError,
    ExtractionFailedError,

    # Factory functions
    create_element,
)

# Main extraction functions
from .extractor import extract_elements
from .pdf_processor import validate_pdf

__all__ = [
    # Enumerations
    "ElementType",
    "OutputFormat",

    # Data classes
    "BoundingBox",
    "Element",
    "Page",
    "Document",
    "ExtractionConfig",
    "ExtractionResult",
    "ValidationResult",

    # Exceptions
    "PDFExtractorError",
    "InvalidPDFError",
    "CorruptedPDFError",
    "EncryptedPDFError",
    "ConfigurationError",
    "ExtractionFailedError",

    # Factory functions
    "create_element",

    # Main functions
    "extract_elements",
    "validate_pdf",
]

__version__ = "1.1.0"
