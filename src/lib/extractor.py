"""
Main extraction orchestrator for PDF element extraction.

This module coordinates PDF loading, element detection, cropping,
and result generation for the extraction workflow.
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict

from .models import (
    ExtractionConfig,
    ExtractionResult,
    Element,
    ElementType,
    create_element,
    InvalidPDFError,
    ExtractionFailedError,
)
from .pdf_processor import load_document, validate_pdf
from .detectors import FigureDetector, TableDetector, EquationDetector
from .cropper import crop_element

logger = logging.getLogger(__name__)


def extract_elements(
    pdf_path: str,
    config: Optional[ExtractionConfig] = None
) -> ExtractionResult:
    """
    Extract figures, tables, and/or equations from a PDF file.

    This is the main public API function for the extraction library.

    Args:
        pdf_path: Path to the PDF file to process
        config: Optional ExtractionConfig (uses defaults if None)

    Returns:
        ExtractionResult with extracted elements and metadata

    Raises:
        InvalidPDFError: If PDF file is invalid or cannot be opened
        ConfigurationError: If config has invalid settings
        ExtractionFailedError: If extraction process fails critically

    Example:
        >>> from src.lib import extract_elements, ExtractionConfig, ElementType
        >>> config = ExtractionConfig(element_types=[ElementType.FIGURE])
        >>> result = extract_elements("paper.pdf", config)
        >>> print(f"Extracted {result.figure_count} figures")
    """
    start_time = time.time()

    # Use default config if not provided
    if config is None:
        config = ExtractionConfig()

    errors: List[str] = []
    warnings: List[str] = []

    try:
        # Step 1: Validate PDF file
        logger.info(f"Validating PDF: {pdf_path}")
        validation = validate_pdf(pdf_path)

        if not validation.is_valid:
            raise InvalidPDFError(validation.error_message)

        # Step 2: Load PDF document
        logger.info(f"Loading PDF document: {pdf_path}")
        document = load_document(pdf_path, max_pages=config.max_pages)

        logger.info(
            f"Loaded {len(document.pages)}/{document.page_count} pages "
            f"from {pdf_path}"
        )

        # Step 3: Create output directory if needed
        output_dir = Path(config.output_directory)
        if not output_dir.exists():
            logger.info(f"Creating output directory: {output_dir}")
            output_dir.mkdir(parents=True, exist_ok=True)

        # Verify output directory is writable
        if not os.access(output_dir, os.W_OK):
            raise ExtractionFailedError(
                f"Output directory is not writable: {output_dir}"
            )

        # Step 4: Initialize detectors for requested element types
        detectors = _create_detectors(config)

        # Step 5: Detect elements across all pages
        logger.info(f"Detecting elements (types: {[str(t) for t in config.element_types]})")
        all_elements: List[Element] = []

        for page in document.pages:
            logger.debug(f"Processing page {page.page_number}/{len(document.pages)}")

            for element_type, detector in detectors.items():
                try:
                    detected = detector.detect(page, pdf_path=pdf_path)
                    all_elements.extend(detected)
                    logger.debug(
                        f"Detected {len(detected)} {element_type.value}(s) "
                        f"on page {page.page_number}"
                    )
                except Exception as e:
                    error_msg = (
                        f"Detection failed for {element_type.value} "
                        f"on page {page.page_number}: {str(e)}"
                    )
                    logger.warning(error_msg)
                    warnings.append(error_msg)

        logger.info(f"Total elements detected: {len(all_elements)}")

        # Step 6: Handle overlapping elements (keep highest confidence)
        if len(config.element_types) > 1:
            all_elements, overlap_warnings = _handle_overlaps(all_elements)
            warnings.extend(overlap_warnings)

        # Step 7: Assign sequence numbers and filenames by type
        all_elements = _assign_sequence_numbers_and_filenames(
            all_elements,
            config.naming_pattern
        )

        # Step 8: Sort elements by page number and position
        all_elements = _sort_elements(all_elements)

        # Step 9: Crop elements and save to individual PDF files
        logger.info(f"Cropping {len(all_elements)} elements to output directory")
        successfully_extracted = []

        for element in all_elements:
            output_path = output_dir / element.output_filename

            try:
                success = crop_element(
                    pdf_path=pdf_path,
                    element=element,
                    output_path=str(output_path),
                    overwrite=config.overwrite_existing
                )

                if success:
                    successfully_extracted.append(element)
                    logger.debug(f"Extracted: {element.output_filename}")
                else:
                    warning_msg = f"Failed to extract {element.output_filename}"
                    warnings.append(warning_msg)
                    logger.warning(warning_msg)

            except FileExistsError as e:
                warning_msg = f"Skipping existing file: {element.output_filename}"
                warnings.append(warning_msg)
                logger.warning(warning_msg)

            except Exception as e:
                error_msg = (
                    f"Failed to extract {element.output_filename}: {str(e)}"
                )
                warnings.append(error_msg)
                logger.error(error_msg)

        # Step 10: Create extraction result
        extraction_time = time.time() - start_time

        result = ExtractionResult(
            document=document,
            elements=successfully_extracted,
            output_directory=str(output_dir),
            success=True,
            extraction_time_seconds=extraction_time,
            errors=errors,
            warnings=warnings
        )

        logger.info(
            f"Extraction complete: {result.total_elements} elements "
            f"in {extraction_time:.2f}s"
        )

        return result

    except (InvalidPDFError, ExtractionFailedError) as e:
        # Known errors - re-raise with context
        logger.error(f"Extraction failed: {e}")
        raise

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error during extraction: {e}", exc_info=True)
        raise ExtractionFailedError(
            f"Extraction failed with unexpected error: {str(e)}"
        )


def _create_detectors(config: ExtractionConfig) -> Dict[ElementType, object]:
    """
    Create detector instances for requested element types.

    Args:
        config: ExtractionConfig with element_types and confidence_threshold

    Returns:
        Dictionary mapping ElementType to detector instance
    """
    detectors = {}

    for element_type in config.element_types:
        if element_type == ElementType.FIGURE:
            detectors[element_type] = FigureDetector(
                confidence_threshold=config.confidence_threshold
            )
        elif element_type == ElementType.TABLE:
            detectors[element_type] = TableDetector(
                confidence_threshold=config.confidence_threshold
            )
        elif element_type == ElementType.EQUATION:
            detectors[element_type] = EquationDetector(
                confidence_threshold=config.confidence_threshold
            )
        else:
            logger.warning(f"Unknown element type: {element_type}")

    return detectors


def _handle_overlaps(
    elements: List[Element],
    overlap_threshold: float = 0.5
) -> tuple[List[Element], List[str]]:
    """
    Remove overlapping elements, keeping the one with highest confidence.

    Args:
        elements: List of detected elements
        overlap_threshold: Minimum IoU to consider overlap (0.0-1.0)

    Returns:
        Tuple of (filtered_elements, warnings)
    """
    warnings: List[str] = []

    if len(elements) <= 1:
        return elements, warnings

    # Sort by confidence (highest first)
    sorted_elements = sorted(
        elements,
        key=lambda e: e.confidence_score,
        reverse=True
    )

    kept_elements: List[Element] = []

    for element in sorted_elements:
        # Check if this element overlaps with any kept element
        overlaps = False

        for kept in kept_elements:
            if _elements_overlap(element, kept, overlap_threshold):
                overlaps = True
                warning = (
                    f"Removed overlapping {element.element_type.value} "
                    f"(confidence={element.confidence_score:.2f}) "
                    f"in favor of {kept.element_type.value} "
                    f"(confidence={kept.confidence_score:.2f}) "
                    f"on page {element.page_number}"
                )
                warnings.append(warning)
                logger.debug(warning)
                break

        if not overlaps:
            kept_elements.append(element)

    return kept_elements, warnings


def _elements_overlap(
    elem1: Element,
    elem2: Element,
    threshold: float = 0.5
) -> bool:
    """
    Check if two elements overlap using IoU (Intersection over Union).

    Args:
        elem1: First element
        elem2: Second element
        threshold: Minimum IoU to consider overlap

    Returns:
        True if elements overlap above threshold
    """
    # Elements on different pages don't overlap
    if elem1.page_number != elem2.page_number:
        return False

    bbox1 = elem1.bounding_box
    bbox2 = elem2.bounding_box

    # Calculate intersection
    x_left = max(bbox1.x, bbox2.x)
    y_top = max(bbox1.y, bbox2.y)
    x_right = min(bbox1.x2, bbox2.x2)
    y_bottom = min(bbox1.y2, bbox2.y2)

    if x_right < x_left or y_bottom < y_top:
        return False  # No intersection

    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # Calculate union
    area1 = bbox1.area
    area2 = bbox2.area
    union_area = area1 + area2 - intersection_area

    # Calculate IoU
    iou = intersection_area / union_area if union_area > 0 else 0

    return iou >= threshold


def _assign_sequence_numbers_and_filenames(
    elements: List[Element],
    naming_pattern: str
) -> List[Element]:
    """
    Assign sequence numbers and generate filenames for elements.

    Each element type gets independent sequential numbering.

    Args:
        elements: List of elements to process
        naming_pattern: Pattern with {type} and {counter} placeholders

    Returns:
        List of elements with updated sequence_number and output_filename
    """
    # Group elements by type
    by_type: Dict[ElementType, List[Element]] = defaultdict(list)
    for element in elements:
        by_type[element.element_type].append(element)

    # Assign sequence numbers within each type
    updated_elements: List[Element] = []

    for element_type, type_elements in by_type.items():
        # Sort by page number, then by position
        type_elements.sort(
            key=lambda e: (e.page_number, e.bounding_box.y, e.bounding_box.x)
        )

        # Assign sequential numbers
        for i, element in enumerate(type_elements, start=1):
            # Generate filename from pattern
            filename = naming_pattern.format(
                type=element_type.value,
                counter=i
            )

            # Create new element with updated fields
            updated_element = create_element(
                element_type=element.element_type,
                bounding_box=element.bounding_box,
                page_number=element.page_number,
                sequence_number=i,
                confidence_score=element.confidence_score,
                output_filename=filename
            )

            updated_elements.append(updated_element)

    return updated_elements


def _sort_elements(elements: List[Element]) -> List[Element]:
    """
    Sort elements by page number and position within page.

    Args:
        elements: List of elements to sort

    Returns:
        Sorted list of elements
    """
    return sorted(
        elements,
        key=lambda e: (e.page_number, e.bounding_box.y, e.bounding_box.x)
    )
