"""
Figure merger module for combining multi-part figure detections.

This module provides functionality to merge multiple overlapping or
closely-related bounding boxes that belong to the same figure.
"""

import logging
from typing import List
from dataclasses import replace

from .models import Element, BoundingBox

logger = logging.getLogger(__name__)


class FigureMerger:
    """
    Merger for combining multi-part figure detections.

    Detects and merges bounding boxes that likely belong to the same figure
    based on overlap, proximity, and confidence scores.
    """

    def __init__(
        self,
        overlap_threshold: float = 0.3,
        proximity_threshold: float = 20.0,
        min_confidence: float = 0.5
    ):
        """
        Initialize FigureMerger.

        Args:
            overlap_threshold: Minimum IoU to consider boxes as overlapping (0.0-1.0)
            proximity_threshold: Maximum distance to consider boxes as close (in points)
            min_confidence: Minimum confidence to consider for merging
        """
        self.overlap_threshold = overlap_threshold
        self.proximity_threshold = proximity_threshold
        self.min_confidence = min_confidence

    def merge_elements(self, elements: List[Element]) -> List[Element]:
        """
        Merge overlapping or closely-related elements on each page.

        Args:
            elements: List of detected elements

        Returns:
            List of merged elements
        """
        if not elements:
            return elements

        # Group elements by page and type
        by_page_type = {}
        for element in elements:
            key = (element.page_number, element.element_type)
            if key not in by_page_type:
                by_page_type[key] = []
            by_page_type[key].append(element)

        merged_elements = []

        # Process each page/type group
        for (page_num, elem_type), page_elements in by_page_type.items():
            logger.debug(
                f"Merging {len(page_elements)} {elem_type.value}(s) on page {page_num}"
            )

            # Merge elements within this group
            merged = self._merge_group(page_elements)
            merged_elements.extend(merged)

            if len(merged) < len(page_elements):
                logger.info(
                    f"Merged {len(page_elements)} → {len(merged)} {elem_type.value}(s) "
                    f"on page {page_num}"
                )

        return merged_elements

    def _merge_group(self, elements: List[Element]) -> List[Element]:
        """
        Merge elements within a single page/type group.

        Args:
            elements: List of elements to merge (same page and type)

        Returns:
            List of merged elements
        """
        if len(elements) <= 1:
            return elements

        # Sort by confidence (highest first)
        sorted_elements = sorted(
            elements,
            key=lambda e: e.confidence_score,
            reverse=True
        )

        merged = []
        used = set()

        for i, elem1 in enumerate(sorted_elements):
            if i in used:
                continue

            # Find all elements that should be merged with elem1
            to_merge = [elem1]
            used.add(i)

            for j, elem2 in enumerate(sorted_elements):
                if j in used or j <= i:
                    continue

                # Check if elem2 should be merged with elem1
                if self._should_merge(elem1, elem2):
                    to_merge.append(elem2)
                    used.add(j)

            # Create merged element
            if len(to_merge) > 1:
                merged_elem = self._create_merged_element(to_merge)
                logger.debug(
                    f"Merged {len(to_merge)} boxes on page {elem1.page_number} "
                    f"into single {elem1.element_type.value}"
                )
            else:
                merged_elem = elem1

            merged.append(merged_elem)

        return merged

    def _should_merge(self, elem1: Element, elem2: Element) -> bool:
        """
        Determine if two elements should be merged.

        Args:
            elem1: First element
            elem2: Second element

        Returns:
            True if elements should be merged
        """
        bbox1 = elem1.bounding_box
        bbox2 = elem2.bounding_box

        # Check for overlap
        iou = self._calculate_iou(bbox1, bbox2)
        if iou >= self.overlap_threshold:
            logger.debug(f"Merging due to overlap (IoU={iou:.2f})")
            return True

        # Check for proximity (vertically or horizontally close)
        distance = self._calculate_min_distance(bbox1, bbox2)
        if distance <= self.proximity_threshold:
            logger.debug(f"Merging due to proximity (distance={distance:.1f})")
            return True

        return False

    def _calculate_iou(self, bbox1: BoundingBox, bbox2: BoundingBox) -> float:
        """
        Calculate Intersection over Union (IoU) for two bounding boxes.

        Args:
            bbox1: First bounding box
            bbox2: Second bounding box

        Returns:
            IoU value (0.0-1.0)
        """
        # Calculate intersection
        x_left = max(bbox1.x, bbox2.x)
        y_top = max(bbox1.y, bbox2.y)
        x_right = min(bbox1.x2, bbox2.x2)
        y_bottom = min(bbox1.y2, bbox2.y2)

        if x_right < x_left or y_bottom < y_top:
            return 0.0  # No intersection

        intersection_area = (x_right - x_left) * (y_bottom - y_top)

        # Calculate union
        area1 = bbox1.area
        area2 = bbox2.area
        union_area = area1 + area2 - intersection_area

        return intersection_area / union_area if union_area > 0 else 0.0

    def _calculate_min_distance(self, bbox1: BoundingBox, bbox2: BoundingBox) -> float:
        """
        Calculate minimum distance between two bounding boxes.

        Args:
            bbox1: First bounding box
            bbox2: Second bounding box

        Returns:
            Minimum distance in points
        """
        # Calculate horizontal and vertical distances
        if bbox1.x2 < bbox2.x:
            h_distance = bbox2.x - bbox1.x2
        elif bbox2.x2 < bbox1.x:
            h_distance = bbox1.x - bbox2.x2
        else:
            h_distance = 0.0

        if bbox1.y2 < bbox2.y:
            v_distance = bbox2.y - bbox1.y2
        elif bbox2.y2 < bbox1.y:
            v_distance = bbox1.y - bbox2.y2
        else:
            v_distance = 0.0

        # Return minimum of horizontal and vertical distances
        if h_distance == 0.0 and v_distance == 0.0:
            return 0.0  # Overlapping
        elif h_distance == 0.0:
            return v_distance
        elif v_distance == 0.0:
            return h_distance
        else:
            return min(h_distance, v_distance)

    def _create_merged_element(self, elements: List[Element]) -> Element:
        """
        Create a single merged element from multiple elements.

        Args:
            elements: List of elements to merge (must be non-empty)

        Returns:
            Merged element with combined bounding box and highest confidence
        """
        if not elements:
            raise ValueError("Cannot merge empty list of elements")

        # Calculate merged bounding box (minimum bounding rectangle)
        min_x = min(e.bounding_box.x for e in elements)
        min_y = min(e.bounding_box.y for e in elements)
        max_x = max(e.bounding_box.x2 for e in elements)
        max_y = max(e.bounding_box.y2 for e in elements)

        merged_bbox = BoundingBox(
            x=min_x,
            y=min_y,
            width=max_x - min_x,
            height=max_y - min_y,
            page_number=elements[0].page_number,
            padding=elements[0].bounding_box.padding
        )

        # Use highest confidence score
        max_confidence = max(e.confidence_score for e in elements)

        # Create merged element (use first element as template)
        merged = replace(
            elements[0],
            bounding_box=merged_bbox,
            confidence_score=max_confidence
        )

        return merged
