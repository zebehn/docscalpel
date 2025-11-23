"""
Output formatters for CLI.

Provides JSON and human-readable text formatters for extraction results.
"""

import json
from typing import Dict, Any

from src.lib.models import ExtractionResult, Element, ElementType


def format_json(result: ExtractionResult) -> str:
    """
    Format extraction result as JSON.

    Args:
        result: ExtractionResult from extract_elements()

    Returns:
        JSON string with complete extraction results

    Example:
        >>> result = extract_elements("paper.pdf")
        >>> json_output = format_json(result)
        >>> print(json_output)
    """
    output = {
        "success": result.success,
        "statistics": {
            "total_elements": result.total_elements,
            "figure_count": result.figure_count,
            "table_count": result.table_count,
            "equation_count": result.equation_count,
            "extraction_time_seconds": result.extraction_time_seconds,
        },
        "document": {
            "file_path": result.document.file_path,
            "page_count": result.document.page_count,
            "pages_processed": len(result.document.pages),
            "file_size_bytes": result.document.file_size_bytes,
            "is_encrypted": result.document.is_encrypted,
        },
        "extraction": {
            "output_directory": result.output_directory,
        },
        "elements": [
            {
                "element_id": elem.element_id,
                "element_type": elem.element_type.value,
                "output_filename": elem.output_filename,
                "page_number": elem.page_number,
                "sequence_number": elem.sequence_number,
                "confidence_score": elem.confidence_score,
                "bounding_box": {
                    "x": elem.bounding_box.x,
                    "y": elem.bounding_box.y,
                    "width": elem.bounding_box.width,
                    "height": elem.bounding_box.height,
                    "page_number": elem.bounding_box.page_number,
                    "padding": elem.bounding_box.padding,
                },
            }
            for elem in result.elements
        ],
        "errors": result.errors,
        "warnings": result.warnings,
    }

    return json.dumps(output, indent=2)


def format_text(result: ExtractionResult) -> str:
    """
    Format extraction result as human-readable text.

    Args:
        result: ExtractionResult from extract_elements()

    Returns:
        Human-readable text summary

    Example:
        >>> result = extract_elements("paper.pdf")
        >>> text_output = format_text(result)
        >>> print(text_output)
    """
    lines = []

    # Header
    if result.success:
        lines.append("✅ Extraction completed successfully")
    else:
        lines.append("❌ Extraction failed")

    lines.append("")

    # Document info
    lines.append("📄 Document:")
    lines.append(f"  File: {result.document.file_path}")
    lines.append(f"  Pages: {result.document.page_count} total, {len(result.document.pages)} processed")
    lines.append(f"  Size: {result.document.file_size_bytes:,} bytes")
    lines.append("")

    # Statistics
    lines.append("📊 Extraction Statistics:")
    lines.append(f"  Total elements: {result.total_elements}")
    lines.append(f"  Figures: {result.figure_count}")
    lines.append(f"  Tables: {result.table_count}")
    lines.append(f"  Equations: {result.equation_count}")
    lines.append(f"  Time: {result.extraction_time_seconds:.2f}s")
    lines.append("")

    # Output directory
    lines.append("📂 Output:")
    lines.append(f"  Directory: {result.output_directory}")
    lines.append("")

    # Elements list
    if result.total_elements > 0:
        lines.append("📋 Extracted Elements:")

        # Group by type
        by_type = {
            ElementType.FIGURE: [],
            ElementType.TABLE: [],
            ElementType.EQUATION: []
        }

        for elem in result.elements:
            by_type[elem.element_type].append(elem)

        for elem_type in [ElementType.FIGURE, ElementType.TABLE, ElementType.EQUATION]:
            elements = by_type[elem_type]
            if elements:
                lines.append(f"  {elem_type.value.capitalize()}s ({len(elements)}):")
                for elem in elements:
                    lines.append(
                        f"    - {elem.output_filename} "
                        f"(page {elem.page_number}, confidence: {elem.confidence_score:.2f})"
                    )
                lines.append("")
    else:
        lines.append("ℹ️  No elements detected in the PDF")
        lines.append("")

    # Warnings
    if result.warnings:
        lines.append("⚠️  Warnings:")
        for warning in result.warnings:
            lines.append(f"  - {warning}")
        lines.append("")

    # Errors
    if result.errors:
        lines.append("❌ Errors:")
        for error in result.errors:
            lines.append(f"  - {error}")
        lines.append("")

    return "\n".join(lines)
