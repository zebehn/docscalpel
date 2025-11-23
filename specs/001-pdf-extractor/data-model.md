# Data Model: PDF Element Extractor

**Date**: 2025-11-19
**Feature**: PDF Element Extractor
**Purpose**: Define core entities and their relationships for PDF element detection and extraction

---

## Entity Overview

The PDF Element Extractor system revolves around five core entities:

1. **Document** - Represents the input PDF file
2. **Element** - Represents a detected item (figure, table, or equation)
3. **BoundingBox** - Defines spatial coordinates of an element
4. **ExtractionResult** - Captures the outcome of the extraction process
5. **ExtractionConfig** - Holds user configuration and preferences

---

## Entity Definitions

### 1. Document

Represents the input technical paper PDF file and its metadata.

**Attributes**:
- `file_path` (string): Absolute or relative path to the PDF file
- `page_count` (integer): Total number of pages in the document
- `pages` (list of Page): Collection of individual pages
- `metadata` (dict): PDF metadata (title, author, creation date, etc.)
- `file_size_bytes` (integer): Size of the PDF file
- `is_encrypted` (boolean): Whether the PDF is password-protected

**Relationships**:
- One Document has many Pages
- One Document produces one ExtractionResult

**Validation Rules**:
- `file_path` must point to a valid, accessible PDF file
- `page_count` must be > 0
- Must be a valid PDF format (validated via PyMuPDF)

**State Transitions**:
```
Created → Loaded → Analyzed → Processed → Complete
```

**Example**:
```python
Document(
    file_path="/papers/sample_paper.pdf",
    page_count=20,
    pages=[Page(...), Page(...), ...],
    metadata={"title": "Deep Learning for Document Analysis", "author": "Smith et al."},
    file_size_bytes=2457600,
    is_encrypted=False
)
```

---

### 2. Page

Represents a single page within the PDF document.

**Attributes**:
- `page_number` (integer): 1-indexed page number
- `width` (float): Page width in points (PDF coordinate system)
- `height` (float): Page height in points
- `rotation` (integer): Page rotation angle (0, 90, 180, 270 degrees)
- `elements` (list of Element): Elements detected on this page

**Relationships**:
- One Page belongs to one Document
- One Page has many Elements

**Validation Rules**:
- `page_number` must be between 1 and Document.page_count
- `width` and `height` must be > 0
- `rotation` must be in {0, 90, 180, 270}

---

### 3. Element

Represents a detected item (figure, table, or equation) within the document.

**Attributes**:
- `element_id` (string): Unique identifier (UUID)
- `element_type` (ElementType enum): Type of element (FIGURE, TABLE, EQUATION)
- `bounding_box` (BoundingBox): Spatial coordinates of the element
- `page_number` (integer): Page where element appears
- `sequence_number` (integer): Sequential number within element type (1, 2, 3, ...)
- `confidence_score` (float): Detection confidence (0.0 to 1.0)
- `output_filename` (string): Generated filename for extracted PDF

**Relationships**:
- One Element belongs to one Page
- One Element has one BoundingBox
- Many Elements belong to one ExtractionResult

**Validation Rules**:
- `element_type` must be valid ElementType enum value
- `confidence_score` must be between 0.0 and 1.0
- `sequence_number` must be > 0
- `output_filename` must follow pattern: `{type}_{sequence:02d}.pdf`

**State Transitions**:
```
Detected → Validated → Extracted → Saved
```

**Example**:
```python
Element(
    element_id="550e8400-e29b-41d4-a716-446655440000",
    element_type=ElementType.FIGURE,
    bounding_box=BoundingBox(...),
    page_number=5,
    sequence_number=2,
    confidence_score=0.94,
    output_filename="figure_02.pdf"
)
```

---

### 4. ElementType (Enum)

Enumeration of supported element types.

**Values**:
- `FIGURE`: Images, charts, graphs, diagrams
- `TABLE`: Tabular data with rows and columns
- `EQUATION`: Mathematical formulas and expressions

**String Representation**:
- Maps to lowercase for output filenames: "figure", "table", "equation"

---

### 5. BoundingBox

Defines the rectangular region of an element on a page.

**Attributes**:
- `x` (float): X-coordinate of top-left corner (PDF points)
- `y` (float): Y-coordinate of top-left corner (PDF points)
- `width` (float): Width of the bounding box (PDF points)
- `height` (float): Height of the bounding box (PDF points)
- `page_number` (integer): Reference to the page
- `padding` (integer): Additional padding around element (pixels, default: 0)

**Relationships**:
- One BoundingBox belongs to one Element

**Validation Rules**:
- All coordinates must be >= 0
- `width` and `height` must be > 0
- Coordinates must be within page bounds
- `padding` must be >= 0

**Derived Properties**:
- `x2`: Right edge (x + width)
- `y2`: Bottom edge (y + height)
- `area`: Total area (width × height)
- `center`: Center point ((x + width/2), (y + height/2))

**Example**:
```python
BoundingBox(
    x=72.0,
    y=150.5,
    width=468.0,
    height=280.3,
    page_number=5,
    padding=10
)
```

---

### 6. ExtractionResult

Represents the outcome of the entire extraction process.

**Attributes**:
- `document` (Document): Reference to source document
- `elements` (list of Element): All detected and extracted elements
- `output_directory` (string): Path where extracted files are saved
- `success` (boolean): Overall success status
- `extraction_time_seconds` (float): Time taken for extraction
- `errors` (list of string): Error messages if any failures occurred
- `warnings` (list of string): Non-fatal warnings

**Relationships**:
- One ExtractionResult corresponds to one Document
- One ExtractionResult contains many Elements

**Derived Properties**:
- `figure_count`: Count of elements with type FIGURE
- `table_count`: Count of elements with type TABLE
- `equation_count`: Count of elements with type EQUATION
- `total_elements`: Total count of all elements

**Validation Rules**:
- `output_directory` must be writable
- `extraction_time_seconds` must be >= 0
- If `success` is False, `errors` must be non-empty

**Example**:
```python
ExtractionResult(
    document=Document(...),
    elements=[Element(...), Element(...), ...],
    output_directory="/output/extracted",
    success=True,
    extraction_time_seconds=23.45,
    errors=[],
    warnings=["Element overlap detected on page 5"]
)
```

---

### 7. ExtractionConfig

Holds user preferences and configuration for the extraction process.

**Attributes**:
- `element_types` (list of ElementType): Types to extract (default: all)
- `output_directory` (string): Target directory for extracted files (default: current directory)
- `naming_pattern` (string): Template for output filenames (default: "{type}_{counter:02d}.pdf")
- `boundary_padding` (integer): Pixels to add around detected boundaries (default: 0)
- `confidence_threshold` (float): Minimum confidence for accepting detection (default: 0.5)
- `output_format` (OutputFormat enum): CLI output format (JSON or HUMAN_READABLE)
- `overwrite_existing` (boolean): Whether to overwrite existing output files (default: False)
- `max_pages` (integer, optional): Maximum pages to process (None = all)

**Validation Rules**:
- `element_types` must not be empty
- `output_directory` must be a valid path
- `naming_pattern` must contain `{type}` and `{counter}` placeholders
- `boundary_padding` must be >= 0
- `confidence_threshold` must be between 0.0 and 1.0
- `max_pages` must be > 0 if specified

**Default Configuration**:
```python
ExtractionConfig(
    element_types=[ElementType.FIGURE, ElementType.TABLE, ElementType.EQUATION],
    output_directory=".",
    naming_pattern="{type}_{counter:02d}.pdf",
    boundary_padding=0,
    confidence_threshold=0.5,
    output_format=OutputFormat.HUMAN_READABLE,
    overwrite_existing=False,
    max_pages=None
)
```

---

### 8. OutputFormat (Enum)

Enumeration for CLI output format options.

**Values**:
- `JSON`: Machine-readable JSON format
- `HUMAN_READABLE`: Human-friendly text format

---

## Entity Relationships Diagram

```
Document (1) ─────── has many ─────── (N) Page
   │                                      │
   │                                      │
   │                            has many  │
   │                               (N) Element
   │                                      │
   │                                      │
   │                            has one   │
   │                                (1) BoundingBox
   │
   │
produces one
   │
   │
   (1) ExtractionResult
         │
         │ contains many
         │
         (N) Element


ExtractionConfig ─── configures ─── Extraction Process
```

---

## Data Flow

```
1. User provides:
   - PDF file path
   - ExtractionConfig (optional)

2. System creates:
   - Document (from PDF)
   - Pages (parsed from PDF)

3. Detection phase:
   - DocLayout-YOLO analyzes each Page
   - Creates Element for each detection
   - Assigns BoundingBox to each Element

4. Extraction phase:
   - For each Element:
     - Crop region using BoundingBox
     - Generate output PDF file
     - Set output_filename

5. Result aggregation:
   - Create ExtractionResult
   - Populate with all Elements
   - Record success/errors
   - Return to user
```

---

## Validation and Constraints

### Cross-Entity Constraints

1. **Element Ordering**: Elements of the same type must have unique, sequential sequence_numbers
2. **Bounding Box Boundaries**: BoundingBox coordinates must be within the corresponding Page dimensions
3. **Output Uniqueness**: No two Elements can have the same output_filename
4. **Page References**: All Element.page_number values must exist in Document.pages
5. **Confidence Filtering**: Elements with confidence_score < ExtractionConfig.confidence_threshold are excluded

### Business Rules

1. **Naming Convention**: Output files follow strict pattern: `{type}_{sequence:02d}.pdf`
   - `type`: Lowercase element type ("figure", "table", "equation")
   - `sequence`: Zero-padded 2-digit number (01, 02, ..., 99)
   - Extension: Always ".pdf"

2. **Element Ordering**: Elements are sequenced by reading order (top-to-bottom, left-to-right) within each page, then by page number

3. **Overlap Handling**: When BoundingBoxes overlap, only the element with higher confidence_score is extracted (duplicate prevention)

4. **Error Handling**:
   - Invalid PDF → ExtractionResult.success = False, errors populated
   - No elements detected → ExtractionResult.success = True, elements = [], warning added
   - Extraction failure for specific element → warning added, continue with remaining elements

---

## Example Complete Workflow

```python
# Input
config = ExtractionConfig(
    element_types=[ElementType.FIGURE],
    output_directory="/output",
    boundary_padding=10
)

# Processing
document = Document(file_path="paper.pdf", page_count=20, ...)
page5 = document.pages[4]  # Page 5 (0-indexed)

element = Element(
    element_type=ElementType.FIGURE,
    bounding_box=BoundingBox(x=72, y=150, width=468, height=280, page_number=5),
    page_number=5,
    sequence_number=2,
    confidence_score=0.94,
    output_filename="figure_02.pdf"
)

# Output
result = ExtractionResult(
    document=document,
    elements=[element],
    output_directory="/output",
    success=True,
    extraction_time_seconds=23.45,
    errors=[],
    warnings=[]
)

# Files Created:
# /output/figure_02.pdf
```

---

## Technology Mapping

| Entity | Python Type | Primary Library |
|--------|-------------|-----------------|
| Document | Class | PyMuPDF (fitz) |
| Page | Class | PyMuPDF (fitz.Page) |
| Element | Class | Custom dataclass |
| ElementType | Enum | Python enum.Enum |
| BoundingBox | Class | Custom dataclass |
| ExtractionResult | Class | Custom dataclass |
| ExtractionConfig | Class | Custom dataclass |
| OutputFormat | Enum | Python enum.Enum |

**Note**: While technology mapping is provided for clarity, this data model document remains implementation-agnostic and focuses on the logical structure of entities.
