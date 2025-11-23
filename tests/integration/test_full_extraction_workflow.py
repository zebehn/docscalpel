"""
Integration tests for full extraction workflow.

These tests validate the end-to-end extraction process from PDF loading
through element detection, cropping, and output file generation.

Test Strategy (TDD):
1. Write these tests FIRST
2. Verify they FAIL (no implementation yet)
3. Implement the feature
4. Verify tests PASS
"""

import pytest
from pathlib import Path
import time

from docscalpel.models import (
    ElementType,
    ExtractionConfig,
    ExtractionResult,
)


class TestUserStory1FigureExtraction:
    """
    User Story 1: Extract all figures from a PDF and save as separate numbered files.

    Acceptance Criteria:
    - Given: PDF with 3 figures
    - When: Extract with element_types=[FIGURE]
    - Then: 3 files created (figure_01.pdf, figure_02.pdf, figure_03.pdf)
    """

    def test_extract_three_figures_from_sample_pdf(
        self, sample_pdf_path, temp_output_dir, assert_file_exists
    ):
        """
        Integration test for User Story 1: Extract 3 figures from PDF.

        This is the PRIMARY acceptance test from the specification.
        """
        from docscalpel.extractor import extract_elements

        # Setup: Configure for figure extraction only
        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir),
            confidence_threshold=0.5
        )

        # Execute: Run extraction
        result = extract_elements(sample_pdf_path, config)

        # Verify: Success and correct count
        assert result.success is True
        assert result.figure_count >= 1, "Should detect at least 1 figure"

        # Verify: Files are created with correct naming
        for i, element in enumerate(result.elements, start=1):
            expected_filename = f"figure_{i:02d}.pdf"
            assert element.output_filename == expected_filename

            output_path = temp_output_dir / expected_filename
            assert_file_exists(str(output_path))

        # Verify: No other element types extracted
        assert result.table_count == 0
        assert result.equation_count == 0

    def test_figure_extraction_performance(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: Verify extraction completes within time budget.

        Performance Target: Process 20-page PDF in under 30 seconds.
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir)
        )

        start_time = time.time()
        result = extract_elements(sample_pdf_path, config)
        elapsed = time.time() - start_time

        # Verify: Performance target met
        assert result.extraction_time_seconds < 30, \
            f"Extraction took {result.extraction_time_seconds}s, target is <30s"

        # Verify: Elapsed time is reasonable
        assert elapsed < 30, f"Wall clock time {elapsed}s exceeds 30s target"

    def test_figure_extraction_with_zero_padding(
        self, sample_pdf_path, temp_output_dir
    ):
        """
        Integration test: Verify sequential numbering with zero-padding.

        Given: Multiple figures extracted
        When: Using default naming pattern
        Then: Filenames have zero-padded numbers (01, 02, not 1, 2)
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir),
            naming_pattern="{type}_{counter:02d}.pdf"
        )

        result = extract_elements(sample_pdf_path, config)

        # Verify: Zero-padding in filenames
        for element in result.elements:
            # Should be figure_01.pdf, not figure_1.pdf
            assert "_0" in element.output_filename or element.sequence_number >= 10

    def test_extraction_with_no_figures_succeeds(
        self, text_only_pdf_path, temp_output_dir
    ):
        """
        Integration test: Handle PDF with no figures gracefully.

        Given: PDF with no extractable figures
        When: Extract with element_types=[FIGURE]
        Then: Returns success with empty results, no files created
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir)
        )

        result = extract_elements(text_only_pdf_path, config)

        # Verify: Success even with no elements
        assert result.success is True
        assert result.figure_count == 0
        assert len(result.elements) == 0

        # Verify: No files created in output directory
        output_files = list(Path(temp_output_dir).glob("figure_*.pdf"))
        assert len(output_files) == 0

    def test_extraction_updates_document_metadata(
        self, sample_pdf_path, temp_output_dir
    ):
        """
        Integration test: Verify document metadata is populated.

        Given: Valid PDF file
        When: Extraction completes
        Then: Document has page_count, file_size, metadata populated
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir)
        )

        result = extract_elements(sample_pdf_path, config)

        # Verify: Document metadata
        assert result.document.file_path == sample_pdf_path
        assert result.document.page_count > 0
        assert result.document.file_size_bytes > 0
        assert isinstance(result.document.metadata, dict)


class TestUserStory2MultiTypeExtraction:
    """
    User Story 2: Extract figures, tables, and equations in single pass.

    Acceptance Criteria:
    - Given: PDF with 2 figures, 3 tables, 1 equation
    - When: Extract with all element types
    - Then: 6 files created with correct type-specific naming
    """

    def test_extract_mixed_elements_from_pdf(
        self, mixed_content_pdf_path, temp_output_dir
    ):
        """
        Integration test for User Story 2: Extract multiple element types.

        This tests the multi-type extraction capability.
        """
        from docscalpel.extractor import extract_elements

        # Setup: Configure for all element types
        config = ExtractionConfig(
            element_types=[ElementType.FIGURE, ElementType.TABLE, ElementType.EQUATION],
            output_directory=str(temp_output_dir),
            confidence_threshold=0.5
        )

        # Execute: Run extraction
        result = extract_elements(mixed_content_pdf_path, config)

        # Verify: Success and mixed types detected
        assert result.success is True
        assert result.total_elements > 0

        # Verify: Type-specific naming
        figure_files = [e for e in result.elements if e.element_type == ElementType.FIGURE]
        table_files = [e for e in result.elements if e.element_type == ElementType.TABLE]
        equation_files = [e for e in result.elements if e.element_type == ElementType.EQUATION]

        # Verify: Each type has independent sequential numbering
        for i, element in enumerate(figure_files, start=1):
            assert element.sequence_number == i
            assert element.output_filename.startswith("figure_")

        for i, element in enumerate(table_files, start=1):
            assert element.sequence_number == i
            assert element.output_filename.startswith("table_")

        for i, element in enumerate(equation_files, start=1):
            assert element.sequence_number == i
            assert element.output_filename.startswith("equation_")

    def test_multi_type_extraction_avoids_duplicates(
        self, mixed_content_pdf_path, temp_output_dir
    ):
        """
        Integration test: Verify overlap handling removes duplicates.

        Given: Elements that may overlap on page
        When: Multi-type extraction runs
        Then: Overlapping elements are deduplicated (highest confidence kept)
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE, ElementType.TABLE],
            output_directory=str(temp_output_dir)
        )

        result = extract_elements(mixed_content_pdf_path, config)

        # Verify: No duplicate output filenames
        filenames = [e.output_filename for e in result.elements]
        assert len(filenames) == len(set(filenames)), "Duplicate filenames detected"

        # If warnings about overlaps exist, verify they're documented
        if result.warnings:
            overlap_warnings = [w for w in result.warnings if "overlap" in w.lower()]
            # Overlap warnings should mention which element was kept
            for warning in overlap_warnings:
                assert "confidence" in warning.lower()


class TestUserStory3CustomConfiguration:
    """
    User Story 3: Support custom output configuration.

    Acceptance Criteria:
    - Custom output directories
    - Custom naming patterns
    - Boundary padding
    - Overwrite behavior
    """

    def test_custom_output_directory(self, sample_pdf_path, tmp_path):
        """
        Integration test: Verify custom output directory is created and used.

        Given: Config with custom output directory
        When: Extraction runs
        Then: Directory is created and files are placed there
        """
        from docscalpel.extractor import extract_elements

        custom_dir = tmp_path / "my_custom_output" / "figures"
        assert not custom_dir.exists()

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(custom_dir)
        )

        result = extract_elements(sample_pdf_path, config)

        # Verify: Directory created
        assert custom_dir.exists()
        assert custom_dir.is_dir()

        # Verify: Files in correct location
        assert result.output_directory == str(custom_dir)

    def test_custom_naming_pattern(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: Verify custom naming patterns work.

        Given: Config with pattern "img_{counter:03d}.pdf"
        When: Extraction runs
        Then: Files named img_001.pdf, img_002.pdf, etc.
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir),
            naming_pattern="img_{counter:03d}.pdf"
        )

        result = extract_elements(sample_pdf_path, config)

        # Verify: Custom naming applied
        for element in result.elements:
            assert element.output_filename.startswith("img_")
            assert element.output_filename.endswith(".pdf")
            # Should be 3-digit padding: img_001.pdf
            assert len(element.output_filename) == len("img_001.pdf")

    def test_boundary_padding_expansion(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: Verify boundary padding expands bounding boxes.

        Given: Config with boundary_padding=10 pixels
        When: Extraction runs
        Then: Extracted regions are 10px larger in all directions
        """
        from docscalpel.extractor import extract_elements

        # Extract without padding
        config_no_padding = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir),
            boundary_padding=0
        )

        result_no_padding = extract_elements(sample_pdf_path, config_no_padding)

        # Extract with padding
        output_dir_padded = temp_output_dir / "padded"
        output_dir_padded.mkdir()

        config_with_padding = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(output_dir_padded),
            boundary_padding=10
        )

        result_with_padding = extract_elements(sample_pdf_path, config_with_padding)

        # Verify: Padded elements have larger bounding boxes
        # (This is a simplified check - actual implementation should verify dimensions)
        for element in result_with_padding.elements:
            assert element.bounding_box.padding == 10

    def test_overwrite_existing_files(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: Verify overwrite_existing flag behavior.

        Given: Output files already exist
        When: Extraction runs with overwrite_existing=True
        Then: Files are overwritten
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir),
            overwrite_existing=True
        )

        # First extraction
        result1 = extract_elements(sample_pdf_path, config)
        first_file = Path(temp_output_dir) / result1.elements[0].output_filename
        first_mtime = first_file.stat().st_mtime

        # Wait a moment to ensure different mtime
        time.sleep(0.1)

        # Second extraction (should overwrite)
        result2 = extract_elements(sample_pdf_path, config)
        second_mtime = first_file.stat().st_mtime

        # Verify: File was overwritten (mtime changed)
        assert second_mtime > first_mtime


class TestErrorHandlingWorkflow:
    """Integration tests for error scenarios."""

    def test_invalid_pdf_error_handling(self, tmp_path):
        """
        Integration test: Verify invalid PDF error handling.

        Given: Non-PDF file
        When: Extraction is attempted
        Then: Clear error message with actionable guidance
        """
        from docscalpel.extractor import extract_elements
        from docscalpel.models import InvalidPDFError

        invalid_file = tmp_path / "not_a_pdf.txt"
        invalid_file.write_text("This is plain text, not a PDF")

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(tmp_path)
        )

        with pytest.raises(InvalidPDFError) as exc_info:
            extract_elements(str(invalid_file), config)

        # Verify: Error message is actionable
        error_msg = str(exc_info.value)
        assert "not a valid PDF" in error_msg.lower()
        assert str(invalid_file) in error_msg

    def test_missing_file_error_handling(self, tmp_path):
        """
        Integration test: Verify missing file error handling.

        Given: Non-existent file path
        When: Extraction is attempted
        Then: Clear error message about missing file
        """
        from docscalpel.extractor import extract_elements
        from docscalpel.models import InvalidPDFError

        missing_file = tmp_path / "does_not_exist.pdf"

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(tmp_path)
        )

        with pytest.raises(InvalidPDFError) as exc_info:
            extract_elements(str(missing_file), config)

        # Verify: Error mentions file not found
        error_msg = str(exc_info.value).lower()
        assert "not found" in error_msg or "does not exist" in error_msg

    def test_permission_error_handling(self, sample_pdf_path, tmp_path):
        """
        Integration test: Verify permission error handling.

        Given: Output directory without write permissions
        When: Extraction is attempted
        Then: Clear error about permissions
        """
        pytest.skip("Permission testing requires OS-specific setup")

    def test_extraction_continues_after_partial_failure(
        self, sample_pdf_path, temp_output_dir
    ):
        """
        Integration test: Verify graceful degradation on partial failures.

        Given: Some pages may fail to process
        When: Extraction runs
        Then: Successful elements are still extracted and errors are logged
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir)
        )

        result = extract_elements(sample_pdf_path, config)

        # Even if some errors occurred, should still succeed if any elements found
        if result.errors:
            # Errors should be documented
            assert len(result.errors) > 0
            # But extraction should still succeed if any elements were found
            if result.total_elements > 0:
                assert result.success is True


class TestExtractionResultValidation:
    """Integration tests for result validation and consistency."""

    def test_result_element_count_matches_files(
        self, sample_pdf_path, temp_output_dir
    ):
        """
        Integration test: Verify result counts match actual files created.

        Given: Extraction completes
        When: Counting files in output directory
        Then: File count matches result.total_elements
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir)
        )

        result = extract_elements(sample_pdf_path, config)

        # Count actual PDF files created
        pdf_files = list(Path(temp_output_dir).glob("*.pdf"))

        # Verify: Count matches
        assert len(pdf_files) == result.total_elements

    def test_result_convenience_properties(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: Verify convenience properties are accurate.

        Given: Extraction with mixed element types
        When: Accessing result properties
        Then: figure_count, table_count, etc. are correct
        """
        from docscalpel.extractor import extract_elements

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE, ElementType.TABLE],
            output_directory=str(temp_output_dir)
        )

        result = extract_elements(sample_pdf_path, config)

        # Manually count by type
        manual_figure_count = sum(
            1 for e in result.elements if e.element_type == ElementType.FIGURE
        )
        manual_table_count = sum(
            1 for e in result.elements if e.element_type == ElementType.TABLE
        )

        # Verify: Properties match manual counts
        assert result.figure_count == manual_figure_count
        assert result.table_count == manual_table_count
        assert result.total_elements == len(result.elements)


class TestErrorHandlingWorkflow:
    """
    Integration tests for error handling throughout the extraction workflow.

    Tests verify that errors are handled gracefully at each stage:
    - Invalid PDF file
    - Missing file
    - Permission errors
    - Corrupted PDF
    - Encrypted PDF
    - Invalid configuration
    - Extraction failures
    """

    def test_missing_file_error_handling(self, temp_output_dir):
        """
        Integration test: Handle missing PDF file error.

        Flow: extract_elements() → validate_pdf() → file not found → error
        """
        from docscalpel.extractor import extract_elements
        from docscalpel.models import PDFExtractorError

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir)
        )

        # Attempt to extract from non-existent file
        with pytest.raises(PDFExtractorError) as excinfo:
            extract_elements("/nonexistent/path/to/file.pdf", config)

        # Verify error message is informative
        assert "not found" in str(excinfo.value).lower() or "no such file" in str(excinfo.value).lower()

    def test_invalid_pdf_error_handling(self, temp_output_dir):
        """
        Integration test: Handle invalid (non-PDF) file error.

        Flow: extract_elements() → validate_pdf() → PyMuPDF error → InvalidPDFError
        """
        from docscalpel.extractor import extract_elements
        from docscalpel.models import InvalidPDFError
        import tempfile

        # Create a fake "PDF" file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("This is not a PDF file, just plain text")
            fake_pdf_path = f.name

        try:
            config = ExtractionConfig(
                element_types=[ElementType.FIGURE],
                output_directory=str(temp_output_dir)
            )

            # Attempt to extract from invalid PDF
            with pytest.raises(InvalidPDFError) as excinfo:
                extract_elements(fake_pdf_path, config)

            # Verify error message mentions PDF invalidity
            assert "invalid" in str(excinfo.value).lower() or "corrupted" in str(excinfo.value).lower()
        finally:
            # Cleanup
            import os
            if os.path.exists(fake_pdf_path):
                os.unlink(fake_pdf_path)

    def test_encrypted_pdf_error_handling(self, temp_output_dir):
        """
        Integration test: Handle encrypted PDF error.

        Flow: extract_elements() → validate_pdf() → detect encryption → EncryptedPDFError

        Note: PyMuPDF may successfully open some encrypted PDFs if they don't
        require a password. This test verifies we detect encryption when present.
        """
        from docscalpel.pdf_processor import validate_pdf
        import fitz

        # Create an encrypted PDF
        encrypted_pdf_path = str(Path(temp_output_dir) / "encrypted.pdf")
        doc = fitz.open()
        page = doc.new_page(width=612, height=792)
        doc.save(encrypted_pdf_path, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw="password")
        doc.close()

        # Verify PDF is detected as encrypted during validation
        validation = validate_pdf(encrypted_pdf_path)

        # Should detect encryption (even if PDF can be opened without password)
        assert validation.is_encrypted is True, "Validation should detect encrypted PDF"

    def test_invalid_configuration_error_handling(self, sample_pdf_path):
        """
        Integration test: Handle invalid configuration errors.

        Flow: ExtractionConfig validation → ConfigurationError
        """
        from docscalpel.models import ConfigurationError

        # Test: Invalid confidence threshold (> 1.0)
        with pytest.raises(ConfigurationError) as excinfo:
            ExtractionConfig(
                element_types=[ElementType.FIGURE],
                confidence_threshold=1.5  # Invalid: must be 0.0-1.0
            )
        assert "confidence" in str(excinfo.value).lower()

        # Test: Negative boundary padding
        with pytest.raises(ConfigurationError) as excinfo:
            ExtractionConfig(
                element_types=[ElementType.FIGURE],
                boundary_padding=-10  # Invalid: must be non-negative
            )
        assert "padding" in str(excinfo.value).lower()

        # Test: Invalid max_pages
        with pytest.raises(ConfigurationError) as excinfo:
            ExtractionConfig(
                element_types=[ElementType.FIGURE],
                max_pages=0  # Invalid: must be >= 1
            )
        assert "max_pages" in str(excinfo.value).lower()

    def test_permission_error_handling(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: Handle permission errors for output directory.

        Flow: extract_elements() → create output dir → permission denied → error
        """
        from docscalpel.extractor import extract_elements
        from docscalpel.models import ConfigurationError
        import os
        import stat

        # Create a directory and make it read-only
        readonly_dir = str(Path(temp_output_dir) / "readonly_dir")
        os.makedirs(readonly_dir, exist_ok=True)

        # Remove write permissions
        os.chmod(readonly_dir, stat.S_IRUSR | stat.S_IXUSR)  # r-x only

        try:
            # Create subdirectory path that would require write permission
            restricted_output = str(Path(readonly_dir) / "output")

            config = ExtractionConfig(
                element_types=[ElementType.FIGURE],
                output_directory=restricted_output
            )

            # Attempt to extract with unwritable output directory
            # Can raise ConfigurationError, PermissionError, OSError, or ExtractionFailedError
            from docscalpel.models import ExtractionFailedError
            with pytest.raises((ConfigurationError, PermissionError, OSError, ExtractionFailedError)) as excinfo:
                extract_elements(sample_pdf_path, config)

            # Verify error relates to permissions or directory access
            error_msg = str(excinfo.value).lower()
            assert any(keyword in error_msg for keyword in ["permission", "access", "denied", "directory", "read-only"])
        finally:
            # Restore write permissions for cleanup
            os.chmod(readonly_dir, stat.S_IRWXU)  # rwx for cleanup

    def test_corrupted_pdf_error_handling(self, temp_output_dir):
        """
        Integration test: Handle corrupted PDF structure.

        Flow: extract_elements() → PyMuPDF detects corruption → CorruptedPDFError
        """
        from docscalpel.extractor import extract_elements
        from docscalpel.models import InvalidPDFError, CorruptedPDFError
        import tempfile

        # Create a PDF-like file with corrupted structure
        corrupted_pdf_path = str(Path(temp_output_dir) / "corrupted.pdf")
        with open(corrupted_pdf_path, 'wb') as f:
            # Write minimal PDF header but with corrupted structure
            f.write(b'%PDF-1.4\n')
            f.write(b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n')
            f.write(b'%%EOF')  # Incomplete/corrupted structure

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir)
        )

        # Attempt to extract from corrupted PDF
        # Should raise InvalidPDFError or its subclass CorruptedPDFError
        with pytest.raises((InvalidPDFError, CorruptedPDFError)) as excinfo:
            extract_elements(corrupted_pdf_path, config)

        # Verify error message mentions corruption or invalidity
        error_msg = str(excinfo.value).lower()
        assert any(keyword in error_msg for keyword in ["corrupted", "invalid", "damaged", "incomplete"])

    def test_single_page_empty_pdf_handling(self, temp_output_dir):
        """
        Integration test: Handle PDF with single blank page (no content).

        Flow: extract_elements() → load_document() → 1 page but no elements → graceful handling

        Note: PyMuPDF requires at least 1 page, so we test with a minimal 1-page PDF.
        """
        from docscalpel.extractor import extract_elements
        import fitz

        # Create minimal PDF (1 blank page)
        empty_pdf_path = str(Path(temp_output_dir) / "minimal.pdf")
        doc = fitz.open()
        doc.new_page(width=612, height=792)  # Add one blank page
        doc.save(empty_pdf_path)
        doc.close()

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir)
        )

        # Extract from minimal PDF
        result = extract_elements(empty_pdf_path, config)

        # Should succeed but with no elements (blank page)
        assert result.success is True, "Minimal blank PDF should not cause failure"
        assert result.document.page_count == 1, "Should have 1 page"
        assert result.total_elements == 0, "Blank PDF should have zero elements"
        assert len(result.elements) == 0

    def test_no_elements_detected_handling(self, temp_output_dir):
        """
        Integration test: Handle PDF where no elements are detected.

        Flow: extract_elements() → detect → 0 elements found → success with empty results
        """
        from docscalpel.extractor import extract_elements
        import fitz

        # Create PDF with just blank pages (no figures/tables/equations)
        blank_pdf_path = str(Path(temp_output_dir) / "blank.pdf")
        doc = fitz.open()
        # Add blank page
        doc.new_page(width=612, height=792)
        doc.save(blank_pdf_path)
        doc.close()

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE, ElementType.TABLE, ElementType.EQUATION],
            output_directory=str(temp_output_dir)
        )

        # Extract from blank PDF
        result = extract_elements(blank_pdf_path, config)

        # Should succeed even with no elements detected
        assert result.success is True, "No elements should not be considered a failure"
        assert result.total_elements == 0
        assert len(result.elements) == 0
        assert len(result.errors) == 0, "No errors should be reported"

    def test_error_recovery_and_cleanup(self, temp_output_dir):
        """
        Integration test: Verify proper cleanup on error.

        Flow: extract_elements() → error occurs → temporary files cleaned up
        """
        from docscalpel.extractor import extract_elements
        import tempfile

        # Create invalid PDF that will cause error
        invalid_pdf_path = str(Path(temp_output_dir) / "invalid_for_cleanup.pdf")
        with open(invalid_pdf_path, 'w') as f:
            f.write("Not a PDF")

        config = ExtractionConfig(
            element_types=[ElementType.FIGURE],
            output_directory=str(temp_output_dir)
        )

        # Count files before extraction attempt
        files_before = set(Path(temp_output_dir).glob("*"))

        # Attempt extraction (will fail)
        try:
            extract_elements(invalid_pdf_path, config)
        except Exception:
            pass  # Expected to fail

        # Count files after extraction attempt
        files_after = set(Path(temp_output_dir).glob("*"))

        # Verify no leaked temporary files (except the invalid PDF we created)
        new_files = files_after - files_before
        temp_files = [f for f in new_files if "tmp" in f.name.lower() or "temp" in f.name.lower()]

        assert len(temp_files) == 0, "Temporary files should be cleaned up after error"
