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
from .caption_parser import CaptionParser
from .figure_merger import FigureMerger

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
        >>> from docscalpel import extract_elements, ExtractionConfig, ElementType
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
        all_caption_bboxes = []  # Collect caption bboxes for later processing

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

                    # Collect caption bboxes from FigureDetector if available
                    if hasattr(detector, 'get_caption_bboxes'):
                        caption_bboxes = detector.get_caption_bboxes()
                        if caption_bboxes:
                            all_caption_bboxes.extend([
                                (bbox, elem_type, page.page_number)
                                for bbox, elem_type in caption_bboxes
                            ])
                            logger.debug(
                                f"Found {len(caption_bboxes)} caption(s) on page {page.page_number}"
                            )

                except Exception as e:
                    error_msg = (
                        f"Detection failed for {element_type.value} "
                        f"on page {page.page_number}: {str(e)}"
                    )
                    logger.warning(error_msg)
                    warnings.append(error_msg)

        logger.info(f"Total elements detected: {len(all_elements)}")

        # Step 5.5: Merge multi-part figures on the same page
        if ElementType.FIGURE in config.element_types and len(all_elements) > 1:
            logger.info("Merging multi-part figures...")
            merger = FigureMerger(
                overlap_threshold=0.3,
                proximity_threshold=20.0,
                min_confidence=config.confidence_threshold
            )
            all_elements = merger.merge_elements(all_elements)

        # Step 6: Handle overlapping elements (keep highest confidence)
        if len(config.element_types) > 1:
            all_elements, overlap_warnings = _handle_overlaps(all_elements)
            warnings.extend(overlap_warnings)

        # Step 6.5: Parse captions and associate with elements
        caption_associations = {}
        if all_caption_bboxes:
            logger.info(f"Parsing {len(all_caption_bboxes)} captions...")
            caption_parser = CaptionParser()

            # Group caption bboxes by page
            captions_by_page = defaultdict(list)
            for bbox, elem_type, page_num in all_caption_bboxes:
                captions_by_page[page_num].append((bbox, elem_type))

            # Extract and parse captions for each page
            all_captions = []
            for page_num, page_caption_bboxes in captions_by_page.items():
                captions = caption_parser.extract_captions_from_page(
                    pdf_path, page_num, page_caption_bboxes
                )
                all_captions.extend(captions)

            # Find missing figure numbers in the sequence and create synthetic captions
            if all_captions:
                from .caption_parser import Caption
                from .models import BoundingBox

                figure_captions = [c for c in all_captions if c.element_type == ElementType.FIGURE and c.parsed_number is not None]
                if figure_captions:
                    detected_numbers = sorted(set(c.parsed_number for c in figure_captions))
                    min_num = min(detected_numbers)
                    max_num = max(detected_numbers)

                    # Find missing numbers in the sequence
                    missing_numbers = [n for n in range(min_num, max_num + 1) if n not in detected_numbers]

                    if missing_numbers:
                        logger.info(f"Found missing figure numbers: {missing_numbers}")

                        # For each missing number, try to find which page has the actual caption
                        import fitz
                        import re
                        doc = fitz.open(pdf_path)
                        for missing_num in missing_numbers:
                            # Search for this figure number with caption pattern (Figure X: description)
                            # Don't match mere references like "see Figure X" or "in Figure X"
                            caption_pattern = re.compile(
                                rf'Figure\s+{missing_num}\s*:',
                                re.IGNORECASE
                            )
                            for page_num in range(1, len(document.pages) + 1):
                                page = doc[page_num - 1]
                                text = page.get_text("text")

                                # Only create synthetic caption if there's an actual caption format
                                if caption_pattern.search(text):
                                    # Create synthetic caption for this page
                                    synthetic_caption = Caption(
                                        text=f"Figure {missing_num}: (YOLO missed caption detection)",
                                        bounding_box=BoundingBox(x=0, y=0, width=1, height=1, page_number=page_num),
                                        page_number=page_num,
                                        element_type=ElementType.FIGURE,
                                        parsed_number=missing_num
                                    )
                                    all_captions.append(synthetic_caption)
                                    logger.info(f"Created synthetic caption for Figure {missing_num} on page {page_num}")
                                    break  # Only create one synthetic caption per missing number
                        doc.close()

            # Associate captions with elements
            if all_captions:
                caption_associations = caption_parser.associate_captions_with_elements(
                    all_elements, all_captions, max_distance=100.0, pdf_path=pdf_path
                )
                logger.info(
                    f"Associated {len(caption_associations)} captions with elements"
                )

                # Merge elements that share the same caption (subfigures)
                if ElementType.FIGURE in config.element_types and len(all_elements) > 1:
                    logger.info("Merging subfigures with shared captions...")
                    merger = FigureMerger()
                    all_elements, caption_associations = merger.merge_by_shared_captions(
                        all_elements, caption_associations
                    )

        # Step 7: Assign sequence numbers and filenames by type
        all_elements = _assign_sequence_numbers_and_filenames(
            all_elements,
            config.naming_pattern,
            caption_associations
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
    naming_pattern: str,
    caption_associations: Optional[Dict[str, any]] = None
) -> List[Element]:
    """
    Assign sequence numbers and generate filenames for elements.

    Uses parsed caption numbers when available, falls back to sequential numbering.

    Args:
        elements: List of elements to process
        naming_pattern: Pattern with {type} and {counter} placeholders
        caption_associations: Optional dict mapping element_id to Caption objects

    Returns:
        List of elements with updated sequence_number and output_filename
    """
    if caption_associations is None:
        caption_associations = {}

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

        # Build mapping of parsed numbers to elements (if available)
        elements_with_caption_numbers = {}
        elements_without_caption_numbers = []

        for element in type_elements:
            if element.element_id in caption_associations:
                caption = caption_associations[element.element_id]
                if caption.parsed_number is not None:
                    elements_with_caption_numbers[caption.parsed_number] = element
                    logger.debug(
                        f"Using caption number {caption.parsed_number} for "
                        f"{element_type.value} on page {element.page_number}"
                    )
                else:
                    elements_without_caption_numbers.append(element)
            else:
                elements_without_caption_numbers.append(element)

        # Assign numbers
        if elements_with_caption_numbers:
            # Use caption numbers for elements that have them
            for parsed_num, element in sorted(elements_with_caption_numbers.items()):
                filename = naming_pattern.format(
                    type=element_type.value,
                    counter=parsed_num
                )

                updated_element = create_element(
                    element_type=element.element_type,
                    bounding_box=element.bounding_box,
                    page_number=element.page_number,
                    sequence_number=parsed_num,
                    confidence_score=element.confidence_score,
                    output_filename=filename
                )
                updated_elements.append(updated_element)

            # Assign sequential numbers to elements without captions
            # Start from the next available number
            next_available = max(elements_with_caption_numbers.keys()) + 1
            for element in elements_without_caption_numbers:
                filename = naming_pattern.format(
                    type=element_type.value,
                    counter=next_available
                )

                updated_element = create_element(
                    element_type=element.element_type,
                    bounding_box=element.bounding_box,
                    page_number=element.page_number,
                    sequence_number=next_available,
                    confidence_score=element.confidence_score,
                    output_filename=filename
                )
                updated_elements.append(updated_element)
                next_available += 1
        else:
            # No caption numbers available, use sequential numbering
            for i, element in enumerate(type_elements, start=1):
                filename = naming_pattern.format(
                    type=element_type.value,
                    counter=i
                )

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
