# Library Interface Contract: PDF Element Extractor

**Version**: 1.0.0
**Date**: 2025-11-19
**Stability**: Draft

---

## Overview

This document defines the public interface contract for the PDF Element Extractor library. The library provides a standalone, independently testable API for detecting and extracting figures, tables, and equations from PDF documents.

**Contract Versioning**: This interface follows semantic versioning (MAJOR.MINOR.PATCH)
- MAJOR: Breaking changes to function signatures or behavior
- MINOR: Backward-compatible additions
- PATCH: Bug fixes and clarifications

---

## Core Functions

### 1. `extract_elements`

Primary function for extracting elements from a PDF file.

**Signature**:
```python
def extract_elements(
    pdf_path: str,
    config: Optional[ExtractionConfig] = None
) -> ExtractionResult
```

**Parameters**:
- `pdf_path` (str, required): Absolute or relative path to the input PDF file
  - Must be a valid, accessible PDF file
  - Must have `.pdf` extension
  - File must exist and be readable

- `config` (ExtractionConfig, optional): Configuration for extraction behavior
  - Default: Extract all element types to current directory
  - See ExtractionConfig contract below

**Returns**:
- `ExtractionResult`: Object containing detected elements, success status, and metadata
  - See ExtractionResult contract below

**Raises**:
- `FileNotFoundError`: If pdf_path does not exist
- `PermissionError`: If pdf_path is not readable
- `InvalidPDFError`: If file is not a valid PDF or is corrupted
- `EncryptedPDFError`: If PDF is password-protected and no password provided

**Behavior**:
1. Load and validate PDF file
2. Parse document structure (pages, dimensions)
3. Run detection model on each page
4. Extract detected elements to separate PDFs
5. Return aggregated results

**Performance Contract**:
- Processes 20-page PDF in ≤30 seconds on standard hardware (CPU-only)
- Memory usage ≤500MB for typical academic papers (up to 100 pages)

**Example**:
```python
from pdf_extractor import extract_elements, ExtractionConfig, ElementType

# Basic usage (extract all types)
result = extract_elements("paper.pdf")

# Custom configuration
config = ExtractionConfig(
    element_types=[ElementType.FIGURE],
    output_directory="./figures",
    boundary_padding=10
)
result = extract_elements("paper.pdf", config)

# Result access
print(f"Extracted {result.figure_count} figures")
for element in result.elements:
    print(f"  {element.output_filename}: confidence={element.confidence_score:.2f}")
```

---

### 2. `validate_pdf`

Validates whether a file is a valid, processable PDF.

**Signature**:
```python
def validate_pdf(pdf_path: str) -> ValidationResult
```

**Parameters**:
- `pdf_path` (str, required): Path to PDF file to validate

**Returns**:
- `ValidationResult`: Object with validation status and details
  - `is_valid` (bool): Whether PDF is valid and processable
  - `error_message` (str, optional): Description if invalid
  - `page_count` (int, optional): Number of pages if valid
  - `is_encrypted` (bool): Whether PDF is password-protected

**Raises**:
- `FileNotFoundError`: If pdf_path does not exist

**Example**:
```python
result = validate_pdf("paper.pdf")
if result.is_valid:
    print(f"Valid PDF with {result.page_count} pages")
else:
    print(f"Invalid: {result.error_message}")
```

---

## Data Types

### ExtractionConfig

Configuration object for customizing extraction behavior.

**Fields**:
```python
@dataclass
class ExtractionConfig:
    element_types: List[ElementType] = field(default_factory=lambda: [
        ElementType.FIGURE,
        ElementType.TABLE,
        ElementType.EQUATION
    ])
    output_directory: str = "."
    naming_pattern: str = "{type}_{counter:02d}.pdf"
    boundary_padding: int = 0
    confidence_threshold: float = 0.5
    output_format: OutputFormat = OutputFormat.HUMAN_READABLE
    overwrite_existing: bool = False
    max_pages: Optional[int] = None
```

**Field Constraints**:
- `element_types`: Non-empty list of ElementType enum values
- `output_directory`: Must be valid, writable directory path
- `naming_pattern`: Must contain `{type}` and `{counter}` placeholders
- `boundary_padding`: Integer >= 0 (pixels)
- `confidence_threshold`: Float in range [0.0, 1.0]
- `output_format`: OutputFormat.JSON or OutputFormat.HUMAN_READABLE
- `overwrite_existing`: Boolean
- `max_pages`: Integer > 0 or None

---

### ExtractionResult

Result object returned by `extract_elements`.

**Fields**:
```python
@dataclass
class ExtractionResult:
    document: Document
    elements: List[Element]
    output_directory: str
    success: bool
    extraction_time_seconds: float
    errors: List[str]
    warnings: List[str]

    # Derived properties
    @property
    def figure_count(self) -> int: ...

    @property
    def table_count(self) -> int: ...

    @property
    def equation_count(self) -> int: ...

    @property
    def total_elements(self) -> int: ...
```

**Invariants**:
- If `success` is False, `errors` must be non-empty
- `extraction_time_seconds` >= 0
- `elements` list contains only extracted (saved) elements
- All Element objects have non-null `output_filename`

---

### Element

Represents a single detected and extracted element.

**Fields**:
```python
@dataclass
class Element:
    element_id: str
    element_type: ElementType
    bounding_box: BoundingBox
    page_number: int
    sequence_number: int
    confidence_score: float
    output_filename: str
```

**Invariants**:
- `element_id` is unique (UUID format)
- `element_type` is valid ElementType enum value
- `page_number` >= 1
- `sequence_number` >= 1
- `confidence_score` in range [0.0, 1.0]
- `output_filename` follows naming_pattern from config

---

### ElementType (Enum)

Enumeration of supported element types.

**Values**:
```python
class ElementType(Enum):
    FIGURE = "figure"
    TABLE = "table"
    EQUATION = "equation"
```

**String Conversion**:
- `ElementType.FIGURE.value` → "figure"
- `str(ElementType.FIGURE)` → "figure"

---

### BoundingBox

Rectangular region defining element location on page.

**Fields**:
```python
@dataclass
class BoundingBox:
    x: float
    y: float
    width: float
    height: float
    page_number: int
    padding: int = 0

    @property
    def x2(self) -> float: ...

    @property
    def y2(self) -> float: ...

    @property
    def area(self) -> float: ...

    @property
    def center(self) -> Tuple[float, float]: ...
```

**Invariants**:
- `x`, `y`, `width`, `height` >= 0
- `width`, `height` > 0 (non-zero area)
- `page_number` >= 1
- `padding` >= 0

---

## Output Format Contracts

### JSON Output Format

When `output_format = OutputFormat.JSON`, the library returns structured JSON via CLI.

**Schema**:
```json
{
  "success": true,
  "extraction_time_seconds": 23.45,
  "document": {
    "file_path": "paper.pdf",
    "page_count": 20
  },
  "elements": [
    {
      "element_id": "550e8400-e29b-41d4-a716-446655440000",
      "element_type": "figure",
      "page_number": 5,
      "sequence_number": 2,
      "confidence_score": 0.94,
      "output_filename": "figure_02.pdf",
      "bounding_box": {
        "x": 72.0,
        "y": 150.5,
        "width": 468.0,
        "height": 280.3,
        "page_number": 5
      }
    }
  ],
  "statistics": {
    "figure_count": 8,
    "table_count": 3,
    "equation_count": 12,
    "total_elements": 23
  },
  "errors": [],
  "warnings": ["Element overlap detected on page 5"]
}
```

---

### Human-Readable Output Format

When `output_format = OutputFormat.HUMAN_READABLE`, the library prints formatted text.

**Example**:
```
PDF Element Extraction Complete
================================

Document: paper.pdf (20 pages)
Output Directory: ./output
Extraction Time: 23.45 seconds

Elements Extracted:
  Figures: 8
    - figure_01.pdf (page 2, confidence: 0.96)
    - figure_02.pdf (page 5, confidence: 0.94)
    ...
  Tables: 3
    - table_01.pdf (page 7, confidence: 0.89)
    ...
  Equations: 12
    - equation_01.pdf (page 3, confidence: 0.92)
    ...

Total Elements: 23

Warnings:
  - Element overlap detected on page 5

Status: SUCCESS
```

---

## Error Handling Contract

### Exception Hierarchy

```
PDFExtractorError (base exception)
├── FileNotFoundError (standard Python exception)
├── PermissionError (standard Python exception)
├── InvalidPDFError
│   └── CorruptedPDFError
├── EncryptedPDFError
├── ConfigurationError
│   ├── InvalidOutputDirectoryError
│   └── InvalidNamingPatternError
└── ExtractionFailedError
```

### Exception Details

**InvalidPDFError**:
- Raised when: File is not a valid PDF format
- Message format: "Invalid PDF file: {pdf_path}. {reason}"

**CorruptedPDFError** (subclass of InvalidPDFError):
- Raised when: PDF is damaged or incomplete
- Message format: "Corrupted PDF file: {pdf_path}. {reason}"

**EncryptedPDFError**:
- Raised when: PDF is password-protected
- Message format: "PDF is encrypted: {pdf_path}. Password required."

**ConfigurationError**:
- Raised when: ExtractionConfig has invalid values
- Message format: "Invalid configuration: {field}. {reason}"

**ExtractionFailedError**:
- Raised when: Extraction process encounters fatal error
- Message format: "Extraction failed for {pdf_path}. {reason}"
- Contains: `partial_result` attribute with any successfully extracted elements

---

## Behavioral Contracts

### Detection Accuracy

**Baseline Performance** (v1.0.0):
- **Figures**: 85-90% detection rate on standard academic papers
- **Tables**: 85-90% detection rate with clear boundaries
- **Equations**: 85-90% detection rate for standard mathematical notation

**Confidence Scores**:
- Scores range from 0.0 (no confidence) to 1.0 (maximum confidence)
- Default threshold: 0.5 (elements with score < 0.5 are filtered out)
- Higher threshold → fewer false positives, more false negatives
- Lower threshold → more false positives, fewer false negatives

---

### Naming and Ordering

**Output Filename Pattern**:
- Default: `{type}_{counter:02d}.pdf`
- Type: Lowercase element type (figure, table, equation)
- Counter: Zero-padded 2-digit sequential number per type
- Examples: `figure_01.pdf`, `table_03.pdf`, `equation_15.pdf`

**Sequencing Logic**:
1. Elements ordered by page number (ascending)
2. Within same page: top-to-bottom, left-to-right (reading order)
3. Sequence numbers assigned independently per element type
4. Numbering starts at 01 for each type

---

### Overlap Handling

When multiple elements overlap (IoU > 0.3):
1. Keep element with highest confidence score
2. Discard lower-confidence overlapping elements
3. Add warning to ExtractionResult

---

## Versioning and Compatibility

### Version 1.0.0 Guarantees

- **Interface Stability**: Function signatures will not change
- **Data Format Stability**: JSON output schema will not have breaking changes
- **Behavioral Stability**: Detection logic may improve (accuracy), but core behavior remains consistent

### Future Compatibility

**Planned v1.1.0 Additions** (non-breaking):
- `extract_elements_async()` for parallel processing
- `fine_tune_model()` for domain-specific training
- `export_to_json()` for saving results to file

**Planned v2.0.0 Changes** (breaking):
- Support for password-protected PDFs (new parameter)
- Batch processing of multiple PDFs
- GPU acceleration options

---

## Testing Contract

### Contract Test Requirements

Implementations must pass the following contract tests:

1. **test_extract_elements_basic**: Extract all elements from sample PDF
2. **test_extract_elements_with_config**: Respect custom configuration
3. **test_extract_elements_invalid_pdf**: Raise InvalidPDFError for non-PDF
4. **test_extract_elements_missing_file**: Raise FileNotFoundError
5. **test_output_format_json**: Generate valid JSON output
6. **test_output_format_human_readable**: Generate readable text output
7. **test_confidence_threshold**: Filter elements below threshold
8. **test_naming_pattern**: Follow custom naming pattern
9. **test_boundary_padding**: Apply padding to bounding boxes
10. **test_element_sequencing**: Maintain correct element ordering

### Performance Test Requirements

1. **test_performance_20_pages**: Complete in ≤30 seconds
2. **test_memory_100_pages**: Use ≤500MB memory
3. **test_accuracy_baseline**: Achieve ≥85% detection on test corpus

---

## Example Integration

```python
# Basic usage
from pdf_extractor import extract_elements

result = extract_elements("research_paper.pdf")
if result.success:
    print(f"Extracted {result.total_elements} elements in {result.extraction_time_seconds:.2f}s")
    for element in result.elements:
        print(f"  - {element.output_filename}")
else:
    print(f"Extraction failed: {result.errors}")

# Advanced usage
from pdf_extractor import extract_elements, ExtractionConfig, ElementType, OutputFormat

config = ExtractionConfig(
    element_types=[ElementType.FIGURE, ElementType.TABLE],
    output_directory="./extracted",
    naming_pattern="paper_{type}_{counter:03d}.pdf",
    boundary_padding=15,
    confidence_threshold=0.7,
    output_format=OutputFormat.JSON,
    overwrite_existing=True
)

result = extract_elements("paper.pdf", config)

# Access results
figures = [e for e in result.elements if e.element_type == ElementType.FIGURE]
print(f"Extracted {len(figures)} figures with avg confidence: {
    sum(e.confidence_score for e in figures) / len(figures):.2f
}")
```

---

## Contract Evolution

This contract is versioned and follows semantic versioning principles. Future versions will:
- Maintain backward compatibility within MAJOR versions
- Document all deprecations with migration paths
- Provide clear upgrade guides for MAJOR version changes

**Deprecation Policy**:
- Deprecated features will be marked for at least one MINOR version before removal
- Deprecation warnings will be logged when deprecated features are used
- Documentation will provide migration guidance

---

## Summary

This contract defines a stable, testable interface for the PDF Element Extractor library that:
- Follows Library-First Architecture principles
- Provides clear input/output contracts
- Specifies error handling behavior
- Defines performance expectations
- Supports both JSON and human-readable output formats
- Enables independent testing without CLI dependencies
