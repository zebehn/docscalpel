"""
Caption parser module for extracting figure numbers from captions.

This module provides functionality to detect captions, extract text,
and parse figure/table numbers from the extracted text.
"""

import re
import logging
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

try:
    import fitz  # PyMuPDF
except ImportError:
    raise ImportError("PyMuPDF is required. Install with: pip install PyMuPDF")

from .models import BoundingBox, ElementType

logger = logging.getLogger(__name__)


@dataclass
class Caption:
    """Represents a detected caption with its text and bounding box."""
    text: str
    bounding_box: BoundingBox
    page_number: int
    element_type: ElementType  # FIGURE, TABLE, or EQUATION
    parsed_number: Optional[int] = None


class CaptionParser:
    """
    Parser for extracting and parsing captions from PDF pages.

    Detects captions, extracts their text, and parses figure/table numbers.
    """

    # Regular expressions for parsing figure/table numbers
    FIGURE_PATTERNS = [
        r'(?:Figure|Fig\.?|FIGURE|FIG\.?)\s*(\d+)',  # Figure 6, Fig. 6, etc.
        r'(?:Figure|Fig\.?|FIGURE|FIG\.?)\s*([A-Z])',  # Figure A, Fig. B, etc.
    ]

    TABLE_PATTERNS = [
        r'(?:Table|TABLE|Tbl\.?)\s*(\d+)',  # Table 2, etc.
        r'(?:Table|TABLE|Tbl\.?)\s*([A-Z])',  # Table A, etc.
    ]

    EQUATION_PATTERNS = [
        r'(?:Equation|Eq\.?|EQUATION|EQ\.?)\s*(\d+)',  # Equation 3, etc.
    ]

    def __init__(self):
        """Initialize CaptionParser."""
        self._compiled_patterns = {
            ElementType.FIGURE: [re.compile(p, re.IGNORECASE) for p in self.FIGURE_PATTERNS],
            ElementType.TABLE: [re.compile(p, re.IGNORECASE) for p in self.TABLE_PATTERNS],
            ElementType.EQUATION: [re.compile(p, re.IGNORECASE) for p in self.EQUATION_PATTERNS],
        }

    def extract_captions_from_page(
        self,
        pdf_path: str,
        page_number: int,
        caption_bboxes: List[Tuple[BoundingBox, ElementType]]
    ) -> List[Caption]:
        """
        Extract text from caption bounding boxes on a page.

        Args:
            pdf_path: Path to the PDF file
            page_number: Page number (1-indexed)
            caption_bboxes: List of tuples (BoundingBox, ElementType) for detected captions

        Returns:
            List of Caption objects with extracted text and parsed numbers
        """
        captions = []

        try:
            doc = fitz.open(pdf_path)
            page = doc[page_number - 1]  # Convert to 0-indexed

            for bbox, element_type in caption_bboxes:
                # Extract text from bounding box region
                rect = fitz.Rect(bbox.x, bbox.y, bbox.x2, bbox.y2)
                text = page.get_text("text", clip=rect).strip()

                if not text:
                    logger.debug(f"No text found in caption bbox on page {page_number}")
                    continue

                # Parse figure/table number from text
                parsed_number = self._parse_number(text, element_type)

                # If no number parsed, try expanding bbox to capture more text
                if parsed_number is None and element_type == ElementType.FIGURE:
                    # Expand bbox vertically to capture "Figure X:" that might be just outside
                    expanded_rect = fitz.Rect(
                        max(0, bbox.x - 50),
                        max(0, bbox.y - 50),
                        bbox.x2 + 50,
                        bbox.y2 + 50
                    )
                    expanded_text = page.get_text("text", clip=expanded_rect).strip()
                    parsed_number = self._parse_number(expanded_text, element_type)
                    if parsed_number is not None:
                        text = expanded_text
                        logger.debug(
                            f"Found caption number {parsed_number} with expanded search on page {page_number}"
                        )

                caption = Caption(
                    text=text,
                    bounding_box=bbox,
                    page_number=page_number,
                    element_type=element_type,
                    parsed_number=parsed_number
                )

                captions.append(caption)
                logger.debug(
                    f"Extracted caption on page {page_number}: "
                    f"'{text[:50]}...' (number={parsed_number})"
                )

            # If we have captions without numbers, search entire page for missing figure numbers
            captions_without_numbers = [c for c in captions if c.parsed_number is None and c.element_type == ElementType.FIGURE]
            if captions_without_numbers:
                full_page_text = page.get_text("text")

                # Find all figure numbers in the page
                found_numbers = []
                for pattern in self._compiled_patterns[ElementType.FIGURE]:
                    for match in pattern.finditer(full_page_text):
                        try:
                            parsed_num = int(match.group(1))
                            found_numbers.append(parsed_num)
                        except ValueError:
                            pass

                # For each caption without a number, assign the first unused number found
                used_numbers = set(c.parsed_number for c in captions if c.parsed_number is not None)
                for caption in captions_without_numbers:
                    for num in found_numbers:
                        if num not in used_numbers:
                            caption.parsed_number = num
                            used_numbers.add(num)
                            logger.debug(
                                f"Found missing caption number {num} via full-page search on page {page_number}"
                            )
                            break

            doc.close()

        except Exception as e:
            logger.error(f"Failed to extract captions from page {page_number}: {e}")

        return captions

    def _parse_number(self, text: str, element_type: ElementType) -> Optional[int]:
        """
        Parse the number from a caption text.

        Args:
            text: Caption text
            element_type: Type of element (FIGURE, TABLE, EQUATION)

        Returns:
            Parsed number as integer, or None if no number found
        """
        if element_type not in self._compiled_patterns:
            return None

        patterns = self._compiled_patterns[element_type]

        for pattern in patterns:
            match = pattern.search(text)
            if match:
                number_str = match.group(1)

                # Try to convert to integer
                try:
                    return int(number_str)
                except ValueError:
                    # Handle letter-based numbering (A=1, B=2, etc.)
                    if number_str.isalpha() and len(number_str) == 1:
                        return ord(number_str.upper()) - ord('A') + 1
                    logger.debug(f"Could not convert '{number_str}' to integer")

        return None

    def associate_captions_with_elements(
        self,
        elements: List,
        captions: List[Caption],
        max_distance: float = 100.0
    ) -> Dict[str, Caption]:
        """
        Associate captions with their corresponding elements based on proximity.

        Args:
            elements: List of detected elements (figures/tables/equations)
            captions: List of detected captions
            max_distance: Maximum distance to consider for association (in points)

        Returns:
            Dictionary mapping element_id to Caption
        """
        associations = {}

        for element in elements:
            best_caption = None
            best_score = float('inf')

            for caption in captions:
                # Only match captions of the same type on the same page
                if (caption.element_type != element.element_type or
                    caption.page_number != element.page_number):
                    continue

                # Skip captions without parsed numbers (likely labels, not actual captions)
                if caption.parsed_number is None:
                    continue

                # Calculate distance between element and caption
                distance = self._calculate_distance(element.bounding_box, caption.bounding_box)

                # Skip if beyond max distance
                if distance >= max_distance:
                    continue

                # Compute score: prefer captions below figures over overlapping/above
                score = distance
                if self._is_caption_below(element.bounding_box, caption.bounding_box):
                    # Caption below figure (ideal position) - use actual distance
                    score = distance
                else:
                    # Caption overlaps or above - add penalty
                    score = distance + 500.0

                if score < best_score:
                    best_score = score
                    best_caption = caption

            if best_caption:
                associations[element.element_id] = best_caption
                logger.debug(
                    f"Associated {element.element_type.value} {element.element_id} "
                    f"with caption (number={best_caption.parsed_number})"
                )

        return associations

    def _is_caption_below(self, element_bbox: BoundingBox, caption_bbox: BoundingBox) -> bool:
        """
        Check if caption is positioned below the element.

        Args:
            element_bbox: Element bounding box
            caption_bbox: Caption bounding box

        Returns:
            True if caption is below element
        """
        return element_bbox.y2 <= caption_bbox.y

    def _calculate_distance(self, bbox1: BoundingBox, bbox2: BoundingBox) -> float:
        """
        Calculate distance between two bounding boxes.

        Uses vertical distance (assuming captions are typically below figures).

        Args:
            bbox1: First bounding box
            bbox2: Second bounding box

        Returns:
            Distance in points
        """
        # Calculate vertical distance between boxes
        if bbox1.y2 <= bbox2.y:
            # bbox1 is above bbox2
            return bbox2.y - bbox1.y2
        elif bbox2.y2 <= bbox1.y:
            # bbox2 is above bbox1
            return bbox1.y - bbox2.y2
        else:
            # Boxes overlap vertically
            return 0.0
