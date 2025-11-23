# DocScalpel

```
   ╱╲
  ╱  ╲     DocScalpel
 ╱____╲    Precision PDF Element Extraction
```

**Surgical precision for document element extraction**

A Python library and CLI application for detecting and extracting figures, tables, and equations from academic PDFs using deep learning.

[![Tests](https://img.shields.io/badge/tests-134%20passing-success)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-76%25-yellow)](tests/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Status

✅ **Library API**: Complete and tested
✅ **CLI Application**: Fully functional
✅ **Documentation**: Comprehensive manuals
✅ **Test Coverage**: 76% (134 passing tests)
✅ **ML Detection**: DocLayout-YOLO integration complete

## Features

- **Extract figures, tables, and equations** from academic PDFs with surgical precision
- **Deep learning powered** using state-of-the-art DocLayout-YOLO model
- **High accuracy** detection with configurable confidence thresholds
- **Sequential numbering** with zero-padding (figure_01.pdf, table_01.pdf, etc.)
- **Multiple element types** in single pass with overlap resolution
- **Custom output** configuration (directory, naming patterns, boundary padding)
- **Library-first architecture** - use as Python library or CLI tool
- **Production-ready** with comprehensive error handling and logging

## Installation

```bash
# Clone the repository
git clone https://github.com/zebehn/docscalpel.git
cd docscalpel

# Install dependencies
pip install -r requirements.txt

# Model will be automatically downloaded from Hugging Face on first run
```

## Quick Start

### As a Library

```python
from docscalpel import extract_elements, ExtractionConfig, ElementType

# Extract all figures
config = ExtractionConfig(element_types=[ElementType.FIGURE])
result = extract_elements("paper.pdf", config)

print(f"Extracted {result.figure_count} figures in {result.extraction_time_seconds:.2f}s")
for element in result.elements:
    print(f"  - {element.output_filename}")
```

### As a CLI

```bash
# Extract all element types (figures, tables, equations)
python -m docscalpel paper.pdf

# Extract only figures
python -m docscalpel paper.pdf --types figure

# Custom output directory
python -m docscalpel paper.pdf --output ./extracted

# JSON output for scripting
python -m docscalpel paper.pdf --format json | jq '.statistics'

# High confidence threshold with padding
python -m docscalpel paper.pdf --confidence 0.8 --padding 10

# Get help
python -m docscalpel --help
```

**📖 CLI Documentation:**
- **[5-Minute Quick Start](QUICKSTART_CLI.md)** - Get started immediately
- **[Complete CLI Manual](CLI_MANUAL.md)** - Full reference with examples
- **[Technical Deep Dive](docs/technical-blog-post.md)** - Architecture and implementation details

## How It Works

DocScalpel combines state-of-the-art deep learning with robust PDF processing:

1. **PDF Rendering**: Pages rendered at 2x resolution for optimal detection
2. **DocLayout-YOLO Detection**: Specialized YOLO model trained on 300K+ documents
3. **Coordinate Transformation**: Precise scaling from image to PDF coordinates
4. **Overlap Resolution**: NMS algorithm keeps highest-confidence elements
5. **Precise Extraction**: Vector-preserving PDF cropping

## Architecture

The system follows a **Library-First Architecture**:

- **Core Library** (`src/lib/`): Standalone extraction engine
- **CLI Application** (`src/cli/`): Thin wrapper for command-line use
- **Independent Testing**: Library testable without CLI dependencies

### Project Structure

```
src/
├── lib/                 # Core extraction library
│   ├── extractor.py    # Main extraction orchestrator
│   ├── detectors/      # Element detection (figure, table, equation)
│   ├── pdf_processor.py # PDF parsing
│   ├── cropper.py      # PDF cropping
│   └── models.py       # Data models
└── cli/                # CLI application
    ├── main.py         # Entry point
    ├── formatter.py    # Output formatting
    └── logger.py       # Logging

tests/
├── contract/           # Library interface tests
├── integration/        # Component integration tests
└── unit/               # Unit tests
```

## Technology Stack

- **Python 3.11+**
- **PyMuPDF (fitz)**: High-performance PDF processing and cropping
- **DocLayout-YOLO**: Deep learning-based document layout analysis
- **Hugging Face Hub**: Model distribution and caching
- **Pillow**: Image processing
- **pytest**: Testing framework with 134 passing tests

## Requirements

- Python 3.11 or higher
- 500MB free memory (2GB recommended for large PDFs)
- 250MB disk space for model cache
- Write access to output directories

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test category
pytest tests/contract/
pytest tests/integration/
pytest tests/unit/
```

### Test-Driven Development

This project follows strict TDD principles:
1. Write tests first
2. Verify tests fail (RED state)
3. Implement feature
4. Verify tests pass (GREEN state)
5. Refactor while keeping tests green

## Performance

**Benchmark Results** (25-page academic paper, CPU inference):

- **Total extraction time**: 67.73 seconds
- **Detected elements**: 39 total (20 figures, 6 tables)
- **Successfully extracted**: 23 elements
- **Per-page average**: 2.71 seconds
- **Inference breakdown**: 77% YOLO, 12.5% rendering, 7.4% cropping

**Optimization Potential**:
- GPU acceleration: 5-10x speedup expected
- Batch processing: 20-30% improvement
- Optimized resolution: 1.5-2x speedup with minimal accuracy loss

## User Stories

### ✅ Priority 1 (MVP): Extract Single Element Type
Extract all figures from a PDF and save as separate numbered files.

### ✅ Priority 2: Extract Multiple Element Types
Extract figures, tables, and equations in a single pass with type-specific naming.

### ✅ Priority 3: Custom Output Configuration
Support custom output directories, naming patterns, and boundary padding.

## Real-World Example

```bash
$ python -m docscalpel research_paper.pdf

✅ Extraction completed successfully

📄 Document:
  File: research_paper.pdf
  Pages: 25 total, 25 processed

📊 Extraction Statistics:
  Total elements: 23
  Figures: 20
  Tables: 3
  Equations: 0
  Time: 67.73s

📂 Output: ./extracted_elements/
```

## Documentation

For detailed documentation, see:
- **[Technical Blog Post](docs/technical-blog-post.md)** - Complete technical deep dive with architecture and implementation details

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors & Contact

**Main Developer**: Minsu Jang
**Email**: minsu@etri.re.kr
**Organization**: Electronics and Telecommunications Research Institute (ETRI)

For questions, bug reports, or collaboration inquiries, please contact the main developer or open an issue on GitHub.

## Contributing

Contributions welcome! Please ensure all tests pass and follow the TDD workflow.

## Citation

If you use DocScalpel in your research, please cite:

```bibtex
@software{docscalpel_2025,
  author = {Jang, Minsu},
  title = {DocScalpel: Precision PDF Element Extraction},
  year = {2025},
  url = {https://github.com/zebehn/docscalpel}
}
```

## Acknowledgments

- **DocLayout-YOLO Team** (OpenDataLab) - Pre-trained model
- **PyMuPDF Contributors** - High-performance PDF library
- **Hugging Face** - Model hosting infrastructure

---

**DocScalpel** - Extracting knowledge with surgical precision.
