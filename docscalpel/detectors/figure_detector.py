"""
Figure detector module using DocLayout-YOLO.

Detects figures and images in PDF pages using the state-of-the-art
DocLayout-YOLO deep learning model.
"""

from typing import List
import logging

try:
    from doclayout_yolo import YOLOv10
except ImportError:
    raise ImportError(
        "doclayout-yolo is required. Install with: pip install doclayout-yolo"
    )

try:
    from huggingface_hub import hf_hub_download
except ImportError:
    raise ImportError(
        "huggingface-hub is required. Install with: pip install huggingface-hub"
    )

from ..models import Element, ElementType, BoundingBox, Page, create_element

logger = logging.getLogger(__name__)


class FigureDetector:
    """
    Detector for figures and images in PDF pages.

    Uses DocLayout-YOLO model for high-accuracy figure detection.
    Filters results by confidence threshold.
    """

    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize FigureDetector with DocLayout-YOLO model.

        Args:
            confidence_threshold: Minimum confidence score (0.0-1.0) for detections
        """
        self.confidence_threshold = confidence_threshold
        self._model = None
        self._model_loaded = False

    @property
    def model(self):
        """Lazy-load the DocLayout-YOLO model."""
        if not self._model_loaded:
            try:
                logger.info("Loading DocLayout-YOLO model for figure detection...")
                # Download model from Hugging Face
                model_path = hf_hub_download(
                    repo_id="juliozhao/DocLayout-YOLO-DocStructBench",
                    filename="doclayout_yolo_docstructbench_imgsz1024.pt"
                )
                self._model = YOLOv10(model_path)
                self._model_loaded = True
                logger.info("DocLayout-YOLO model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load DocLayout-YOLO model: {e}")
                raise RuntimeError(
                    f"Failed to load DocLayout-YOLO model for figure detection: {e}"
                )
        return self._model

    def detect(self, page: Page, pdf_path: str = None, detect_captions: bool = True) -> List[Element]:
        """
        Detect figures in a PDF page.

        Args:
            page: Page object to analyze
            pdf_path: Path to PDF file (required for rendering)
            detect_captions: Whether to also detect and store caption bounding boxes

        Returns:
            List of Element objects with type FIGURE, filtered by confidence threshold

        Raises:
            ValueError: If page is None or invalid
            RuntimeError: If detection fails

        Example:
            >>> detector = FigureDetector(confidence_threshold=0.8)
            >>> elements = detector.detect(page)
            >>> print(f"Found {len(elements)} figures")
        """
        if page is None:
            raise ValueError("Page cannot be None")

        elements: List[Element] = []
        # Store caption bboxes temporarily for later processing
        self._caption_bboxes = []

        try:
            logger.debug(
                f"Figure detection on page {page.page_number} "
                f"(threshold={self.confidence_threshold})"
            )

            # Render page to image for YOLO inference
            if pdf_path is None:
                logger.warning(f"PDF path not provided, cannot render page {page.page_number}")
                return elements

            page_image, zoom_factor = self._render_page_to_image(pdf_path, page.page_number)

            if page_image is None:
                logger.warning(f"Failed to render page {page.page_number} to image")
                return elements

            # Run DocLayout-YOLO inference
            results = self.model.predict(
                page_image,
                imgsz=1024,  # Image size for inference
                conf=self.confidence_threshold,  # Confidence threshold
                device='cpu'  # Use CPU (can be changed to 'cuda' for GPU)
            )

            # Parse detection results
            if results and len(results) > 0:
                detections = results[0]  # First result (single image)

                # Extract bounding boxes, classes, and confidences
                if hasattr(detections, 'boxes'):
                    boxes = detections.boxes

                    for i in range(len(boxes)):
                        # Get class name
                        class_id = int(boxes.cls[i])
                        class_name = detections.names[class_id] if hasattr(detections, 'names') else ""

                        confidence = float(boxes.conf[i])

                        # Get bounding box coordinates (xyxy format)
                        bbox_coords = boxes.xyxy[i].cpu().numpy()
                        x1, y1, x2, y2 = bbox_coords

                        # Scale coordinates back to original PDF dimensions
                        scale_factor = 1.0 / zoom_factor
                        x1_scaled = float(x1) * scale_factor
                        y1_scaled = float(y1) * scale_factor
                        x2_scaled = float(x2) * scale_factor
                        y2_scaled = float(y2) * scale_factor

                        # Create BoundingBox with scaled coordinates
                        bbox = BoundingBox(
                            x=x1_scaled,
                            y=y1_scaled,
                            width=x2_scaled - x1_scaled,
                            height=y2_scaled - y1_scaled,
                            page_number=page.page_number,
                            padding=0
                        )

                        # Filter for figures (class name may vary: "figure", "Figure", etc.)
                        if class_name.lower() in ['figure', 'fig', 'image', 'picture']:
                            # Create Element
                            element = create_element(
                                element_type=ElementType.FIGURE,
                                bounding_box=bbox,
                                page_number=page.page_number,
                                sequence_number=1,  # Placeholder, will be reassigned by extractor
                                confidence_score=confidence,
                                output_filename=""  # Will be generated by extractor
                            )

                            elements.append(element)
                            logger.debug(
                                f"Detected figure on page {page.page_number}: "
                                f"confidence={confidence:.2f}, bbox=({x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f})"
                            )

                        # Detect captions if requested
                        elif detect_captions and class_name.lower() in ['figure_caption', 'caption']:
                            self._caption_bboxes.append((bbox, ElementType.FIGURE))
                            logger.debug(
                                f"Detected figure caption on page {page.page_number}: "
                                f"confidence={confidence:.2f}, bbox=({x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f})"
                            )

            logger.debug(f"Found {len(elements)} figures on page {page.page_number}")
            return elements

        except Exception as e:
            logger.error(f"Detection failed on page {page.page_number}: {e}")
            # Return empty list on failure (graceful degradation)
            return []

    def get_caption_bboxes(self) -> List:
        """
        Get detected caption bounding boxes from the last detection.

        Returns:
            List of tuples (BoundingBox, ElementType) for detected captions
        """
        return getattr(self, '_caption_bboxes', [])

    def _render_page_to_image(self, pdf_path: str, page_number: int):
        """
        Render a PDF page to an image for YOLO inference.

        Args:
            pdf_path: Path to the PDF file
            page_number: Page number to render (1-indexed)

        Returns:
            Tuple of (PIL Image, zoom_factor) or (None, None) on error
        """
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            import io
            import numpy as np

            logger.debug(f"Rendering page {page_number} from {pdf_path}")

            # Open PDF document
            doc = fitz.open(pdf_path)

            # Get page (convert to 0-indexed)
            page_idx = page_number - 1
            if page_idx < 0 or page_idx >= len(doc):
                logger.error(f"Page {page_number} out of range for PDF with {len(doc)} pages")
                doc.close()
                return None, None

            page = doc[page_idx]

            # Render page to image at high resolution for better detection
            # zoom = 2.0 means 2x resolution (144 DPI instead of 72 DPI)
            zoom = 2.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))

            doc.close()

            logger.debug(f"Rendered page {page_number} to image: {image.size} (zoom={zoom})")
            return image, zoom

        except Exception as e:
            logger.error(f"Failed to render page {page_number}: {e}")
            return None, None

    def _create_element_from_detection(
        self,
        detection: dict,
        page_number: int
    ) -> Element:
        """
        Convert a raw detection result to an Element object.

        Args:
            detection: Detection dict from DocLayout-YOLO with bbox and confidence
            page_number: Page number where element was detected

        Returns:
            Element object with FIGURE type
        """
        # Extract bounding box coordinates
        x, y, width, height = detection['bbox']
        confidence = detection['confidence']

        # Create BoundingBox
        bbox = BoundingBox(
            x=float(x),
            y=float(y),
            width=float(width),
            height=float(height),
            page_number=page_number,
            padding=0
        )

        # Create Element (sequence_number and output_filename will be set by extractor)
        element = create_element(
            element_type=ElementType.FIGURE,
            bounding_box=bbox,
            page_number=page_number,
            sequence_number=0,  # Placeholder, will be reassigned
            confidence_score=float(confidence),
            output_filename=""  # Placeholder, will be generated
        )

        return element
