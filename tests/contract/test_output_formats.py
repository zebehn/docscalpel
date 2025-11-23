"""
Contract tests for CLI output formats.

These tests validate that JSON and text output formats match the documented
specification in CLI_MANUAL.md. They serve as executable documentation of
the output format contract.

Contract guarantees:
1. JSON output follows documented schema (success, statistics, elements, errors, warnings)
2. Text output has consistent structure (status line, statistics section, output section)
3. Field names and types match specification
4. Required fields are always present
5. Output is parseable and machine-readable (JSON) or human-readable (text)
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any

from src.lib.models import (
    ExtractionResult,
    ExtractionConfig,
    Element,
    ElementType,
    BoundingBox,
)
from src.cli.formatter import format_json, format_text


class TestJSONOutputContract:
    """Contract tests for JSON output format."""

    def test_json_output_schema_success_case(self, sample_extraction_result):
        """
        Contract: JSON output for successful extraction must contain:
        - success: boolean
        - statistics: object with counts and timing
        - elements: array of element objects
        - errors: array (empty on success)
        - warnings: array (possibly empty)
        """
        json_output = format_json(sample_extraction_result)
        result = json.loads(json_output)

        # Top-level structure
        assert "success" in result, "JSON must contain 'success' field"
        assert isinstance(result["success"], bool), "'success' must be boolean"
        assert result["success"] is True, "Success case must have success=true"

        assert "statistics" in result, "JSON must contain 'statistics' field"
        assert isinstance(result["statistics"], dict), "'statistics' must be object"

        assert "elements" in result, "JSON must contain 'elements' field"
        assert isinstance(result["elements"], list), "'elements' must be array"

        assert "errors" in result, "JSON must contain 'errors' field"
        assert isinstance(result["errors"], list), "'errors' must be array"

        assert "warnings" in result, "JSON must contain 'warnings' field"
        assert isinstance(result["warnings"], list), "'warnings' must be array"

    def test_json_statistics_schema(self, sample_extraction_result):
        """
        Contract: statistics object must contain:
        - total_elements: integer
        - figure_count: integer
        - table_count: integer
        - equation_count: integer
        - extraction_time_seconds: number
        """
        json_output = format_json(sample_extraction_result)
        result = json.loads(json_output)
        stats = result["statistics"]

        # Required fields
        assert "total_elements" in stats, "statistics must contain 'total_elements'"
        assert isinstance(stats["total_elements"], int), "'total_elements' must be integer"

        assert "figure_count" in stats, "statistics must contain 'figure_count'"
        assert isinstance(stats["figure_count"], int), "'figure_count' must be integer"

        assert "table_count" in stats, "statistics must contain 'table_count'"
        assert isinstance(stats["table_count"], int), "'table_count' must be integer"

        assert "equation_count" in stats, "statistics must contain 'equation_count'"
        assert isinstance(stats["equation_count"], int), "'equation_count' must be integer"

        assert "extraction_time_seconds" in stats, "statistics must contain 'extraction_time_seconds'"
        assert isinstance(
            stats["extraction_time_seconds"], (int, float)
        ), "'extraction_time_seconds' must be number"

        # Verify counts are non-negative
        assert stats["total_elements"] >= 0, "total_elements must be non-negative"
        assert stats["figure_count"] >= 0, "figure_count must be non-negative"
        assert stats["table_count"] >= 0, "table_count must be non-negative"
        assert stats["equation_count"] >= 0, "equation_count must be non-negative"
        assert stats["extraction_time_seconds"] >= 0, "extraction_time_seconds must be non-negative"

    def test_json_element_schema(self, sample_extraction_result):
        """
        Contract: Each element in elements array must contain:
        - element_type: string (figure|table|equation)
        - output_filename: string
        - page_number: integer (1-indexed)
        - confidence_score: number (0.0-1.0)
        - bounding_box: object with x, y, width, height
        - sequence_number: integer (1-indexed)
        - element_id: string
        """
        json_output = format_json(sample_extraction_result)
        result = json.loads(json_output)

        if len(result["elements"]) == 0:
            pytest.skip("No elements to validate schema")

        element = result["elements"][0]

        # Required fields
        assert "element_id" in element, "element must contain 'element_id'"
        assert isinstance(element["element_id"], str), "'element_id' must be string"

        assert "element_type" in element, "element must contain 'element_type'"
        assert element["element_type"] in ["figure", "table", "equation"], "element_type must be figure|table|equation"

        assert "output_filename" in element, "element must contain 'output_filename'"
        assert isinstance(element["output_filename"], str), "'output_filename' must be string"

        assert "page_number" in element, "element must contain 'page_number'"
        assert isinstance(element["page_number"], int), "'page_number' must be integer"
        assert element["page_number"] >= 1, "page_number must be 1-indexed"

        assert "confidence_score" in element, "element must contain 'confidence_score'"
        assert isinstance(element["confidence_score"], (int, float)), "'confidence_score' must be number"
        assert 0.0 <= element["confidence_score"] <= 1.0, "confidence_score must be in range [0.0, 1.0]"

        assert "bounding_box" in element, "element must contain 'bounding_box'"
        assert isinstance(element["bounding_box"], dict), "'bounding_box' must be object"

        assert "sequence_number" in element, "element must contain 'sequence_number'"
        assert isinstance(element["sequence_number"], int), "'sequence_number' must be integer"
        assert element["sequence_number"] >= 1, "sequence_number must be 1-indexed"

    def test_json_bounding_box_schema(self, sample_extraction_result):
        """
        Contract: bounding_box object must contain:
        - x: number
        - y: number
        - width: number
        - height: number
        All must be non-negative.
        """
        json_output = format_json(sample_extraction_result)
        result = json.loads(json_output)

        if len(result["elements"]) == 0:
            pytest.skip("No elements to validate bounding box schema")

        bbox = result["elements"][0]["bounding_box"]

        # Required fields
        assert "x" in bbox, "bounding_box must contain 'x'"
        assert isinstance(bbox["x"], (int, float)), "'x' must be number"
        assert bbox["x"] >= 0, "x must be non-negative"

        assert "y" in bbox, "bounding_box must contain 'y'"
        assert isinstance(bbox["y"], (int, float)), "'y' must be number"
        assert bbox["y"] >= 0, "y must be non-negative"

        assert "width" in bbox, "bounding_box must contain 'width'"
        assert isinstance(bbox["width"], (int, float)), "'width' must be number"
        assert bbox["width"] > 0, "width must be positive"

        assert "height" in bbox, "bounding_box must contain 'height'"
        assert isinstance(bbox["height"], (int, float)), "'height' must be number"
        assert bbox["height"] > 0, "height must be positive"

    def test_json_output_is_valid_json(self, sample_extraction_result):
        """Contract: JSON output must be valid, parseable JSON."""
        json_output = format_json(sample_extraction_result)

        # Should not raise exception
        try:
            result = json.loads(json_output)
        except json.JSONDecodeError as e:
            pytest.fail(f"JSON output is not valid JSON: {e}")

        assert isinstance(result, dict), "JSON output must be a JSON object (dict)"

    def test_json_error_case_schema(self):
        """
        Contract: JSON output for failed extraction must contain:
        - success: false
        - statistics: object with zero counts
        - elements: empty array
        - errors: array with error messages (non-empty)
        - warnings: array (possibly empty)
        """
        from src.lib.models import Document

        document = Document(file_path="missing.pdf", page_count=1)

        error_result = ExtractionResult(
            document=document,
            elements=[],
            output_directory="./output",
            success=False,
            extraction_time_seconds=0.0,
            errors=["PDF file not found: missing.pdf"],
            warnings=[],
        )

        json_output = format_json(error_result)
        result = json.loads(json_output)

        assert result["success"] is False, "Error case must have success=false"
        assert len(result["errors"]) > 0, "Error case must have non-empty errors array"
        assert len(result["elements"]) == 0, "Error case should have empty elements array"
        assert result["statistics"]["total_elements"] == 0, "Error case should have zero elements"

    def test_json_output_count_consistency(self, sample_extraction_result):
        """
        Contract: Element counts must be consistent:
        - total_elements == figure_count + table_count + equation_count
        - len(elements) == total_elements
        """
        json_output = format_json(sample_extraction_result)
        result = json.loads(json_output)
        stats = result["statistics"]

        # Count consistency
        expected_total = stats["figure_count"] + stats["table_count"] + stats["equation_count"]
        assert (
            stats["total_elements"] == expected_total
        ), f"total_elements ({stats['total_elements']}) must equal sum of type counts ({expected_total})"

        assert len(result["elements"]) == stats["total_elements"], (
            f"Number of elements in array ({len(result['elements'])}) "
            f"must match total_elements ({stats['total_elements']})"
        )


class TestTextOutputContract:
    """Contract tests for human-readable text output format."""

    def test_text_output_has_status_line(self, sample_extraction_result):
        """
        Contract: Text output must start with a status line:
        - Success case: "✅ Extraction completed successfully"
        - Error case: "❌ Extraction failed"
        """
        text_output = format_text(sample_extraction_result)
        lines = text_output.strip().split("\n")

        assert len(lines) > 0, "Text output must not be empty"

        if sample_extraction_result.success:
            assert "Extraction completed successfully" in lines[0], (
                "Success case must have success status line"
            )
        else:
            assert "Extraction failed" in lines[0], "Error case must have error status line"

    def test_text_output_has_statistics_section(self, sample_extraction_result):
        """
        Contract: Text output must contain a statistics section with:
        - Total elements count
        - Figure count
        - Table count
        - Equation count (if non-zero)
        - Extraction time
        """
        text_output = format_text(sample_extraction_result)

        # Check for statistics section header
        assert "Extraction Statistics:" in text_output or "Statistics:" in text_output, (
            "Text output must contain statistics section"
        )

        # Check for required statistics
        assert "Total elements:" in text_output, "Must show total elements count"
        assert "Figures:" in text_output, "Must show figure count"
        assert "Tables:" in text_output, "Must show table count"
        assert "Time:" in text_output or "Extraction time:" in text_output, "Must show extraction time"

    def test_text_output_has_output_section(self, sample_extraction_result):
        """
        Contract: Text output must contain an output section showing:
        - Output directory
        - List of generated files (or count)
        """
        text_output = format_text(sample_extraction_result)

        # Check for output section
        assert "Output:" in text_output or "Files:" in text_output, (
            "Text output must contain output section"
        )

        assert "Directory:" in text_output or "directory:" in text_output, (
            "Text output must show output directory"
        )

    def test_text_output_shows_errors_when_present(self):
        """
        Contract: Text output must display error messages when extraction fails.
        """
        from src.lib.models import Document

        document = Document(file_path="missing.pdf", page_count=1)

        error_result = ExtractionResult(
            document=document,
            elements=[],
            output_directory="./output",
            success=False,
            extraction_time_seconds=0.0,
            errors=["PDF file not found: missing.pdf", "Invalid configuration"],
            warnings=[],
        )

        text_output = format_text(error_result)

        # Check for error section
        assert "Errors:" in text_output or "Error:" in text_output, (
            "Text output must show errors section"
        )

        # Check that actual error messages are present
        assert "PDF file not found" in text_output, "Error messages must be included in output"
        assert "Invalid configuration" in text_output, "All error messages must be shown"

    def test_text_output_shows_warnings_when_present(self, sample_extraction_result):
        """
        Contract: Text output must display warning messages when present.
        """
        # sample_extraction_result already has "Sample warning for testing"
        assert len(sample_extraction_result.warnings) > 0, "Fixture should have warnings"

        text_output = format_text(sample_extraction_result)

        # Check for warnings section
        assert "Warnings:" in text_output or "Warning:" in text_output, (
            "Text output must show warnings section when warnings are present"
        )

        # Check that actual warning is present
        assert "Sample warning for testing" in text_output, (
            "Warning messages must be included in output"
        )

    def test_text_output_is_human_readable(self, sample_extraction_result):
        """
        Contract: Text output must be human-readable:
        - Contains newlines for structure
        - Uses emojis for visual markers (✅, ❌, 📊, 📂, ⚠️, ⏱️)
        - Uses clear labels and formatting
        """
        text_output = format_text(sample_extraction_result)

        # Check for newlines (structured output)
        assert "\n" in text_output, "Text output must be multi-line for readability"

        # Check for visual markers (at least some emojis)
        has_emojis = any(
            emoji in text_output for emoji in ["✅", "❌", "📊", "📂", "⚠️", "⏱️"]
        )
        assert has_emojis, "Text output should use emojis for visual clarity"

    def test_text_output_no_elements_case(self):
        """
        Contract: Text output must handle case where no elements were detected.
        """
        from src.lib.models import Document

        document = Document(file_path="sample.pdf", page_count=1)

        no_elements_result = ExtractionResult(
            document=document,
            elements=[],
            output_directory="./output",
            success=True,
            extraction_time_seconds=1.23,
            errors=[],
            warnings=[],
        )

        text_output = format_text(no_elements_result)

        # Should still be successful
        assert "Extraction completed successfully" in text_output or "✅" in text_output, (
            "No elements case is still a success"
        )

        # Should show zero counts
        assert "Total elements: 0" in text_output or "0 elements" in text_output.lower(), (
            "Must show zero elements"
        )


@pytest.fixture
def sample_extraction_result():
    """Fixture providing a sample extraction result for testing."""
    from src.lib.models import Document, Page

    elements = [
        Element(
            element_id="test-id-1",
            element_type=ElementType.FIGURE,
            bounding_box=BoundingBox(x=100, y=200, width=300, height=400, page_number=1),
            confidence_score=0.95,
            page_number=1,
            sequence_number=1,
            output_filename="figure_01.pdf",
        ),
        Element(
            element_id="test-id-2",
            element_type=ElementType.TABLE,
            bounding_box=BoundingBox(x=50, y=100, width=500, height=200, page_number=2),
            confidence_score=0.88,
            page_number=2,
            sequence_number=1,
            output_filename="table_01.pdf",
        ),
    ]

    document = Document(
        file_path="sample.pdf",
        page_count=2,
        pages=[
            Page(page_number=1, width=612, height=792),
            Page(page_number=2, width=612, height=792),
        ],
    )

    return ExtractionResult(
        document=document,
        elements=elements,
        output_directory="./output",
        success=True,
        extraction_time_seconds=2.45,
        errors=[],
        warnings=["Sample warning for testing"],
    )
