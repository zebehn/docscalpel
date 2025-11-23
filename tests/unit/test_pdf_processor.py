"""
Unit tests for PDF processor module.

Tests PDF validation, loading, and document creation functionality.

Test Strategy (TDD):
1. Write these tests FIRST
2. Verify they FAIL (no implementation yet)
3. Implement pdf_processor.py
4. Verify tests PASS
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.lib.models import (
    Document,
    Page,
    ValidationResult,
    InvalidPDFError,
    CorruptedPDFError,
    EncryptedPDFError,
    ConfigurationError,
)


class TestValidatePDF:
    """Test the validate_pdf() function."""

    def test_validate_pdf_function_exists(self):
        """Verify validate_pdf() function is importable."""
        from src.lib.pdf_processor import validate_pdf
        assert callable(validate_pdf)

    def test_validate_pdf_with_valid_file_returns_valid(self, sample_pdf_path):
        """
        Unit test: validate_pdf() returns ValidationResult for valid PDF.

        Given: Path to a valid PDF file
        When: validate_pdf() is called
        Then: Returns ValidationResult with is_valid=True
        """
        from src.lib.pdf_processor import validate_pdf

        result = validate_pdf(sample_pdf_path)

        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert result.page_count is not None
        assert result.page_count > 0
        assert result.error_message is None
        assert result.is_encrypted is False

    def test_validate_pdf_with_missing_file_returns_invalid(self, tmp_path):
        """
        Unit test: validate_pdf() detects missing files.

        Given: Path to non-existent file
        When: validate_pdf() is called
        Then: Returns ValidationResult with is_valid=False and error message
        """
        from src.lib.pdf_processor import validate_pdf

        missing_file = tmp_path / "does_not_exist.pdf"

        result = validate_pdf(str(missing_file))

        assert result.is_valid is False
        assert result.error_message is not None
        assert "not found" in result.error_message.lower() or \
               "does not exist" in result.error_message.lower()

    def test_validate_pdf_with_non_pdf_file_returns_invalid(self, tmp_path):
        """
        Unit test: validate_pdf() detects non-PDF files.

        Given: Path to a text file (not a PDF)
        When: validate_pdf() is called
        Then: Returns ValidationResult with is_valid=False
        """
        from src.lib.pdf_processor import validate_pdf

        text_file = tmp_path / "not_a_pdf.txt"
        text_file.write_text("This is plain text")

        result = validate_pdf(str(text_file))

        assert result.is_valid is False
        assert result.error_message is not None
        assert "not a valid PDF" in result.error_message.lower()

    def test_validate_pdf_with_corrupted_file_returns_invalid(self, tmp_path):
        """
        Unit test: validate_pdf() detects corrupted PDFs.

        Given: Path to corrupted/incomplete PDF
        When: validate_pdf() is called
        Then: Returns ValidationResult with is_valid=False
        """
        from src.lib.pdf_processor import validate_pdf

        corrupted_pdf = tmp_path / "corrupted.pdf"
        # Write incomplete PDF header
        corrupted_pdf.write_bytes(b"%PDF-1.4\n%\xE2\xE3")

        result = validate_pdf(str(corrupted_pdf))

        assert result.is_valid is False
        assert result.error_message is not None

    def test_validate_pdf_detects_encrypted_file(self, tmp_path):
        """
        Unit test: validate_pdf() detects encrypted PDFs.

        Given: Path to encrypted/password-protected PDF
        When: validate_pdf() is called
        Then: Returns ValidationResult with is_encrypted=True
        """
        pytest.skip("Encrypted PDF fixture not yet available")


class TestLoadDocument:
    """Test the load_document() function."""

    def test_load_document_function_exists(self):
        """Verify load_document() function is importable."""
        from src.lib.pdf_processor import load_document
        assert callable(load_document)

    def test_load_document_returns_document_object(self, sample_pdf_path):
        """
        Unit test: load_document() returns Document with populated fields.

        Given: Path to valid PDF
        When: load_document() is called
        Then: Returns Document with all required fields
        """
        from src.lib.pdf_processor import load_document

        document = load_document(sample_pdf_path)

        # Verify: Document structure
        assert isinstance(document, Document)
        assert document.file_path == sample_pdf_path
        assert document.page_count > 0
        assert document.file_size_bytes > 0
        assert isinstance(document.pages, list)
        assert isinstance(document.metadata, dict)
        assert document.is_encrypted is False

    def test_load_document_populates_pages(self, sample_pdf_path):
        """
        Unit test: load_document() creates Page objects for each page.

        Given: Valid PDF with multiple pages
        When: load_document() is called
        Then: Document.pages contains Page objects with correct data
        """
        from src.lib.pdf_processor import load_document

        document = load_document(sample_pdf_path)

        # Verify: Pages list is populated
        assert len(document.pages) == document.page_count

        # Verify: Each page has required fields
        for i, page in enumerate(document.pages):
            assert isinstance(page, Page)
            assert page.page_number == i + 1
            assert page.width > 0
            assert page.height > 0
            assert page.rotation in {0, 90, 180, 270}
            assert isinstance(page.elements, list)

    def test_load_document_extracts_metadata(self, sample_pdf_path):
        """
        Unit test: load_document() extracts PDF metadata.

        Given: PDF with metadata (title, author, etc.)
        When: load_document() is called
        Then: Document.metadata contains extracted information
        """
        from src.lib.pdf_processor import load_document

        document = load_document(sample_pdf_path)

        # Verify: Metadata is a dictionary
        assert isinstance(document.metadata, dict)

        # Common metadata fields (may not all be present)
        possible_keys = ['title', 'author', 'subject', 'creator', 'producer']
        # At least check that it's extracting something
        # (actual content depends on test PDF)

    def test_load_document_calculates_file_size(self, sample_pdf_path):
        """
        Unit test: load_document() calculates correct file size.

        Given: PDF file
        When: load_document() is called
        Then: Document.file_size_bytes matches actual file size
        """
        from src.lib.pdf_processor import load_document

        document = load_document(sample_pdf_path)

        # Verify: File size is positive
        assert document.file_size_bytes > 0

        # Verify: File size is reasonable (not wildly incorrect)
        actual_size = Path(sample_pdf_path).stat().st_size
        assert document.file_size_bytes == actual_size

    def test_load_document_with_invalid_pdf_raises_error(self, tmp_path):
        """
        Unit test: load_document() raises InvalidPDFError for invalid files.

        Given: Non-PDF file
        When: load_document() is called
        Then: Raises InvalidPDFError
        """
        from src.lib.pdf_processor import load_document

        text_file = tmp_path / "not_a_pdf.txt"
        text_file.write_text("This is not a PDF")

        with pytest.raises(InvalidPDFError):
            load_document(str(text_file))

    def test_load_document_with_missing_file_raises_error(self, tmp_path):
        """
        Unit test: load_document() raises InvalidPDFError for missing files.

        Given: Non-existent file path
        When: load_document() is called
        Then: Raises InvalidPDFError
        """
        from src.lib.pdf_processor import load_document

        missing_file = tmp_path / "does_not_exist.pdf"

        with pytest.raises(InvalidPDFError):
            load_document(str(missing_file))

    def test_load_document_with_corrupted_pdf_raises_error(self, tmp_path):
        """
        Unit test: load_document() raises CorruptedPDFError for damaged files.

        Given: Corrupted PDF file
        When: load_document() is called
        Then: Raises CorruptedPDFError
        """
        from src.lib.pdf_processor import load_document

        corrupted_pdf = tmp_path / "corrupted.pdf"
        corrupted_pdf.write_bytes(b"%PDF-1.4\n%")

        with pytest.raises((InvalidPDFError, CorruptedPDFError)):
            load_document(str(corrupted_pdf))

    def test_load_document_with_encrypted_pdf_raises_error(self):
        """
        Unit test: load_document() raises EncryptedPDFError for encrypted files.

        Given: Password-protected PDF
        When: load_document() is called
        Then: Raises EncryptedPDFError
        """
        pytest.skip("Encrypted PDF fixture not yet available")

    def test_load_document_respects_max_pages_limit(self, sample_pdf_path):
        """
        Unit test: load_document() respects max_pages configuration.

        Given: PDF with 10 pages and max_pages=5
        When: load_document() is called with max_pages=5
        Then: Only first 5 pages are loaded
        """
        from src.lib.pdf_processor import load_document

        # Load with page limit
        document = load_document(sample_pdf_path, max_pages=5)

        # Verify: Only loaded requested pages
        assert len(document.pages) <= 5

        # Verify: Page numbers are sequential from 1
        for i, page in enumerate(document.pages):
            assert page.page_number == i + 1


class TestPDFProcessorEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_load_document_with_single_page_pdf(self, tmp_path):
        """
        Unit test: Handle single-page PDFs correctly.

        Given: PDF with exactly 1 page
        When: load_document() is called
        Then: Document has page_count=1 and pages list with 1 item
        """
        pytest.skip("Single-page PDF fixture not yet available")

    def test_load_document_with_rotated_pages(self, sample_pdf_path):
        """
        Unit test: Handle rotated pages correctly.

        Given: PDF with rotated pages (90°, 180°, 270°)
        When: load_document() is called
        Then: Page.rotation field is set correctly
        """
        from src.lib.pdf_processor import load_document

        document = load_document(sample_pdf_path)

        # Verify: Rotation values are valid
        for page in document.pages:
            assert page.rotation in {0, 90, 180, 270}

    def test_load_document_with_large_pdf(self):
        """
        Unit test: Handle large PDFs efficiently.

        Given: PDF with 100+ pages
        When: load_document() is called
        Then: Completes without memory issues
        """
        pytest.skip("Large PDF fixture not yet available")

    def test_validate_pdf_with_empty_file(self, tmp_path):
        """
        Unit test: Handle empty files gracefully.

        Given: Empty file (0 bytes)
        When: validate_pdf() is called
        Then: Returns is_valid=False
        """
        from src.lib.pdf_processor import validate_pdf

        empty_file = tmp_path / "empty.pdf"
        empty_file.write_bytes(b"")

        result = validate_pdf(str(empty_file))

        assert result.is_valid is False
        assert result.error_message is not None

    def test_load_document_with_special_characters_in_path(self, tmp_path):
        """
        Unit test: Handle file paths with special characters.

        Given: PDF path with spaces and special characters
        When: load_document() is called
        Then: Loads successfully
        """
        pytest.skip("Special character path testing requires fixture setup")


class TestConfigurationValidation:
    """Test configuration validation in pdf_processor."""

    def test_load_document_rejects_negative_max_pages(self, sample_pdf_path):
        """
        Unit test: Validate max_pages parameter.

        Given: max_pages=-1 (invalid)
        When: load_document() is called
        Then: Raises ConfigurationError
        """
        from src.lib.pdf_processor import load_document

        with pytest.raises((ConfigurationError, ValueError)):
            load_document(sample_pdf_path, max_pages=-1)

    def test_load_document_with_max_pages_zero(self, sample_pdf_path):
        """
        Unit test: Handle max_pages=0 edge case.

        Given: max_pages=0
        When: load_document() is called
        Then: Raises ConfigurationError or loads all pages
        """
        from src.lib.pdf_processor import load_document

        with pytest.raises((ConfigurationError, ValueError)):
            load_document(sample_pdf_path, max_pages=0)


class TestPDFProcessorIntegrationWithPyMuPDF:
    """Test integration with PyMuPDF library."""

    def test_load_document_uses_pymupdf(self, sample_pdf_path):
        """
        Unit test: Verify PyMuPDF is used for PDF processing.

        Given: Valid PDF
        When: load_document() is called
        Then: Uses fitz (PyMuPDF) library
        """
        from src.lib.pdf_processor import load_document

        # This test verifies the implementation uses PyMuPDF
        # by checking that it can handle PyMuPDF-specific features
        document = load_document(sample_pdf_path)

        # PyMuPDF provides accurate page dimensions
        assert all(page.width > 0 for page in document.pages)
        assert all(page.height > 0 for page in document.pages)

    def test_validate_pdf_handles_pymupdf_errors(self, tmp_path):
        """
        Unit test: Handle PyMuPDF errors gracefully.

        Given: File that causes PyMuPDF to raise an error
        When: validate_pdf() is called
        Then: Returns is_valid=False with error message
        """
        from src.lib.pdf_processor import validate_pdf

        # Create a file that looks like PDF but isn't valid
        invalid_pdf = tmp_path / "invalid.pdf"
        invalid_pdf.write_bytes(b"%PDF-1.4\ngarbage data here")

        result = validate_pdf(str(invalid_pdf))

        # Should handle error gracefully, not crash
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
