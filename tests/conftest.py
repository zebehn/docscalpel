"""
Pytest configuration and shared fixtures for DocScalpel tests.

This module provides reusable test fixtures for sample PDFs, test data,
and common test utilities.
"""

import pytest
import os
from pathlib import Path
from typing import List

from docscalpel.models import (
    ElementType,
    BoundingBox,
    Element,
    Document,
    Page,
    ExtractionConfig,
    ExtractionResult,
    create_element,
)


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def fixtures_dir(project_root) -> Path:
    """Return the fixtures directory path."""
    return project_root / "fixtures"


@pytest.fixture
def temp_output_dir(tmp_path) -> Path:
    """Create and return a temporary output directory for tests."""
    output_dir = tmp_path / "extracted"
    output_dir.mkdir()
    return output_dir


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_bounding_box() -> BoundingBox:
    """Create a sample bounding box for testing."""
    return BoundingBox(
        x=72.0,
        y=150.5,
        width=468.0,
        height=280.3,
        page_number=1,
        padding=0
    )


@pytest.fixture
def sample_figure_element(sample_bounding_box) -> Element:
    """Create a sample figure element for testing."""
    return create_element(
        element_type=ElementType.FIGURE,
        bounding_box=sample_bounding_box,
        page_number=1,
        sequence_number=1,
        confidence_score=0.95,
        output_filename="figure_01.pdf"
    )


@pytest.fixture
def sample_table_element() -> Element:
    """Create a sample table element for testing."""
    bbox = BoundingBox(x=50.0, y=200.0, width=500.0, height=300.0, page_number=2)
    return create_element(
        element_type=ElementType.TABLE,
        bounding_box=bbox,
        page_number=2,
        sequence_number=1,
        confidence_score=0.89,
        output_filename="table_01.pdf"
    )


@pytest.fixture
def sample_equation_element() -> Element:
    """Create a sample equation element for testing."""
    bbox = BoundingBox(x=100.0, y=300.0, width=400.0, height=80.0, page_number=3)
    return create_element(
        element_type=ElementType.EQUATION,
        bounding_box=bbox,
        page_number=3,
        sequence_number=1,
        confidence_score=0.92,
        output_filename="equation_01.pdf"
    )


@pytest.fixture
def sample_page() -> Page:
    """Create a sample page for testing."""
    return Page(
        page_number=1,
        width=595.0,  # A4 width in points
        height=842.0,  # A4 height in points
        rotation=0,
        elements=[]
    )


@pytest.fixture
def sample_document(sample_page) -> Document:
    """Create a sample document for testing."""
    return Document(
        file_path="test_paper.pdf",
        page_count=10,
        pages=[sample_page],
        metadata={"title": "Test Paper", "author": "Test Author"},
        file_size_bytes=1024000,
        is_encrypted=False
    )


@pytest.fixture
def default_extraction_config() -> ExtractionConfig:
    """Create a default extraction configuration for testing."""
    return ExtractionConfig()


@pytest.fixture
def figure_only_config() -> ExtractionConfig:
    """Create a configuration for extracting figures only."""
    return ExtractionConfig(
        element_types=[ElementType.FIGURE],
        output_directory="./test_output"
    )


@pytest.fixture
def custom_config(temp_output_dir) -> ExtractionConfig:
    """Create a custom configuration for testing."""
    return ExtractionConfig(
        element_types=[ElementType.FIGURE, ElementType.TABLE],
        output_directory=str(temp_output_dir),
        naming_pattern="img_{counter:03d}.pdf",
        boundary_padding=10,
        confidence_threshold=0.7,
        overwrite_existing=True
    )


@pytest.fixture
def sample_extraction_result(
    sample_document,
    sample_figure_element,
    temp_output_dir
) -> ExtractionResult:
    """Create a sample extraction result for testing."""
    return ExtractionResult(
        document=sample_document,
        elements=[sample_figure_element],
        output_directory=str(temp_output_dir),
        success=True,
        extraction_time_seconds=10.5,
        errors=[],
        warnings=[]
    )


@pytest.fixture
def mixed_elements_result(
    sample_document,
    sample_figure_element,
    sample_table_element,
    sample_equation_element,
    temp_output_dir
) -> ExtractionResult:
    """Create an extraction result with mixed element types."""
    return ExtractionResult(
        document=sample_document,
        elements=[sample_figure_element, sample_table_element, sample_equation_element],
        output_directory=str(temp_output_dir),
        success=True,
        extraction_time_seconds=20.3,
        errors=[],
        warnings=[]
    )


# ============================================================================
# PDF Fixtures (Placeholders for actual PDF files)
# ============================================================================

@pytest.fixture
def sample_pdf_path(fixtures_dir) -> str:
    """Return path to sample PDF with figures (placeholder)."""
    # In actual implementation, this would point to a real test PDF
    return str(fixtures_dir / "sample_paper_with_figures.pdf")


@pytest.fixture
def mixed_content_pdf_path(fixtures_dir) -> str:
    """Return path to PDF with figures, tables, and equations (placeholder)."""
    return str(fixtures_dir / "sample_paper_mixed.pdf")


@pytest.fixture
def text_only_pdf_path(fixtures_dir) -> str:
    """Return path to PDF with no elements (placeholder)."""
    return str(fixtures_dir / "text_only_paper.pdf")


# ============================================================================
# Test Utilities
# ============================================================================

@pytest.fixture
def assert_file_exists():
    """Fixture providing a function to assert file existence."""
    def _assert_exists(file_path: str):
        assert os.path.exists(file_path), f"File does not exist: {file_path}"
        assert os.path.isfile(file_path), f"Path is not a file: {file_path}"
    return _assert_exists


@pytest.fixture
def assert_pdf_valid():
    """Fixture providing a function to assert PDF file validity."""
    def _assert_valid(file_path: str):
        assert file_path.endswith(".pdf"), f"Not a PDF file: {file_path}"
        # In actual implementation, would use PyMuPDF to validate
    return _assert_valid


@pytest.fixture
def count_elements_by_type():
    """Fixture providing a function to count elements by type."""
    def _count(elements: List[Element], element_type: ElementType) -> int:
        return sum(1 for e in elements if e.element_type == element_type)
    return _count
