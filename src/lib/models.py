"""
Data models for DocScalpel.

This module contains all core data classes and enums used throughout
the extraction library, following Library-First Architecture principles.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Tuple
from uuid import uuid4


# ============================================================================
# Enumerations
# ============================================================================

class ElementType(Enum):
    """Enumeration of supported element types."""
    FIGURE = "figure"
    TABLE = "table"
    EQUATION = "equation"

    def __str__(self) -> str:
        return self.value


class OutputFormat(Enum):
    """Enumeration for CLI output format options."""
    JSON = "json"
    HUMAN_READABLE = "text"


# ============================================================================
# Exception Classes
# ============================================================================

class PDFExtractorError(Exception):
    """Base exception for all PDF extractor errors."""
    pass


class InvalidPDFError(PDFExtractorError):
    """Raised when file is not a valid PDF format."""
    pass


class CorruptedPDFError(InvalidPDFError):
    """Raised when PDF is damaged or incomplete."""
    pass


class EncryptedPDFError(PDFExtractorError):
    """Raised when PDF is password-protected."""
    pass


class ConfigurationError(PDFExtractorError):
    """Raised when ExtractionConfig has invalid values."""
    pass


class ExtractionFailedError(PDFExtractorError):
    """Raised when extraction process encounters fatal error."""

    def __init__(self, message: str, partial_result=None):
        super().__init__(message)
        self.partial_result = partial_result


# ============================================================================
# Core Data Classes
# ============================================================================

@dataclass
class BoundingBox:
    """Defines the rectangular region of an element on a page."""
    x: float
    y: float
    width: float
    height: float
    page_number: int
    padding: int = 0

    def __post_init__(self):
        """Validate bounding box constraints."""
        if self.x < 0 or self.y < 0:
            raise ValueError("Coordinates must be non-negative")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Width and height must be positive")
        if self.page_number < 1:
            raise ValueError("Page number must be >= 1")
        if self.padding < 0:
            raise ValueError("Padding must be non-negative")

    @property
    def x2(self) -> float:
        """Right edge coordinate."""
        return self.x + self.width

    @property
    def y2(self) -> float:
        """Bottom edge coordinate."""
        return self.y + self.height

    @property
    def area(self) -> float:
        """Total area of the bounding box."""
        return self.width * self.height

    @property
    def center(self) -> Tuple[float, float]:
        """Center point of the bounding box."""
        return (self.x + self.width / 2, self.y + self.height / 2)


@dataclass
class Element:
    """Represents a detected item (figure, table, or equation)."""
    element_id: str
    element_type: ElementType
    bounding_box: BoundingBox
    page_number: int
    sequence_number: int
    confidence_score: float
    output_filename: str

    def __post_init__(self):
        """Validate element constraints."""
        if not isinstance(self.element_type, ElementType):
            raise ValueError("element_type must be ElementType enum")
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("confidence_score must be between 0.0 and 1.0")
        if self.sequence_number < 1:
            raise ValueError("sequence_number must be >= 1")
        if self.page_number < 1:
            raise ValueError("page_number must be >= 1")


@dataclass
class Page:
    """Represents a single page within a PDF document."""
    page_number: int
    width: float
    height: float
    rotation: int = 0
    elements: List[Element] = field(default_factory=list)

    def __post_init__(self):
        """Validate page constraints."""
        if self.page_number < 1:
            raise ValueError("page_number must be >= 1")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Width and height must be positive")
        if self.rotation not in {0, 90, 180, 270}:
            raise ValueError("rotation must be 0, 90, 180, or 270")


@dataclass
class Document:
    """Represents the input technical paper PDF file."""
    file_path: str
    page_count: int
    pages: List[Page] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    file_size_bytes: int = 0
    is_encrypted: bool = False

    def __post_init__(self):
        """Validate document constraints."""
        if self.page_count < 1:
            raise ValueError("page_count must be >= 1")


@dataclass
class ExtractionConfig:
    """Configuration object for customizing extraction behavior."""
    element_types: List[ElementType] = field(default_factory=lambda: [
        ElementType.FIGURE,
        ElementType.TABLE,
        ElementType.EQUATION
    ])
    output_directory: str = "."
    naming_pattern: str = "{type}_{counter:02d}.pdf"
    boundary_padding: int = 0
    confidence_threshold: float = 0.5
    output_format: OutputFormat = OutputFormat.HUMAN_READABLE
    overwrite_existing: bool = False
    max_pages: Optional[int] = None

    def __post_init__(self):
        """Validate configuration constraints."""
        if not self.element_types:
            raise ConfigurationError("element_types must not be empty")
        if "{type}" not in self.naming_pattern or "{counter" not in self.naming_pattern:
            raise ConfigurationError(
                "naming_pattern must contain {type} and {counter} placeholders"
            )
        if self.boundary_padding < 0:
            raise ConfigurationError("boundary_padding must be non-negative")
        if not (0.0 <= self.confidence_threshold <= 1.0):
            raise ConfigurationError("confidence_threshold must be between 0.0 and 1.0")
        if self.max_pages is not None and self.max_pages < 1:
            raise ConfigurationError("max_pages must be >= 1")


@dataclass
class ExtractionResult:
    """Represents the outcome of the extraction process."""
    document: Document
    elements: List[Element]
    output_directory: str
    success: bool
    extraction_time_seconds: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate result constraints."""
        if not self.success and not self.errors:
            raise ValueError("If success is False, errors must be non-empty")
        if self.extraction_time_seconds < 0:
            raise ValueError("extraction_time_seconds must be non-negative")

    @property
    def figure_count(self) -> int:
        """Count of figure elements."""
        return sum(1 for e in self.elements if e.element_type == ElementType.FIGURE)

    @property
    def table_count(self) -> int:
        """Count of table elements."""
        return sum(1 for e in self.elements if e.element_type == ElementType.TABLE)

    @property
    def equation_count(self) -> int:
        """Count of equation elements."""
        return sum(1 for e in self.elements if e.element_type == ElementType.EQUATION)

    @property
    def total_elements(self) -> int:
        """Total count of all elements."""
        return len(self.elements)


@dataclass
class ValidationResult:
    """Result object for PDF validation."""
    is_valid: bool
    error_message: Optional[str] = None
    page_count: Optional[int] = None
    is_encrypted: bool = False


# ============================================================================
# Factory Functions
# ============================================================================

def create_element(
    element_type: ElementType,
    bounding_box: BoundingBox,
    page_number: int,
    sequence_number: int,
    confidence_score: float,
    output_filename: str
) -> Element:
    """Factory function to create an Element with auto-generated UUID."""
    return Element(
        element_id=str(uuid4()),
        element_type=element_type,
        bounding_box=bounding_box,
        page_number=page_number,
        sequence_number=sequence_number,
        confidence_score=confidence_score,
        output_filename=output_filename
    )
