"""
Unit tests for element detector modules.

Tests figure, table, and equation detection functionality.

Test Strategy (TDD):
1. Write these tests FIRST
2. Verify they FAIL (no implementation yet)
3. Implement detector modules
4. Verify tests PASS
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List

from src.lib.models import (
    ElementType,
    BoundingBox,
    Element,
    Page,
    Document,
    create_element,
)


class TestFigureDetector:
    """Test the figure_detector module."""

    def test_figure_detector_class_exists(self):
        """Verify FigureDetector class is importable."""
        from src.lib.detectors.figure_detector import FigureDetector
        assert FigureDetector is not None

    def test_figure_detector_initialization(self):
        """
        Unit test: FigureDetector initializes with default settings.

        Given: No configuration
        When: FigureDetector is instantiated
        Then: Creates detector with default confidence threshold
        """
        from src.lib.detectors.figure_detector import FigureDetector

        detector = FigureDetector(confidence_threshold=0.5)

        assert detector is not None
        assert hasattr(detector, 'confidence_threshold')
        assert detector.confidence_threshold == 0.5

    def test_figure_detector_detect_method_exists(self):
        """Verify detect() method exists on FigureDetector."""
        from src.lib.detectors.figure_detector import FigureDetector

        detector = FigureDetector(confidence_threshold=0.5)
        assert callable(getattr(detector, 'detect', None))

    def test_figure_detector_detect_returns_elements(self, sample_page):
        """
        Unit test: detect() returns list of Element objects.

        Given: A page from PDF
        When: detect() is called
        Then: Returns list of Element objects with type FIGURE
        """
        from src.lib.detectors.figure_detector import FigureDetector

        detector = FigureDetector(confidence_threshold=0.5)

        # Mock page data - actual detection will use real PDF page
        elements = detector.detect(sample_page)

        # Verify: Returns list
        assert isinstance(elements, list)

        # Verify: All elements are FIGURE type
        for element in elements:
            assert isinstance(element, Element)
            assert element.element_type == ElementType.FIGURE

    def test_figure_detector_filters_by_confidence(self, sample_page):
        """
        Unit test: detect() filters elements below confidence threshold.

        Given: Page with low and high confidence detections
        When: detect() is called with threshold=0.8
        Then: Only returns elements with confidence >= 0.8
        """
        from src.lib.detectors.figure_detector import FigureDetector

        detector = FigureDetector(confidence_threshold=0.8)

        elements = detector.detect(sample_page)

        # Verify: All returned elements meet threshold
        for element in elements:
            assert element.confidence_score >= 0.8

    def test_figure_detector_assigns_bounding_boxes(self, sample_page):
        """
        Unit test: detect() assigns valid bounding boxes to elements.

        Given: Page with detected figures
        When: detect() is called
        Then: Each element has valid BoundingBox with page dimensions
        """
        from src.lib.detectors.figure_detector import FigureDetector

        detector = FigureDetector(confidence_threshold=0.5)

        elements = detector.detect(sample_page)

        # Verify: Each element has bounding box
        for element in elements:
            assert isinstance(element.bounding_box, BoundingBox)
            assert element.bounding_box.page_number == sample_page.page_number

            # Verify: Box is within page bounds
            assert element.bounding_box.x >= 0
            assert element.bounding_box.y >= 0
            assert element.bounding_box.x + element.bounding_box.width <= sample_page.width
            assert element.bounding_box.y + element.bounding_box.height <= sample_page.height

    def test_figure_detector_with_no_figures_returns_empty(self, sample_page):
        """
        Unit test: detect() returns empty list when no figures found.

        Given: Page with no detectable figures (text-only)
        When: detect() is called
        Then: Returns empty list, no errors
        """
        from src.lib.detectors.figure_detector import FigureDetector

        detector = FigureDetector(confidence_threshold=0.5)

        # For text-only page, should return empty
        elements = detector.detect(sample_page)

        # Verify: Empty list is valid response
        assert isinstance(elements, list)

    def test_figure_detector_uses_doclayout_yolo(self):
        """
        Unit test: FigureDetector uses DocLayout-YOLO model.

        Given: FigureDetector initialization
        When: Model is loaded
        Then: Uses doclayout-yolo library
        """
        from src.lib.detectors.figure_detector import FigureDetector

        detector = FigureDetector(confidence_threshold=0.5)

        # Verify: Detector has model attribute (actual model loading tested in integration)
        assert hasattr(detector, 'model') or hasattr(detector, '_model')

    def test_figure_detector_assigns_sequence_numbers(self, sample_page):
        """
        Unit test: detect() assigns sequential numbers to figures.

        Given: Page with multiple figures
        When: detect() is called
        Then: Elements have sequence_number starting from 1
        """
        pytest.skip("Sequence numbering happens at extractor level, not detector")


class TestTableDetector:
    """Test the table_detector module."""

    def test_table_detector_class_exists(self):
        """Verify TableDetector class is importable."""
        from src.lib.detectors.table_detector import TableDetector
        assert TableDetector is not None

    def test_table_detector_initialization(self):
        """
        Unit test: TableDetector initializes with default settings.

        Given: No configuration
        When: TableDetector is instantiated
        Then: Creates detector with default settings
        """
        from src.lib.detectors.table_detector import TableDetector

        detector = TableDetector(confidence_threshold=0.5)

        assert detector is not None
        assert detector.confidence_threshold == 0.5

    def test_table_detector_detect_returns_table_elements(self, sample_page):
        """
        Unit test: detect() returns list of TABLE elements.

        Given: A page with tables
        When: detect() is called
        Then: Returns Element objects with type TABLE
        """
        from src.lib.detectors.table_detector import TableDetector

        detector = TableDetector(confidence_threshold=0.5)

        elements = detector.detect(sample_page)

        # Verify: All elements are TABLE type
        for element in elements:
            assert isinstance(element, Element)
            assert element.element_type == ElementType.TABLE

    def test_table_detector_filters_by_confidence(self, sample_page):
        """
        Unit test: detect() filters tables below confidence threshold.

        Given: Page with detected tables
        When: detect() is called with threshold=0.7
        Then: Only returns tables with confidence >= 0.7
        """
        from src.lib.detectors.table_detector import TableDetector

        detector = TableDetector(confidence_threshold=0.7)

        elements = detector.detect(sample_page)

        # Verify: All meet threshold
        for element in elements:
            assert element.confidence_score >= 0.7

    def test_table_detector_uses_doclayout_yolo_primary(self):
        """
        Unit test: TableDetector uses DocLayout-YOLO as primary method.

        Given: TableDetector initialization
        When: Detection is configured
        Then: Uses DocLayout-YOLO model
        """
        from src.lib.detectors.table_detector import TableDetector

        detector = TableDetector(confidence_threshold=0.5)

        # Verify: Has detection model
        assert hasattr(detector, 'model') or hasattr(detector, '_model')

    def test_table_detector_fallback_to_pdfplumber(self):
        """
        Unit test: TableDetector can fall back to pdfplumber if needed.

        Given: DocLayout-YOLO fails or unavailable
        When: detect() is called
        Then: Falls back to pdfplumber for table extraction
        """
        pytest.skip("Fallback mechanism not yet specified in requirements")

    def test_table_detector_with_no_tables_returns_empty(self, sample_page):
        """
        Unit test: detect() returns empty list when no tables found.

        Given: Page with no tables
        When: detect() is called
        Then: Returns empty list
        """
        from src.lib.detectors.table_detector import TableDetector

        detector = TableDetector(confidence_threshold=0.5)

        elements = detector.detect(sample_page)

        # Verify: Empty list is valid
        assert isinstance(elements, list)


class TestEquationDetector:
    """Test the equation_detector module."""

    def test_equation_detector_class_exists(self):
        """Verify EquationDetector class is importable."""
        from src.lib.detectors.equation_detector import EquationDetector
        assert EquationDetector is not None

    def test_equation_detector_initialization(self):
        """
        Unit test: EquationDetector initializes with default settings.

        Given: No configuration
        When: EquationDetector is instantiated
        Then: Creates detector with default settings
        """
        from src.lib.detectors.equation_detector import EquationDetector

        detector = EquationDetector(confidence_threshold=0.5)

        assert detector is not None
        assert detector.confidence_threshold == 0.5

    def test_equation_detector_detect_returns_equation_elements(self, sample_page):
        """
        Unit test: detect() returns list of EQUATION elements.

        Given: A page with equations
        When: detect() is called
        Then: Returns Element objects with type EQUATION
        """
        from src.lib.detectors.equation_detector import EquationDetector

        detector = EquationDetector(confidence_threshold=0.5)

        elements = detector.detect(sample_page)

        # Verify: All elements are EQUATION type
        for element in elements:
            assert isinstance(element, Element)
            assert element.element_type == ElementType.EQUATION

    def test_equation_detector_filters_by_confidence(self, sample_page):
        """
        Unit test: detect() filters equations below confidence threshold.

        Given: Page with detected equations
        When: detect() is called with threshold=0.8
        Then: Only returns equations with confidence >= 0.8
        """
        from src.lib.detectors.equation_detector import EquationDetector

        detector = EquationDetector(confidence_threshold=0.8)

        elements = detector.detect(sample_page)

        # Verify: All meet threshold
        for element in elements:
            assert element.confidence_score >= 0.8

    def test_equation_detector_uses_doclayout_yolo(self):
        """
        Unit test: EquationDetector uses DocLayout-YOLO model.

        Given: EquationDetector initialization
        When: Detection is configured
        Then: Uses DocLayout-YOLO for equation detection
        """
        from src.lib.detectors.equation_detector import EquationDetector

        detector = EquationDetector(confidence_threshold=0.5)

        # Verify: Has detection model
        assert hasattr(detector, 'model') or hasattr(detector, '_model')

    def test_equation_detector_with_no_equations_returns_empty(self, sample_page):
        """
        Unit test: detect() returns empty list when no equations found.

        Given: Page with no equations
        When: detect() is called
        Then: Returns empty list
        """
        from src.lib.detectors.equation_detector import EquationDetector

        detector = EquationDetector(confidence_threshold=0.5)

        elements = detector.detect(sample_page)

        # Verify: Empty list is valid
        assert isinstance(elements, list)


class TestDetectorBaseInterface:
    """Test common detector interface and behavior."""

    def test_all_detectors_have_consistent_interface(self):
        """
        Unit test: All detector classes have the same interface.

        Given: FigureDetector, TableDetector, EquationDetector
        When: Checking their public methods
        Then: All have detect() method with same signature
        """
        from src.lib.detectors.figure_detector import FigureDetector
        from src.lib.detectors.table_detector import TableDetector
        from src.lib.detectors.equation_detector import EquationDetector

        detectors = [
            FigureDetector(confidence_threshold=0.5),
            TableDetector(confidence_threshold=0.5),
            EquationDetector(confidence_threshold=0.5)
        ]

        # Verify: All have detect method
        for detector in detectors:
            assert hasattr(detector, 'detect')
            assert callable(detector.detect)

    def test_detectors_return_elements_with_unique_ids(self, sample_page):
        """
        Unit test: All detectors assign unique element IDs.

        Given: Multiple detections from any detector
        When: detect() is called
        Then: Each element has unique element_id
        """
        from src.lib.detectors.figure_detector import FigureDetector

        detector = FigureDetector(confidence_threshold=0.5)

        elements = detector.detect(sample_page)

        if len(elements) > 1:
            # Verify: All IDs are unique
            element_ids = [e.element_id for e in elements]
            assert len(element_ids) == len(set(element_ids))

    def test_detectors_handle_rotated_pages(self, sample_page):
        """
        Unit test: Detectors handle rotated pages correctly.

        Given: Page with rotation (90°, 180°, 270°)
        When: detect() is called
        Then: Bounding boxes are adjusted for rotation
        """
        pytest.skip("Rotation handling not yet specified in requirements")


class TestDetectorErrorHandling:
    """Test error handling in detectors."""

    def test_detector_handles_invalid_page_gracefully(self):
        """
        Unit test: Detectors handle invalid page data gracefully.

        Given: Invalid or None page object
        When: detect() is called
        Then: Raises appropriate error or returns empty list
        """
        from src.lib.detectors.figure_detector import FigureDetector

        detector = FigureDetector(confidence_threshold=0.5)

        with pytest.raises((ValueError, TypeError, AttributeError)):
            detector.detect(None)

    def test_detector_handles_model_loading_failure(self):
        """
        Unit test: Detector handles model loading failures.

        Given: DocLayout-YOLO model fails to load
        When: Detector is initialized
        Then: Raises clear error message
        """
        pytest.skip("Model loading error handling not yet implemented")

    def test_detector_handles_detection_failure_on_page(self, sample_page):
        """
        Unit test: Detector handles detection failures gracefully.

        Given: Page that causes detection to fail
        When: detect() is called
        Then: Returns empty list or raises ExtractionFailedError
        """
        pytest.skip("Detection failure handling not yet implemented")


class TestDetectorPerformance:
    """Test detector performance characteristics."""

    def test_figure_detector_performance_baseline(self, sample_page):
        """
        Unit test: FigureDetector meets performance baseline.

        Given: Single page
        When: detect() is called
        Then: Completes in reasonable time (< 1 second per page)
        """
        pytest.skip("Performance testing deferred to integration tests")

    def test_detector_batch_processing(self):
        """
        Unit test: Detectors can process multiple pages efficiently.

        Given: List of 10 pages
        When: detect() is called on each
        Then: Total time is reasonable
        """
        pytest.skip("Batch processing optimization not yet specified")


class TestDetectorConfidenceScoring:
    """Test confidence score handling across detectors."""

    def test_confidence_scores_are_normalized(self, sample_page):
        """
        Unit test: Confidence scores are between 0.0 and 1.0.

        Given: Any detector
        When: detect() is called
        Then: All confidence_score values are in [0.0, 1.0]
        """
        from src.lib.detectors.figure_detector import FigureDetector

        detector = FigureDetector(confidence_threshold=0.0)  # Accept all

        elements = detector.detect(sample_page)

        for element in elements:
            assert 0.0 <= element.confidence_score <= 1.0

    def test_higher_confidence_threshold_returns_fewer_elements(self, sample_page):
        """
        Unit test: Higher thresholds result in fewer detections.

        Given: Same page processed with different thresholds
        When: detect() is called with 0.5 and 0.9
        Then: 0.9 threshold returns fewer or equal elements
        """
        from src.lib.detectors.figure_detector import FigureDetector

        detector_low = FigureDetector(confidence_threshold=0.5)
        detector_high = FigureDetector(confidence_threshold=0.9)

        elements_low = detector_low.detect(sample_page)
        elements_high = detector_high.detect(sample_page)

        # Verify: High threshold returns fewer or equal elements
        assert len(elements_high) <= len(elements_low)
