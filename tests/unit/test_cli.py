"""
Unit tests for CLI components (formatter, logger, argument validation).

Tests individual CLI modules in isolation without full integration.

Test Strategy (TDD):
1. Write these tests FIRST
2. Verify they FAIL (no implementation yet)
3. Implement CLI modules
4. Verify tests PASS
"""

import pytest
import json
from unittest.mock import Mock, patch

from docscalpel.models import (
    ExtractionResult,
    Document,
    Element,
    ElementType,
    BoundingBox,
    create_element,
)


class TestJSONFormatter:
    """Test JSON output formatter."""

    def test_json_formatter_exists(self):
        """Verify JSON formatter is importable."""
        from docscalpel.cli.formatter import format_json
        assert callable(format_json)

    def test_format_json_with_success_result(self, sample_extraction_result):
        """
        Unit test: Format successful extraction as JSON.

        Given: ExtractionResult with success=True
        When: format_json() is called
        Then: Returns valid JSON string with all fields
        """
        from docscalpel.cli.formatter import format_json

        json_output = format_json(sample_extraction_result)

        # Verify: Valid JSON
        result = json.loads(json_output)

        # Verify: Required fields present
        assert 'success' in result
        assert result['success'] is True
        assert 'statistics' in result
        assert 'document' in result
        assert 'elements' in result

    def test_format_json_includes_statistics(self, sample_extraction_result):
        """
        Unit test: JSON output includes statistics.

        Given: ExtractionResult with elements
        When: format_json() is called
        Then: JSON includes figure_count, table_count, etc.
        """
        from docscalpel.cli.formatter import format_json

        json_output = format_json(sample_extraction_result)
        result = json.loads(json_output)

        stats = result['statistics']
        assert 'figure_count' in stats
        assert 'table_count' in stats
        assert 'equation_count' in stats
        assert 'total_elements' in stats
        assert 'extraction_time_seconds' in stats

    def test_format_json_includes_elements_list(self, sample_extraction_result):
        """
        Unit test: JSON output includes elements array.

        Given: ExtractionResult with elements
        When: format_json() is called
        Then: JSON includes elements array with details
        """
        from docscalpel.cli.formatter import format_json

        json_output = format_json(sample_extraction_result)
        result = json.loads(json_output)

        elements = result['elements']
        assert isinstance(elements, list)

        if len(elements) > 0:
            element = elements[0]
            assert 'element_type' in element
            assert 'output_filename' in element
            assert 'page_number' in element
            assert 'confidence_score' in element

    def test_format_json_with_errors(self, sample_document, temp_output_dir):
        """
        Unit test: JSON includes errors and warnings.

        Given: ExtractionResult with errors/warnings
        When: format_json() is called
        Then: JSON includes errors and warnings arrays
        """
        from docscalpel.cli.formatter import format_json

        result = ExtractionResult(
            document=sample_document,
            elements=[],
            output_directory=str(temp_output_dir),
            success=False,
            extraction_time_seconds=1.0,
            errors=['Error 1', 'Error 2'],
            warnings=['Warning 1']
        )

        json_output = format_json(result)
        parsed = json.loads(json_output)

        assert parsed['success'] is False
        assert len(parsed['errors']) == 2
        assert len(parsed['warnings']) == 1


class TestTextFormatter:
    """Test human-readable text output formatter."""

    def test_text_formatter_exists(self):
        """Verify text formatter is importable."""
        from docscalpel.cli.formatter import format_text
        assert callable(format_text)

    def test_format_text_with_success_result(self, sample_extraction_result):
        """
        Unit test: Format successful extraction as text.

        Given: ExtractionResult with success=True
        When: format_text() is called
        Then: Returns human-readable text summary
        """
        from docscalpel.cli.formatter import format_text

        text_output = format_text(sample_extraction_result)

        # Verify: Text output is non-empty
        assert len(text_output) > 0
        assert isinstance(text_output, str)

        # Verify: Contains key information
        assert 'success' in text_output.lower() or 'extracted' in text_output.lower()

    def test_format_text_includes_statistics(self, sample_extraction_result):
        """
        Unit test: Text output includes statistics.

        Given: ExtractionResult with elements
        When: format_text() is called
        Then: Text includes counts and timing
        """
        from docscalpel.cli.formatter import format_text

        text_output = format_text(sample_extraction_result)

        # Should mention element counts or totals
        assert 'figure' in text_output.lower() or 'element' in text_output.lower()

    def test_format_text_with_no_elements(self, sample_document, temp_output_dir):
        """
        Unit test: Text formatter handles no elements case.

        Given: ExtractionResult with no elements
        When: format_text() is called
        Then: Text clearly indicates no elements found
        """
        from docscalpel.cli.formatter import format_text

        result = ExtractionResult(
            document=sample_document,
            elements=[],
            output_directory=str(temp_output_dir),
            success=True,
            extraction_time_seconds=1.0,
            errors=[],
            warnings=[]
        )

        text_output = format_text(result)

        assert 'no' in text_output.lower() or '0' in text_output

    def test_format_text_with_errors(self, sample_document, temp_output_dir):
        """
        Unit test: Text formatter shows errors prominently.

        Given: ExtractionResult with errors
        When: format_text() is called
        Then: Text includes error messages
        """
        from docscalpel.cli.formatter import format_text

        result = ExtractionResult(
            document=sample_document,
            elements=[],
            output_directory=str(temp_output_dir),
            success=False,
            extraction_time_seconds=1.0,
            errors=['Critical error occurred'],
            warnings=['Minor warning']
        )

        text_output = format_text(result)

        assert 'error' in text_output.lower()
        assert 'Critical error occurred' in text_output


class TestLoggingConfiguration:
    """Test logging configuration module."""

    def test_logging_setup_exists(self):
        """Verify logging setup function is importable."""
        from docscalpel.cli.logger import setup_logging
        assert callable(setup_logging)

    def test_setup_logging_with_verbose_mode(self):
        """
        Unit test: Logging setup in verbose mode.

        Given: verbose=True
        When: setup_logging() is called
        Then: Logging level is set to DEBUG
        """
        from docscalpel.cli.logger import setup_logging
        import logging

        setup_logging(verbose=True)

        # Verify: Root logger level is DEBUG
        root_logger = logging.getLogger()
        assert root_logger.level <= logging.DEBUG

    def test_setup_logging_with_normal_mode(self):
        """
        Unit test: Logging setup in normal mode.

        Given: verbose=False
        When: setup_logging() is called
        Then: Logging level is set to INFO or WARNING
        """
        from docscalpel.cli.logger import setup_logging
        import logging

        setup_logging(verbose=False)

        # Verify: Root logger level is INFO or higher
        root_logger = logging.getLogger()
        assert root_logger.level >= logging.INFO

    def test_logging_outputs_to_stderr(self):
        """
        Unit test: Logging outputs to stderr, not stdout.

        Given: Logging is configured
        When: Log messages are written
        Then: They appear on stderr, not stdout
        """
        from docscalpel.cli.logger import setup_logging
        import logging
        import sys

        setup_logging(verbose=True)

        # Verify: Handlers write to stderr
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if hasattr(handler, 'stream'):
                assert handler.stream == sys.stderr or handler.stream.name == '<stderr>'


class TestArgumentParsing:
    """Test argument parser logic."""

    def test_parse_element_types_single(self):
        """
        Unit test: Parse single element type.

        Given: types_str = "figure"
        When: parse_element_types() is called
        Then: Returns [ElementType.FIGURE]
        """
        from docscalpel.cli.main import parse_element_types

        types = parse_element_types("figure")

        assert len(types) == 1
        assert types[0] == ElementType.FIGURE

    def test_parse_element_types_multiple(self):
        """
        Unit test: Parse multiple element types.

        Given: types_str = "figure,table,equation"
        When: parse_element_types() is called
        Then: Returns list with all three types
        """
        from docscalpel.cli.main import parse_element_types

        types = parse_element_types("figure,table,equation")

        assert len(types) == 3
        assert ElementType.FIGURE in types
        assert ElementType.TABLE in types
        assert ElementType.EQUATION in types

    def test_parse_element_types_with_spaces(self):
        """
        Unit test: Parse types with spaces.

        Given: types_str = "figure, table, equation"
        When: parse_element_types() is called
        Then: Handles spaces correctly
        """
        from docscalpel.cli.main import parse_element_types

        types = parse_element_types("figure, table, equation")

        assert len(types) == 3

    def test_parse_element_types_invalid_raises_error(self):
        """
        Unit test: Invalid element type raises error.

        Given: types_str = "invalid_type"
        When: parse_element_types() is called
        Then: Raises ValueError
        """
        from docscalpel.cli.main import parse_element_types

        with pytest.raises(ValueError):
            parse_element_types("invalid_type")

    def test_validate_confidence_threshold_valid(self):
        """
        Unit test: Validate valid confidence threshold.

        Given: confidence = 0.5
        When: validate_confidence() is called
        Then: Returns True
        """
        from docscalpel.cli.main import validate_confidence

        assert validate_confidence(0.5) is True
        assert validate_confidence(0.0) is True
        assert validate_confidence(1.0) is True

    def test_validate_confidence_threshold_invalid(self):
        """
        Unit test: Reject invalid confidence threshold.

        Given: confidence > 1.0 or < 0.0
        When: validate_confidence() is called
        Then: Returns False or raises error
        """
        from docscalpel.cli.main import validate_confidence

        assert validate_confidence(1.5) is False
        assert validate_confidence(-0.1) is False


class TestCLIExitCodes:
    """Test CLI exit code logic."""

    def test_success_exit_code_is_zero(self):
        """
        Unit test: Successful extraction returns exit code 0.

        Given: Extraction succeeds
        When: CLI finishes
        Then: Returns exit code 0
        """
        # This is tested in integration tests
        pass

    def test_failure_exit_code_is_nonzero(self):
        """
        Unit test: Failed extraction returns non-zero exit code.

        Given: Extraction fails
        When: CLI finishes
        Then: Returns non-zero exit code
        """
        # This is tested in integration tests
        pass
