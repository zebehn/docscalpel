"""
Detector modules for identifying elements in PDF pages.

This package contains specialized detectors for different element types:
- FigureDetector: Detects figures and images
- TableDetector: Detects tables
- EquationDetector: Detects mathematical equations

All detectors use the DocLayout-YOLO model for high-accuracy detection.
"""

from .figure_detector import FigureDetector
from .table_detector import TableDetector
from .equation_detector import EquationDetector

__all__ = [
    "FigureDetector",
    "TableDetector",
    "EquationDetector",
]
