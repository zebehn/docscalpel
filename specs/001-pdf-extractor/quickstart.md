# Quickstart Guide: PDF Element Extractor

**Date**: 2025-11-19
**Feature**: PDF Element Extractor
**Purpose**: Practical guide for developers to understand, test, and validate the PDF element extraction system

---

## Overview

The PDF Element Extractor is a library + CLI application that detects and extracts figures, tables, and equations from technical papers. This quickstart provides concrete examples for testing each user story independently.

---

## Prerequisites

**System Requirements**:
- Python 3.11+
- 500MB free memory
- Write access to output directories

**Dependencies** (install before testing):
```bash
pip install pymupdf doclayout-yolo pdfplumber pytest pillow
```

---

## Project Structure

```
figure-extractor/
├── src/
│   ├── lib/                  # Core extraction library
│   │   ├── extractor.py      # Main extraction orchestrator
│   │   ├── detectors/        # Element detection
│   │   ├── pdf_processor.py  # PDF parsing
│   │   ├── cropper.py        # PDF cropping
│   │   └── models.py         # Data models
│   └── cli/                  # CLI application
│       ├── main.py           # CLI entry point
│       ├── formatter.py      # Output formatting
│       └── logger.py         # Logging
├── tests/
│   ├── contract/             # Library interface tests
│   ├── integration/          # Component integration tests
│   └── unit/                 # Unit tests
└── fixtures/                 # Test PDF files
```

---

## User Story 1: Extract Single Element Type (P1)

**Goal**: Extract all figures from a PDF to use in a presentation

### Test Scenario 1.1: Extract figures from 3-figure PDF

**Given**: A technical paper PDF with 3 figures

**When**: User runs extraction for figures

**Then**: System creates 3 files (figure_01.pdf, figure_02.pdf, figure_03.pdf)

**Test Commands**:
```bash
# Library usage
python << 'EOF'
from src.lib.extractor import extract_elements
from src.lib.models import ExtractionConfig, ElementType

config = ExtractionConfig(
    element_types=[ElementType.FIGURE],
    output_directory="./test_output"
)

result = extract_elements("fixtures/sample_paper_with_figures.pdf", config)

assert result.success == True
assert result.figure_count == 3
assert len(result.elements) == 3

for i, element in enumerate(result.elements, 1):
    assert element.output_filename == f"figure_{i:02d}.pdf"
    assert element.element_type == ElementType.FIGURE

print("✓ Test 1.1 passed: 3 figures extracted")
EOF

# CLI usage
pdf-extractor --types figure --output ./test_output fixtures/sample_paper_with_figures.pdf

# Verify outputs
ls -1 ./test_output/
# Expected:
# figure_01.pdf
# figure_02.pdf
# figure_03.pdf
```

**Expected Output** (CLI text format):
```
PDF Element Extraction Complete
================================

Document: sample_paper_with_figures.pdf (10 pages)
Output Directory: ./test_output
Extraction Time: 8.23 seconds

Elements Extracted:
  Figures: 3
    - figure_01.pdf (page 2, confidence: 0.96)
    - figure_02.pdf (page 5, confidence: 0.94)
    - figure_03.pdf (page 8, confidence: 0.91)

Total Elements: 3

Status: SUCCESS
```

---

### Test Scenario 1.2: No figures detected

**Given**: A PDF with no figures

**When**: User runs extraction

**Then**: System reports "No figures detected" and creates no files

**Test Commands**:
```bash
# Library usage
python << 'EOF'
from src.lib.extractor import extract_elements
from src.lib.models import ExtractionConfig, ElementType

config = ExtractionConfig(element_types=[ElementType.FIGURE])
result = extract_elements("fixtures/text_only_paper.pdf", config)

assert result.success == True
assert result.figure_count == 0
assert len(result.elements) == 0

print("✓ Test 1.2 passed: No figures detected correctly")
EOF

# CLI usage
pdf-extractor --types figure fixtures/text_only_paper.pdf
```

**Expected Output**:
```
PDF Element Extraction Complete
================================

Document: text_only_paper.pdf (5 pages)
Output Directory: .
Extraction Time: 3.12 seconds

Elements Extracted:
  Figures: 0

Total Elements: 0

Warnings:
  - No elements of requested types detected

Status: SUCCESS
```

---

### Test Scenario 1.3: Zero-padded numbering (10 figures)

**Given**: A PDF with 10 figures

**When**: User runs extraction

**Then**: Files numbered from figure_01.pdf to figure_10.pdf with consistent padding

**Test Commands**:
```bash
# Library usage
python << 'EOF'
from src.lib.extractor import extract_elements
from src.lib.models import ElementType

result = extract_elements("fixtures/paper_10_figures.pdf")

assert result.figure_count == 10
assert result.elements[0].output_filename == "figure_01.pdf"
assert result.elements[9].output_filename == "figure_10.pdf"

print("✓ Test 1.3 passed: Zero-padding maintained for 10 figures")
EOF

# CLI verification
pdf-extractor --types figure fixtures/paper_10_figures.pdf
ls -1 figure_*.pdf | wc -l  # Should be 10
```

---

## User Story 2: Extract Multiple Element Types (P2)

**Goal**: Extract all visual and mathematical content (figures, tables, equations)

### Test Scenario 2.1: Extract multiple types

**Given**: A PDF with 2 figures, 3 tables, 1 equation

**When**: User requests extraction of all types

**Then**: System creates 6 files with type-specific naming

**Test Commands**:
```bash
# Library usage
python << 'EOF'
from src.lib.extractor import extract_elements
from src.lib.models import ElementType

result = extract_elements("fixtures/sample_paper_mixed.pdf")

assert result.figure_count == 2
assert result.table_count == 3
assert result.equation_count == 1
assert result.total_elements == 6

# Verify naming
figures = [e for e in result.elements if e.element_type == ElementType.FIGURE]
tables = [e for e in result.elements if e.element_type == ElementType.TABLE]
equations = [e for e in result.elements if e.element_type == ElementType.EQUATION]

assert figures[0].output_filename == "figure_01.pdf"
assert figures[1].output_filename == "figure_02.pdf"
assert tables[0].output_filename == "table_01.pdf"
assert tables[2].output_filename == "table_03.pdf"
assert equations[0].output_filename == "equation_01.pdf"

print("✓ Test 2.1 passed: Multiple types extracted with correct naming")
EOF

# CLI usage
pdf-extractor fixtures/sample_paper_mixed.pdf
```

**Expected Output**:
```
PDF Element Extraction Complete
================================

Document: sample_paper_mixed.pdf (15 pages)
Output Directory: .
Extraction Time: 12.67 seconds

Elements Extracted:
  Figures: 2
    - figure_01.pdf (page 3, confidence: 0.95)
    - figure_02.pdf (page 7, confidence: 0.92)
  Tables: 3
    - table_01.pdf (page 5, confidence: 0.89)
    - table_02.pdf (page 9, confidence: 0.91)
    - table_03.pdf (page 12, confidence: 0.87)
  Equations: 1
    - equation_01.pdf (page 4, confidence: 0.93)

Total Elements: 6

Status: SUCCESS
```

---

### Test Scenario 2.2: Handle overlapping regions

**Given**: A PDF with overlapping element boundaries

**When**: User runs extraction

**Then**: System extracts primary element type without duplication

**Test Commands**:
```bash
# Library usage
python << 'EOF'
from src.lib.extractor import extract_elements

result = extract_elements("fixtures/paper_with_overlaps.pdf")

# Verify no duplicate extractions in overlapping regions
# (Implementation should keep highest-confidence element)
assert len(result.warnings) > 0
assert any("overlap" in w.lower() for w in result.warnings)

print("✓ Test 2.2 passed: Overlaps handled correctly")
EOF
```

**Expected Output**:
```
...
Warnings:
  - Element overlap detected on page 5: kept FIGURE (conf=0.94), discarded TABLE (conf=0.78)
...
```

---

### Test Scenario 2.3: Each output file contains single element

**Given**: A PDF with mixed content

**When**: Extraction completes

**Then**: Each output PDF contains exactly one element

**Test Commands**:
```bash
# Verify each output PDF has single element
for pdf in figure_*.pdf table_*.pdf equation_*.pdf; do
  pages=$(python -c "import fitz; print(fitz.open('$pdf').page_count)")
  if [ "$pages" != "1" ]; then
    echo "✗ ERROR: $pdf has $pages pages (expected 1)"
    exit 1
  fi
done
echo "✓ Test 2.3 passed: All output files are single-page PDFs"
```

---

## User Story 3: Custom Output Configuration (P3)

**Goal**: Configure output location and naming for automated workflows

### Test Scenario 3.1: Custom output directory

**Given**: User specifies output directory "/output/extracted"

**When**: Extraction runs

**Then**: All files created in specified directory

**Test Commands**:
```bash
# Library usage
python << 'EOF'
from src.lib.extractor import extract_elements
from src.lib.models import ExtractionConfig
import os

config = ExtractionConfig(output_directory="/tmp/extracted_test")
result = extract_elements("fixtures/sample_paper_mixed.pdf", config)

assert result.output_directory == "/tmp/extracted_test"
assert os.path.exists("/tmp/extracted_test/figure_01.pdf")

print("✓ Test 3.1 passed: Custom directory used")
EOF

# CLI usage
pdf-extractor --output /tmp/extracted_test fixtures/sample_paper_mixed.pdf
ls /tmp/extracted_test/
```

---

### Test Scenario 3.2: Custom naming pattern

**Given**: User specifies pattern "img_{counter:03d}.pdf"

**When**: Extracting 5 figures

**Then**: Files named img_001.pdf through img_005.pdf

**Test Commands**:
```bash
# Library usage
python << 'EOF'
from src.lib.extractor import extract_elements
from src.lib.models import ExtractionConfig, ElementType

config = ExtractionConfig(
    element_types=[ElementType.FIGURE],
    naming_pattern="img_{counter:03d}.pdf"
)
result = extract_elements("fixtures/paper_5_figures.pdf", config)

assert result.elements[0].output_filename == "img_001.pdf"
assert result.elements[4].output_filename == "img_005.pdf"

print("✓ Test 3.2 passed: Custom naming pattern applied")
EOF

# CLI usage
pdf-extractor \
  --types figure \
  --naming-pattern "img_{counter:03d}.pdf" \
  fixtures/paper_5_figures.pdf
```

---

### Test Scenario 3.3: Boundary padding

**Given**: User specifies 10-pixel padding

**When**: Extracting elements

**Then**: Cropped regions include 10 pixels around boundaries

**Test Commands**:
```bash
# Library usage
python << 'EOF'
from src.lib.extractor import extract_elements
from src.lib.models import ExtractionConfig

config = ExtractionConfig(boundary_padding=10)
result = extract_elements("fixtures/sample_paper_with_figures.pdf", config)

# Verify bounding boxes have padding applied
for element in result.elements:
    assert element.bounding_box.padding == 10

print("✓ Test 3.3 passed: Boundary padding applied")
EOF

# CLI usage
pdf-extractor --padding 10 fixtures/sample_paper_with_figures.pdf
```

---

## JSON Output Format Testing

**Test JSON Output**:
```bash
# CLI with JSON output
pdf-extractor --format json fixtures/sample_paper_mixed.pdf > result.json

# Validate JSON structure
python << 'EOF'
import json

with open("result.json") as f:
    result = json.load(f)

assert "success" in result
assert "extraction_time_seconds" in result
assert "elements" in result
assert "statistics" in result
assert result["statistics"]["figure_count"] >= 0

print("✓ JSON output valid")
EOF

# Use with jq for parsing
cat result.json | jq '.statistics'
cat result.json | jq '.elements[] | select(.element_type == "figure")'
```

---

## Performance Testing

**Test 20-Page Performance Target**:
```bash
# Library timing test
python << 'EOF'
import time
from src.lib.extractor import extract_elements

start = time.time()
result = extract_elements("fixtures/paper_20_pages.pdf")
elapsed = time.time() - start

assert elapsed < 30.0, f"Performance target missed: {elapsed:.2f}s > 30s"
print(f"✓ Performance test passed: {elapsed:.2f}s < 30s target")
EOF
```

---

## Error Handling Testing

**Test Invalid PDF**:
```bash
# Should raise InvalidPDFError
python << 'EOF'
from src.lib.extractor import extract_elements
from src.lib.models import InvalidPDFError

try:
    extract_elements("fixtures/not_a_pdf.txt")
    assert False, "Should have raised InvalidPDFError"
except InvalidPDFError as e:
    assert "Invalid PDF" in str(e)
    print("✓ Invalid PDF error handled correctly")
EOF

# CLI should exit with code 4
pdf-extractor fixtures/not_a_pdf.txt
echo $?  # Should be 4
```

**Test Missing File**:
```bash
# Should raise FileNotFoundError
python << 'EOF'
from src.lib.extractor import extract_elements

try:
    extract_elements("nonexistent.pdf")
    assert False, "Should have raised FileNotFoundError"
except FileNotFoundError:
    print("✓ Missing file error handled correctly")
EOF

# CLI should exit with code 3
pdf-extractor nonexistent.pdf
echo $?  # Should be 3
```

---

## Contract Testing

**Test Library Interface Contract**:
```bash
# Run contract tests
pytest tests/contract/test_extractor_contract.py -v

# Expected output:
# test_extract_elements_basic PASSED
# test_extract_elements_with_config PASSED
# test_extract_elements_invalid_pdf PASSED
# test_output_format_json PASSED
# test_confidence_threshold PASSED
```

**Test CLI Interface Contract**:
```bash
# Run CLI contract tests
pytest tests/contract/test_cli_contract.py -v

# Test help message
pdf-extractor --help | grep "PDF Element Extractor"

# Test version
pdf-extractor --version | grep "v1.0.0"
```

---

## Integration Testing

**Full Workflow Test**:
```bash
pytest tests/integration/test_full_extraction_workflow.py -v
```

**Test CLI → Library Integration**:
```bash
pytest tests/integration/test_cli_library_integration.py -v
```

---

## Acceptance Criteria Checklist

### User Story 1 (P1)
- [x] Extract figures from 3-figure PDF → 3 separate files
- [x] No figures detected → success with empty results
- [x] 10 figures → maintain zero-padding (figure_01 to figure_10)

### User Story 2 (P2)
- [x] Extract mixed types → correct type-specific naming
- [x] Handle overlapping regions → keep highest confidence
- [x] Each output file → single-page PDF

### User Story 3 (P3)
- [x] Custom output directory → files in specified location
- [x] Custom naming pattern → pattern applied correctly
- [x] Boundary padding → padding applied to crops

### Cross-Cutting
- [x] JSON output format → valid, parseable JSON
- [x] Human-readable output → clear, formatted text
- [x] Performance → 20-page PDF in <30 seconds
- [x] Error handling → appropriate exceptions and exit codes

---

## Manual Verification

**Visual Inspection**:
1. Extract figures from a known paper
2. Open each extracted PDF
3. Verify:
   - Element is correctly isolated
   - Boundaries are appropriate (not too tight/loose)
   - Quality is preserved (no degradation)
   - Content is readable

**Example**:
```bash
pdf-extractor --types figure sample_paper.pdf
open figure_01.pdf  # Manual review
```

---

## Debugging Tips

**Enable Verbose Logging**:
```bash
pdf-extractor --verbose paper.pdf 2> debug.log
cat debug.log
```

**Test with Single Page**:
```bash
pdf-extractor --max-pages 1 paper.pdf
```

**Check Confidence Scores**:
```bash
pdf-extractor --format json paper.pdf | jq '.elements[] | .confidence_score'
```

**Lower Confidence Threshold** (find more elements):
```bash
pdf-extractor --confidence 0.3 paper.pdf
```

---

## Summary

This quickstart provides:
- **Test commands** for each user story
- **Expected outputs** for verification
- **Library and CLI examples**
- **Performance and error testing**
- **Contract validation procedures**

All tests are independently runnable and validate the acceptance criteria from the specification.
