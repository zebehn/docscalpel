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

            # Handle captions without numbers by searching the page
            captions_without_numbers = [c for c in captions if c.parsed_number is None and c.element_type == ElementType.FIGURE]
            if captions_without_numbers and caption_bboxes:
                full_page_text = page.get_text("text")

                # Find all figure numbers mentioned on the page
                found_numbers = []
                for pattern in self._compiled_patterns[ElementType.FIGURE]:
                    for match in pattern.finditer(full_page_text):
                        try:
                            parsed_num = int(match.group(1))
                            found_numbers.append(parsed_num)
                        except ValueError:
                            pass

                # Assign numbers to captions without numbers
                used_numbers = set(c.parsed_number for c in captions if c.parsed_number is not None)
                for caption in captions_without_numbers:
                    for num in found_numbers:
                        if num not in used_numbers:
                            caption.parsed_number = num
                            used_numbers.add(num)
                            logger.debug(
                                f"Assigned number {num} to caption without number via full-page search on page {page_number}"
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
        max_distance: float = 100.0,
        pdf_path: Optional[str] = None
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

        # Separate real captions from synthetic ones (synthetic have bbox at 0,0,1,1)
        real_captions = [c for c in captions if not (c.bounding_box.width == 1 and c.bounding_box.height == 1)]
        synthetic_captions = [c for c in captions if c.bounding_box.width == 1 and c.bounding_box.height == 1]

        # Group elements and captions by page to handle multi-figure pages specially
        from collections import defaultdict
        elements_by_page = defaultdict(list)
        for elem in elements:
            elements_by_page[(elem.page_number, elem.element_type)].append(elem)

        captions_by_page = defaultdict(list)
        for cap in captions:
            if cap.parsed_number is not None:
                captions_by_page[(cap.page_number, cap.element_type)].append(cap)

        # For pages with multiple captions AND multiple figures, use position-based matching
        # If there are multiple figures but only 1 caption, they're likely subfigures that should
        # all share the same caption (will be merged later by merge_by_shared_captions)
        for (page_num, elem_type), page_elements in elements_by_page.items():
            page_captions = captions_by_page.get((page_num, elem_type), [])

            # Only use position matching if we have multiple captions
            # (multiple figures with 1 caption = subfigures, handle via distance matching)
            if len(page_captions) > 1 and len(page_elements) > 1:
                # Multiple captions AND figures on this page - use smart matching
                # Sort elements by position (top to bottom, left to right)
                sorted_elements = sorted(page_elements, key=lambda e: (e.bounding_box.y, e.bounding_box.x))
                # Sort captions by number
                sorted_captions = sorted(page_captions, key=lambda c: c.parsed_number)

                # Associate in order: first element gets lowest-numbered caption, etc.
                # If there are more figures than captions, extra figures get the last caption
                # (likely subfigures of the last figure)
                for i, elem in enumerate(sorted_elements):
                    caption_idx = min(i, len(sorted_captions) - 1)
                    caption = sorted_captions[caption_idx]
                    associations[elem.element_id] = caption
                    logger.debug(
                        f"Associated {elem_type.value} {elem.element_id} with caption "
                        f"(number={caption.parsed_number}) via position matching"
                    )
                continue

        # For remaining elements not yet associated, use standard distance-based matching
        for element in elements:
            if element.element_id in associations:
                continue  # Already associated via position matching

            best_caption = None
            best_score = float('inf')

            for caption in real_captions:
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

        # Second pass: for remaining unassociated elements, try synthetic captions
        # Associate based on expected sequence (elements in reading order get sequential caption numbers)
        if synthetic_captions:
            unassociated = [e for e in elements if e.element_id not in associations]
            # Group by page and type
            from collections import defaultdict
            by_page = defaultdict(list)
            for elem in unassociated:
                by_page[(elem.page_number, elem.element_type)].append(elem)

            for (page_num, elem_type), page_elements in by_page.items():
                # Get synthetic captions for this page/type
                page_synthetic = [c for c in synthetic_captions
                                 if c.page_number == page_num and c.element_type == elem_type]
                if not page_synthetic:
                    continue

                # Sort elements by position (top to bottom, left to right)
                page_elements.sort(key=lambda e: (e.bounding_box.y, e.bounding_box.x))
                # Sort synthetic captions by number
                page_synthetic.sort(key=lambda c: c.parsed_number)

                # Associate in order
                for elem, caption in zip(page_elements, page_synthetic):
                    associations[elem.element_id] = caption
                    logger.info(
                        f"Associated {elem_type.value} {elem.element_id} with synthetic "
                        f"caption {caption.parsed_number} on page {page_num}"
                    )

        # Note: We no longer call _fix_shared_captions here because figures that
        # share a caption are now handled by merge_by_shared_captions in FigureMerger.
        # This allows subfigures to be properly merged instead of getting synthetic captions.

        return associations

    def _fix_shared_captions(
        self,
        elements: List,
        captions: List[Caption],
        associations: Dict[str, Caption],
        pdf_path: Optional[str] = None
    ) -> Dict[str, Caption]:
        """
        Fix cases where multiple elements are incorrectly associated with the same caption.

        This happens when YOLO misses some caption detections, causing all subfigures
        to be associated with a single caption.

        Args:
            elements: List of detected elements
            captions: List of detected captions
            associations: Current associations mapping element_id to Caption

        Returns:
            Updated associations dictionary
        """
        if not associations:
            return associations

        # Group elements by page and type
        from collections import defaultdict
        by_page_type = defaultdict(list)
        for element in elements:
            key = (element.page_number, element.element_type)
            by_page_type[key].append(element)

        for (page_num, elem_type), page_elements in by_page_type.items():
            # Count how many elements share each caption number
            caption_usage = defaultdict(list)
            for element in page_elements:
                if element.element_id in associations:
                    caption_num = associations[element.element_id].parsed_number
                    caption_usage[caption_num].append(element)

            # Find captions that are shared by multiple elements
            for caption_num, shared_elements in caption_usage.items():
                if len(shared_elements) <= 1:
                    continue  # No sharing, skip

                # Multiple elements share this caption - search for missing numbers
                logger.debug(
                    f"Found {len(shared_elements)} elements sharing caption {caption_num} "
                    f"on page {page_num}"
                )

                # Get all caption numbers already found on this page
                page_captions = [c for c in captions if c.page_number == page_num and c.element_type == elem_type]
                used_numbers = set(c.parsed_number for c in page_captions if c.parsed_number is not None)

                # Search for missing figure numbers in the expected range
                expected_numbers = list(range(caption_num, caption_num + len(shared_elements)))
                missing_numbers = [n for n in expected_numbers if n not in used_numbers]

                if not missing_numbers and pdf_path:
                    # Try searching full page for any figure numbers
                    missing_numbers = self._search_missing_numbers_on_page(
                        pdf_path,
                        page_num,
                        elem_type,
                        used_numbers,
                        caption_num,
                        len(shared_elements)
                    )

                if missing_numbers:
                    # Sort elements by vertical position (top to bottom)
                    sorted_elements = sorted(shared_elements, key=lambda e: e.bounding_box.y)

                    # Create synthetic captions for missing numbers
                    for i, missing_num in enumerate(missing_numbers[:len(sorted_elements)-1]):
                        if i + 1 < len(sorted_elements):
                            element = sorted_elements[i + 1]

                            # Create synthetic caption
                            synthetic_caption = Caption(
                                text=f"Figure {missing_num}: (synthetic - YOLO missed detection)",
                                bounding_box=element.bounding_box,  # Use element bbox as placeholder
                                page_number=page_num,
                                element_type=elem_type,
                                parsed_number=missing_num
                            )

                            # Update association
                            associations[element.element_id] = synthetic_caption
                            logger.info(
                                f"Created synthetic caption {missing_num} for element on page {page_num} "
                                f"(YOLO missed detection)"
                            )

        return associations

    def _search_missing_numbers_on_page(
        self,
        pdf_path: str,
        page_num: int,
        elem_type: ElementType,
        used_numbers: set,
        start_num: int,
        count: int
    ) -> List[int]:
        """
        Search page text for missing figure numbers.

        Args:
            pdf_path: Path to PDF file
            page_num: Page number to search
            elem_type: Element type
            used_numbers: Set of already-used numbers
            start_num: Starting figure number
            count: Number of figures

        Returns:
            List of missing figure numbers found on page
        """
        missing = []

        try:
            import fitz
            doc = fitz.open(pdf_path)
            page = doc[page_num - 1]  # Convert to 0-indexed
            text = page.get_text("text")

            # Search for figure numbers in expected range
            if elem_type not in self._compiled_patterns:
                doc.close()
                return missing

            for pattern in self._compiled_patterns[elem_type]:
                for match in pattern.finditer(text):
                    try:
                        num = int(match.group(1))
                        # Only include numbers in expected range that aren't already used
                        if start_num <= num < start_num + count and num not in used_numbers:
                            missing.append(num)
                    except ValueError:
                        pass

            doc.close()

        except Exception as e:
            logger.error(f"Failed to search for missing numbers on page {page_num}: {e}")

        return sorted(set(missing))  # Remove duplicates and sort

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
