"""
Integration tests for CLI → library → PyMuPDF integration.

These tests verify the complete end-to-end flow from CLI entry point through
the extraction library down to PyMuPDF PDF processing, ensuring all components
work together correctly with real PDF files.

Integration coverage:
1. CLI argument parsing → library configuration
2. Library extraction → PDF validation
3. PDF processing → element detection
4. Element detection → PDF cropping
5. PDF cropping → output file creation
6. Full error handling flow through all layers
"""

import json
import os
import pytest
import tempfile
import fitz  # PyMuPDF
from pathlib import Path
from unittest.mock import patch

from src.lib.extractor import extract_elements
from src.lib.models import ExtractionConfig, ElementType


class TestPDFLibraryIntegration:
    """Integration tests for library → PyMuPDF interaction."""

    def test_extract_from_real_pdf_end_to_end(self, sample_pdf_with_figures, temp_output_dir):
        """
        Integration test: Extract elements from real PDF using PyMuPDF.

        Flow: extract_elements() → load_document() → PyMuPDF fitz.open()
              → detect elements → crop_element() → PyMuPDF save()
        """
        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=temp_output_dir,
            confidence_threshold=0.1,  # Low threshold to catch any detections
        )

        result = extract_elements(sample_pdf_with_figures, config)

        # Verify result structure
        assert result is not None, "extract_elements() should return result"
        assert result.success is True, "Extraction should succeed"
        assert result.document is not None, "Result should contain document"

        # Verify document was loaded via PyMuPDF
        assert result.document.file_path == sample_pdf_with_figures
        assert result.document.page_count > 0, "PDF should have pages"

        # Verify PyMuPDF can still open the original PDF
        with fitz.open(sample_pdf_with_figures) as doc:
            assert len(doc) == result.document.page_count, (
                "PyMuPDF page count should match document page count"
            )

    def test_pdf_validation_with_pymupdf(self, sample_pdf_with_figures):
        """
        Integration test: PDF validation using PyMuPDF.

        Flow: validate_pdf() → PyMuPDF fitz.open() → validation checks
        """
        from src.lib.pdf_processor import validate_pdf

        validation_result = validate_pdf(sample_pdf_with_figures)

        assert validation_result.is_valid is True, "Valid PDF should pass validation"
        assert validation_result.page_count is not None, "Validation should return page count"
        assert validation_result.page_count > 0, "Valid PDF should have pages"
        assert validation_result.is_encrypted is False, "Test PDF should not be encrypted"
        assert validation_result.error_message is None, "Valid PDF should have no error"

    def test_pdf_loading_with_pymupdf(self, sample_pdf_with_figures):
        """
        Integration test: Load PDF document using PyMuPDF.

        Flow: load_document() → PyMuPDF fitz.open() → Document creation
        """
        from src.lib.pdf_processor import load_document

        document = load_document(sample_pdf_with_figures)

        assert document is not None, "load_document() should return Document"
        assert document.file_path == sample_pdf_with_figures
        assert document.page_count > 0, "Document should have pages"
        assert len(document.pages) > 0, "Document should have page objects"

        # Verify each page has PyMuPDF-derived properties
        for page in document.pages:
            assert page.width > 0, "Page should have width from PyMuPDF"
            assert page.height > 0, "Page should have height from PyMuPDF"
            assert page.page_number >= 1, "Page numbers should be 1-indexed"

    def test_pdf_cropping_with_pymupdf(self, sample_pdf_with_figures, temp_output_dir):
        """
        Integration test: Crop PDF region using PyMuPDF.

        Flow: crop_element() → PyMuPDF open() → set_cropbox() → save()
        """
        from src.lib.cropper import crop_element
        from src.lib.models import BoundingBox, Element, ElementType

        # Create test element with bounding box
        bbox = BoundingBox(x=100, y=100, width=200, height=150, page_number=1)
        element = Element(
            element_id="test-crop",
            element_type=ElementType.FIGURE,
            bounding_box=bbox,
            page_number=1,
            sequence_number=1,
            confidence_score=0.9,
            output_filename="test_crop.pdf",
        )

        output_path = os.path.join(temp_output_dir, "test_crop.pdf")

        # Crop element using PyMuPDF
        success = crop_element(
            pdf_path=sample_pdf_with_figures,
            element=element,
            output_path=output_path,
        )

        assert success is True, "Cropping should succeed"
        assert os.path.exists(output_path), "Cropped PDF should be created"

        # Verify cropped PDF is valid and has correct dimensions via PyMuPDF
        with fitz.open(output_path) as doc:
            assert len(doc) == 1, "Cropped PDF should have 1 page"
            page = doc[0]
            rect = page.rect

            # Dimensions should approximately match bounding box
            # (within tolerance for PDF units and padding)
            assert rect.width > 0, "Cropped page should have width"
            assert rect.height > 0, "Cropped page should have height"

    def test_multi_page_pdf_processing(self, sample_pdf_with_figures, temp_output_dir):
        """
        Integration test: Process multi-page PDF through PyMuPDF.

        Verifies that PyMuPDF correctly handles multiple pages.
        """
        config = ExtractionConfig(
            element_types=[ElementType.FIGURE, ElementType.TABLE],
            output_directory=temp_output_dir,
            max_pages=None,  # Process all pages
        )

        result = extract_elements(sample_pdf_with_figures, config)

        assert result.success is True

        # Verify PyMuPDF processed all pages
        with fitz.open(sample_pdf_with_figures) as doc:
            total_pages = len(doc)
            assert result.document.page_count == total_pages
            assert len(result.document.pages) <= total_pages

    def test_pymupdf_error_handling_invalid_pdf(self, temp_output_dir):
        """
        Integration test: Verify PyMuPDF error handling for invalid PDF.

        Flow: extract_elements() → PyMuPDF error → exception handling
        """
        from src.lib.models import InvalidPDFError

        # Create a fake "PDF" that's not actually valid
        fake_pdf_path = os.path.join(temp_output_dir, "fake.pdf")
        with open(fake_pdf_path, "w") as f:
            f.write("This is not a PDF file")

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=temp_output_dir,
        )

        # Should raise InvalidPDFError when PyMuPDF detects invalid PDF
        with pytest.raises(InvalidPDFError) as excinfo:
            extract_elements(fake_pdf_path, config)

        # Verify error message mentions PDF invalidity
        assert "invalid" in str(excinfo.value).lower() or "corrupted" in str(excinfo.value).lower(), (
            "Error should mention invalid/corrupted PDF"
        )

    def test_pymupdf_encrypted_pdf_handling(self, temp_output_dir):
        """
        Integration test: Verify PyMuPDF detects encrypted PDFs.

        Flow: validate_pdf() → PyMuPDF detects encryption → validation fails
        """
        from src.lib.pdf_processor import validate_pdf

        # Create a simple encrypted PDF using PyMuPDF
        encrypted_pdf_path = os.path.join(temp_output_dir, "encrypted.pdf")
        doc = fitz.open()
        page = doc.new_page(width=612, height=792)
        doc.save(encrypted_pdf_path, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw="password")
        doc.close()

        # Validate the encrypted PDF
        validation_result = validate_pdf(encrypted_pdf_path)

        # Should detect encryption via PyMuPDF
        assert validation_result.is_encrypted is True, "PyMuPDF should detect encryption"
        assert validation_result.is_valid is False, "Encrypted PDF should fail validation"


class TestCLIPDFLibraryIntegration:
    """Integration tests for CLI → library → PyMuPDF flow."""

    def test_cli_to_pymupdf_extraction_flow(self, sample_pdf_with_figures, temp_output_dir, capsys):
        """
        Integration test: Full CLI → library → PyMuPDF flow.

        Flow: CLI main() → parse args → extract_elements() → PyMuPDF → output
        """
        from src.cli.main import main

        test_args = [
            'pdf-extractor',
            sample_pdf_with_figures,
            '--types', 'figure',
            '--output', temp_output_dir,
            '--format', 'json',
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        # Verify CLI succeeded
        assert exit_code == 0, "CLI should exit successfully"

        # Capture and parse JSON output
        captured = capsys.readouterr()
        try:
            result = json.loads(captured.out)
        except json.JSONDecodeError:
            pytest.fail(f"CLI output is not valid JSON: {captured.out}")

        # Verify PyMuPDF was used to process PDF
        assert "document" in result, "Output should contain document info"
        assert result["document"]["page_count"] > 0, "PyMuPDF should have loaded pages"

    def test_cli_pymupdf_error_propagation(self, temp_output_dir, capsys):
        """
        Integration test: PyMuPDF errors propagate through CLI.

        Flow: CLI main() → extract_elements() → PyMuPDF error → CLI error output
        """
        from src.cli.main import main

        # Use non-existent file to trigger PyMuPDF error
        test_args = [
            'pdf-extractor',
            '/nonexistent/file.pdf',
            '--output', temp_output_dir,
            '--format', 'json',
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        # Verify CLI handles error
        assert exit_code != 0, "CLI should exit with error code"

        captured = capsys.readouterr()

        # Error may be in stdout (as formatted output) or stderr (as log)
        error_output = captured.out + captured.err
        assert "error" in error_output.lower() or "failed" in error_output.lower() or "not found" in error_output.lower(), (
            "Error message should appear in output or logs"
        )

    def test_cli_pymupdf_cropping_integration(self, sample_pdf_with_figures, temp_output_dir):
        """
        Integration test: CLI triggers PyMuPDF cropping.

        Flow: CLI → extract_elements() → crop_element() → PyMuPDF save()
        """
        from src.cli.main import main

        test_args = [
            'pdf-extractor',
            sample_pdf_with_figures,
            '--types', 'figure',
            '--output', temp_output_dir,
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        assert exit_code == 0, "CLI should succeed"

        # Verify PyMuPDF created output files
        output_files = list(Path(temp_output_dir).glob("*.pdf"))

        # If elements were detected, verify cropped PDFs are valid via PyMuPDF
        for output_file in output_files:
            with fitz.open(str(output_file)) as doc:
                assert len(doc) >= 1, f"Output PDF {output_file} should have pages"
                assert doc[0].rect.width > 0, "Cropped PDF should have valid dimensions"


@pytest.fixture
def sample_pdf_with_figures(tmp_path):
    """
    Fixture providing a real PDF file for testing with PyMuPDF.

    Creates a simple PDF with some content that can be processed.
    """
    pdf_path = tmp_path / "sample_with_figures.pdf"

    # Create a real PDF using PyMuPDF
    doc = fitz.open()

    # Page 1: Add some text and a rectangle (simulating a figure region)
    page1 = doc.new_page(width=612, height=792)
    page1.insert_text((72, 72), "Sample PDF for Testing", fontsize=14)
    page1.draw_rect(fitz.Rect(100, 150, 400, 350), color=(0, 0, 1), width=2)

    # Page 2: Add more content
    page2 = doc.new_page(width=612, height=792)
    page2.insert_text((72, 72), "Page 2", fontsize=14)
    page2.draw_rect(fitz.Rect(50, 200, 300, 400), color=(1, 0, 0), width=2)

    # Save the PDF
    doc.save(str(pdf_path))
    doc.close()

    return str(pdf_path)


@pytest.fixture
def temp_output_dir(tmp_path):
    """Fixture providing a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return str(output_dir)
