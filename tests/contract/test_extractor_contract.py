"""
Contract tests for the extract_elements() public API.

These tests verify that the library's main interface adheres to its contract
as specified in contracts/library-interface.md.

Test Strategy (TDD):
1. Write these tests FIRST
2. Verify they FAIL (no implementation yet)
3. Implement the feature
4. Verify tests PASS
"""

import pytest
from pathlib import Path
from typing import List

from docscalpel.models import (
    ElementType,
    ExtractionConfig,
    ExtractionResult,
    PDFExtractorError,
    InvalidPDFError,
    ConfigurationError,
)


# These tests will fail until extract_elements() is implemented
# This is EXPECTED and CORRECT for TDD approach

class TestExtractElementsContract:
    """Test the extract_elements() function contract."""

    def test_extract_elements_function_exists(self):
        """Verify extract_elements() function is importable."""
        # This will fail until we implement the function
        from docscalpel.extractor import extract_elements
        assert callable(extract_elements)

    def test_extract_elements_with_valid_pdf_returns_result(
        self, sample_pdf_path, temp_output_dir, figure_only_config
    ):
        """
        CONTRACT: extract_elements() returns ExtractionResult for valid PDF.

        Given: A valid PDF file path and configuration
        When: extract_elements() is called
        Then: Returns ExtractionResult with success=True
        """
        from docscalpel.extractor import extract_elements

        # Update config to use temp directory
        figure_only_config.output_directory = str(temp_output_dir)

        result = extract_elements(sample_pdf_path, figure_only_config)

        # Contract assertions
        assert isinstance(result, ExtractionResult)
        assert result.success is True
        assert result.document is not None
        assert result.output_directory == str(temp_output_dir)
        assert result.extraction_time_seconds >= 0
        assert isinstance(result.elements, list)

    def test_extract_elements_with_default_config(
        self, sample_pdf_path, temp_output_dir
    ):
        """
        CONTRACT: extract_elements() works with default config.

        Given: Only a PDF path (no config)
        When: extract_elements() is called
        Then: Uses default configuration and succeeds
        """
        from docscalpel.extractor import extract_elements

        result = extract_elements(sample_pdf_path, None)

        assert isinstance(result, ExtractionResult)
        assert result.success is True

    def test_extract_elements_with_custom_config(self, sample_pdf_path, custom_config):
        """
        CONTRACT: extract_elements() respects custom configuration.

        Given: Custom ExtractionConfig with specific settings
        When: extract_elements() is called
        Then: Configuration is applied correctly
        """
        from docscalpel.extractor import extract_elements

        result = extract_elements(sample_pdf_path, custom_config)

        assert result.output_directory == custom_config.output_directory
        # Elements should respect confidence threshold
        for element in result.elements:
            assert element.confidence_score >= custom_config.confidence_threshold

    def test_extract_elements_creates_output_directory(
        self, sample_pdf_path, tmp_path
    ):
        """
        CONTRACT: extract_elements() creates output directory if missing.

        Given: Config with non-existent output directory
        When: extract_elements() is called
        Then: Directory is created automatically
        """
        from docscalpel.extractor import extract_elements

        output_dir = tmp_path / "new_output"
        assert not output_dir.exists()

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(output_dir)
        )

        result = extract_elements(sample_pdf_path, config)

        assert output_dir.exists()
        assert output_dir.is_dir()

    def test_extract_elements_with_invalid_pdf_raises_error(self, tmp_path):
        """
        CONTRACT: extract_elements() raises InvalidPDFError for invalid files.

        Given: A file that is not a valid PDF
        When: extract_elements() is called
        Then: Raises InvalidPDFError with clear message
        """
        from docscalpel.extractor import extract_elements

        # Create a non-PDF file
        invalid_file = tmp_path / "not_a_pdf.txt"
        invalid_file.write_text("This is not a PDF")

        config = ExtractionConfig(output_directory=str(tmp_path))

        with pytest.raises(InvalidPDFError) as exc_info:
            extract_elements(str(invalid_file), config)

        # Error message should be actionable
        assert "not a valid PDF" in str(exc_info.value).lower()

    def test_extract_elements_with_missing_file_raises_error(self, tmp_path):
        """
        CONTRACT: extract_elements() raises InvalidPDFError for missing files.

        Given: A file path that doesn't exist
        When: extract_elements() is called
        Then: Raises InvalidPDFError
        """
        from docscalpel.extractor import extract_elements

        missing_file = tmp_path / "does_not_exist.pdf"
        config = ExtractionConfig(output_directory=str(tmp_path))

        with pytest.raises(InvalidPDFError):
            extract_elements(str(missing_file), config)

    def test_extract_elements_with_invalid_config_raises_error(self, sample_pdf_path):
        """
        CONTRACT: extract_elements() validates configuration.

        Given: Invalid ExtractionConfig (e.g., empty element_types)
        When: extract_elements() is called
        Then: Raises ConfigurationError
        """
        from docscalpel.extractor import extract_elements

        # This should fail during config creation
        with pytest.raises(ConfigurationError):
            invalid_config = ExtractionConfig(element_types=[])

    def test_extract_elements_result_has_correct_structure(
        self, sample_pdf_path, temp_output_dir
    ):
        """
        CONTRACT: ExtractionResult has all required fields.

        Given: Successful extraction
        When: Result is returned
        Then: All contract fields are present and valid
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir)
        )

        result = extract_elements(sample_pdf_path, config)

        # Required fields per contract
        assert hasattr(result, 'document')
        assert hasattr(result, 'elements')
        assert hasattr(result, 'output_directory')
        assert hasattr(result, 'success')
        assert hasattr(result, 'extraction_time_seconds')
        assert hasattr(result, 'errors')
        assert hasattr(result, 'warnings')

        # Convenience properties per contract
        assert hasattr(result, 'figure_count')
        assert hasattr(result, 'table_count')
        assert hasattr(result, 'equation_count')
        assert hasattr(result, 'total_elements')

    def test_extract_elements_creates_pdf_files(
        self, sample_pdf_path, temp_output_dir, assert_file_exists
    ):
        """
        CONTRACT: extract_elements() creates individual PDF files.

        Given: PDF with extractable elements
        When: Extraction completes
        Then: Individual PDF files are created in output directory
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir)
        )

        result = extract_elements(sample_pdf_path, config)

        # Verify each element has corresponding output file
        for element in result.elements:
            output_path = Path(result.output_directory) / element.output_filename
            assert_file_exists(str(output_path))

    def test_extract_elements_with_no_elements_succeeds(
        self, text_only_pdf_path, temp_output_dir
    ):
        """
        CONTRACT: extract_elements() succeeds even when no elements found.

        Given: PDF with no figures/tables/equations
        When: extract_elements() is called
        Then: Returns success=True with empty elements list
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir)
        )

        result = extract_elements(text_only_pdf_path, config)

        assert result.success is True
        assert len(result.elements) == 0
        assert result.total_elements == 0

    def test_extract_elements_respects_confidence_threshold(
        self, sample_pdf_path, temp_output_dir
    ):
        """
        CONTRACT: extract_elements() filters by confidence threshold.

        Given: Config with high confidence threshold (e.g., 0.9)
        When: extract_elements() is called
        Then: Only high-confidence elements are returned
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir),
            confidence_threshold=0.9
        )

        result = extract_elements(sample_pdf_path, config)

        # All returned elements must meet threshold
        for element in result.elements:
            assert element.confidence_score >= 0.9

    def test_extract_elements_sequential_numbering(
        self, sample_pdf_path, temp_output_dir
    ):
        """
        CONTRACT: Elements are numbered sequentially by type.

        Given: PDF with multiple figures
        When: extract_elements() is called
        Then: Filenames use sequential numbering (figure_01, figure_02, etc.)
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir),
            naming_pattern="{type}_{counter:02d}.pdf"
        )

        result = extract_elements(sample_pdf_path, config)

        # Verify sequential numbering
        for i, element in enumerate(result.elements, start=1):
            assert element.sequence_number == i
            expected_name = f"figure_{i:02d}.pdf"
            assert element.output_filename == expected_name


class TestExtractElementsEdgeCases:
    """Test edge cases and error handling."""

    def test_extract_elements_with_encrypted_pdf_raises_error(self, tmp_path):
        """
        CONTRACT: Encrypted PDFs raise EncryptedPDFError.

        Given: Password-protected PDF
        When: extract_elements() is called
        Then: Raises EncryptedPDFError
        """
        from docscalpel.extractor import extract_elements
        from docscalpel.models import EncryptedPDFError

        # This test will be skipped if no encrypted PDF fixture exists
        pytest.skip("Encrypted PDF fixture not yet available")

    def test_extract_elements_with_corrupted_pdf_raises_error(self, tmp_path):
        """
        CONTRACT: Corrupted PDFs raise CorruptedPDFError.

        Given: Damaged/incomplete PDF file
        When: extract_elements() is called
        Then: Raises CorruptedPDFError
        """
        from docscalpel.extractor import extract_elements
        from docscalpel.models import CorruptedPDFError

        # Create a corrupted PDF (truncated content)
        corrupted_pdf = tmp_path / "corrupted.pdf"
        corrupted_pdf.write_bytes(b"%PDF-1.4\n%")  # Incomplete PDF header

        config = ExtractionConfig(output_directory=str(tmp_path))

        with pytest.raises((InvalidPDFError, CorruptedPDFError)):
            extract_elements(str(corrupted_pdf), config)

    def test_extract_elements_preserves_element_order(
        self, sample_pdf_path, temp_output_dir
    ):
        """
        CONTRACT: Elements are returned in page order.

        Given: PDF with elements on multiple pages
        When: extract_elements() is called
        Then: Elements are ordered by page_number, then by position
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir)
        )

        result = extract_elements(sample_pdf_path, config)

        # Verify elements are in page order
        for i in range(len(result.elements) - 1):
            current_page = result.elements[i].page_number
            next_page = result.elements[i + 1].page_number
            assert next_page >= current_page
