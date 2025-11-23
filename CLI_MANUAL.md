# DocScalpel - CLI User Manual

**Version**: 1.0.0
**Date**: 2025-11-20

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Command Reference](#command-reference)
5. [Usage Examples](#usage-examples)
6. [Output Formats](#output-formats)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)
9. [Performance Tips](#performance-tips)

---

## Introduction

DocScalpel is a command-line tool that automatically detects and extracts figures, tables, and equations from academic PDF papers. It uses deep learning (DocLayout-YOLO) to identify elements and saves each as a separate, numbered PDF file.

### What It Does

- 🎨 Extracts **figures** from PDFs
- 📊 Extracts **tables** from PDFs
- 🔢 Extracts **equations** from PDFs
- 📝 Generates sequential numbered output files
- ⚙️ Highly configurable extraction settings
- 📤 Outputs results in JSON or human-readable text

### System Requirements

- **Python**: 3.11 or higher
- **Memory**: 500MB minimum
- **Disk Space**: 100MB + space for output files
- **Operating System**: macOS, Linux, or Windows

---

## Installation

### Method 1: Direct Execution (Recommended for Development)

```bash
# 1. Navigate to the project directory
cd /path/to/docscalpel

# 2. Install dependencies (if not already installed)
pip install -r requirements.txt

# 3. Run directly using Python
python -m src.cli.main paper.pdf
```

### Method 2: Install with pip (Recommended for Production)

```bash
# 1. Navigate to the project directory
cd /path/to/docscalpel

# 2. Install the package
pip install -e .

# 3. Run from anywhere
pdf-extractor paper.pdf
```

### Method 3: Using the Executable Script

```bash
# 1. Navigate to the project directory
cd /path/to/docscalpel

# 2. Make the script executable (Unix/macOS only)
chmod +x pdf-extractor

# 3. Run the script
./pdf-extractor paper.pdf
```

### Verify Installation

```bash
# Check version
python -m src.cli.main --version
# Output: pdf-extractor 1.0.0

# Show help
python -m src.cli.main --help
```

---

## Quick Start

### Basic Extraction

Extract all figures, tables, and equations from a PDF:

```bash
python -m src.cli.main paper.pdf
```

**Output**:
```
✅ Extraction completed successfully

📄 Document:
  File: paper.pdf
  Pages: 10 total, 10 processed
  Size: 2,345,678 bytes

📊 Extraction Statistics:
  Total elements: 8
  Figures: 5
  Tables: 2
  Equations: 1
  Time: 3.45s

📂 Output:
  Directory: .
```

Files created: `figure_01.pdf`, `figure_02.pdf`, ..., `table_01.pdf`, `table_02.pdf`, `equation_01.pdf`

### Extract Only Figures

```bash
python -m src.cli.main paper.pdf --types figure
```

### Extract to Specific Directory

```bash
python -m src.cli.main paper.pdf --output ./extracted_elements
```

### Get JSON Output

```bash
python -m src.cli.main paper.pdf --format json
```

---

## Command Reference

### Syntax

```bash
python -m src.cli.main PDF_FILE [OPTIONS]
```

Or if installed via pip:

```bash
pdf-extractor PDF_FILE [OPTIONS]
```

### Positional Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `PDF_FILE` | Path to the PDF file to process | Yes |

### Optional Arguments

#### Element Selection

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--types TYPES` | Comma-separated element types to extract | `figure,table,equation` | `--types figure,table` |

**Valid types**: `figure`, `table`, `equation`

#### Output Configuration

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--output DIR` | Output directory for extracted elements | `.` (current directory) | `--output ./figures` |
| `--naming-pattern PATTERN` | Naming pattern for output files | `{type}_{counter:02d}.pdf` | `--naming-pattern img_{counter:03d}.pdf` |
| `--overwrite` | Overwrite existing output files | `False` | `--overwrite` |

**Pattern placeholders**:
- `{type}`: Element type (figure, table, equation)
- `{counter}`: Sequential number
- `{counter:02d}`: Zero-padded number (e.g., 01, 02)
- `{counter:03d}`: 3-digit zero-padded number (e.g., 001, 002)

#### Detection Settings

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--confidence THRESHOLD` | Minimum confidence threshold (0.0-1.0) | `0.5` | `--confidence 0.8` |
| `--padding PIXELS` | Boundary padding in pixels | `0` | `--padding 10` |
| `--max-pages N` | Maximum number of pages to process | `None` (all pages) | `--max-pages 50` |

#### Output Format

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--format FORMAT` | Output format: `json` or `text` | `text` | `--format json` |
| `--verbose`, `-v` | Enable verbose logging | `False` | `--verbose` |

#### Information Commands

| Option | Description |
|--------|-------------|
| `--help`, `-h` | Show help message and exit |
| `--version` | Show version number and exit |

---

## Usage Examples

### Example 1: Extract Only Figures

Extract all figures from a research paper:

```bash
python -m src.cli.main research_paper.pdf --types figure --output ./figures
```

**Result**: Creates `figures/figure_01.pdf`, `figures/figure_02.pdf`, etc.

### Example 2: Extract Tables with Custom Naming

Extract tables with custom filename pattern:

```bash
python -m src.cli.main paper.pdf \
  --types table \
  --output ./tables \
  --naming-pattern "table_{counter:03d}.pdf"
```

**Result**: Creates `tables/table_001.pdf`, `tables/table_002.pdf`, etc.

### Example 3: High-Confidence Figures Only

Extract only high-confidence figures (≥80%):

```bash
python -m src.cli.main paper.pdf \
  --types figure \
  --confidence 0.8 \
  --output ./high_conf_figures
```

### Example 4: Extract with Boundary Padding

Add 10-pixel padding around detected elements:

```bash
python -m src.cli.main paper.pdf \
  --padding 10 \
  --output ./padded_elements
```

**Use case**: Ensures no content is cut off at element boundaries

### Example 5: Process First 20 Pages Only

For quick testing or large PDFs:

```bash
python -m src.cli.main large_paper.pdf \
  --max-pages 20 \
  --output ./test_extraction
```

### Example 6: JSON Output for Scripting

Get machine-readable JSON output:

```bash
python -m src.cli.main paper.pdf --format json > results.json
```

**Result**: Creates `results.json` with complete extraction metadata

### Example 7: Extract Multiple Types with Custom Settings

Complete extraction with all custom settings:

```bash
python -m src.cli.main paper.pdf \
  --types figure,table,equation \
  --output ./extracted \
  --naming-pattern "{type}_{counter:02d}.pdf" \
  --padding 5 \
  --confidence 0.6 \
  --overwrite \
  --verbose
```

### Example 8: Batch Processing Multiple PDFs

Process all PDFs in a directory:

```bash
# Bash script
for pdf in papers/*.pdf; do
  echo "Processing: $pdf"
  python -m src.cli.main "$pdf" \
    --output "extracted/$(basename "$pdf" .pdf)" \
    --types figure,table
done
```

### Example 9: Using JSON Output with jq

Extract specific statistics:

```bash
# Get element counts
python -m src.cli.main paper.pdf --format json | \
  jq '.statistics'

# Get only figure count
python -m src.cli.main paper.pdf --format json | \
  jq '.statistics.figure_count'

# Get list of extracted files
python -m src.cli.main paper.pdf --format json | \
  jq '.elements[].output_filename'
```

### Example 10: Verbose Logging for Debugging

Enable detailed logging to stderr:

```bash
python -m src.cli.main paper.pdf --verbose 2> extraction.log
```

**Result**:
- Standard output: Results
- `extraction.log`: Detailed debug information

---

## Output Formats

### Text Format (Default)

Human-readable format with emojis and clear structure.

**Example**:
```
✅ Extraction completed successfully

📄 Document:
  File: paper.pdf
  Pages: 10 total, 10 processed
  Size: 1,234,567 bytes

📊 Extraction Statistics:
  Total elements: 5
  Figures: 3
  Tables: 2
  Equations: 0
  Time: 2.45s

📂 Output:
  Directory: ./extracted

📋 Extracted Elements:
  Figures (3):
    - figure_01.pdf (page 2, confidence: 0.95)
    - figure_02.pdf (page 5, confidence: 0.89)
    - figure_03.pdf (page 8, confidence: 0.92)
  Tables (2):
    - table_01.pdf (page 3, confidence: 0.87)
    - table_02.pdf (page 7, confidence: 0.91)
```

**When to use**:
- ✅ Interactive terminal use
- ✅ Quick visual inspection
- ✅ Progress monitoring

### JSON Format

Machine-readable structured data.

**Example**:
```json
{
  "success": true,
  "statistics": {
    "total_elements": 5,
    "figure_count": 3,
    "table_count": 2,
    "equation_count": 0,
    "extraction_time_seconds": 2.45
  },
  "document": {
    "file_path": "paper.pdf",
    "page_count": 10,
    "pages_processed": 10,
    "file_size_bytes": 1234567,
    "is_encrypted": false
  },
  "extraction": {
    "output_directory": "./extracted"
  },
  "elements": [
    {
      "element_id": "abc-123-def-456",
      "element_type": "figure",
      "output_filename": "figure_01.pdf",
      "page_number": 2,
      "sequence_number": 1,
      "confidence_score": 0.95,
      "bounding_box": {
        "x": 72.0,
        "y": 150.5,
        "width": 468.0,
        "height": 280.3,
        "page_number": 2,
        "padding": 0
      }
    }
  ],
  "errors": [],
  "warnings": []
}
```

**When to use**:
- ✅ Automated pipelines
- ✅ Data analysis
- ✅ Integration with other tools
- ✅ Logging and monitoring

**JSON Schema**:

```javascript
{
  "success": boolean,              // Overall success status
  "statistics": {
    "total_elements": number,      // Total elements extracted
    "figure_count": number,        // Number of figures
    "table_count": number,         // Number of tables
    "equation_count": number,      // Number of equations
    "extraction_time_seconds": number  // Processing time
  },
  "document": {
    "file_path": string,           // Input PDF path
    "page_count": number,          // Total pages in PDF
    "pages_processed": number,     // Pages actually processed
    "file_size_bytes": number,     // File size
    "is_encrypted": boolean        // Encryption status
  },
  "extraction": {
    "output_directory": string     // Output directory path
  },
  "elements": [                    // Array of extracted elements
    {
      "element_id": string,        // Unique identifier
      "element_type": string,      // "figure", "table", or "equation"
      "output_filename": string,   // Generated filename
      "page_number": number,       // Source page (1-indexed)
      "sequence_number": number,   // Type-specific sequence number
      "confidence_score": number,  // Detection confidence (0.0-1.0)
      "bounding_box": {
        "x": number,               // Left coordinate
        "y": number,               // Top coordinate
        "width": number,           // Box width
        "height": number,          // Box height
        "page_number": number,     // Page number
        "padding": number          // Applied padding
      }
    }
  ],
  "errors": [string],              // Array of error messages
  "warnings": [string]             // Array of warning messages
}
```

---

## Advanced Features

### Custom Naming Patterns

Control output filename format with pattern strings.

**Syntax**: `--naming-pattern "PATTERN"`

**Available placeholders**:
- `{type}`: Element type (figure, table, equation)
- `{counter:Nd}`: Zero-padded number with N digits

**Examples**:

```bash
# Default: figure_01.pdf, figure_02.pdf
--naming-pattern "{type}_{counter:02d}.pdf"

# Three-digit padding: figure_001.pdf
--naming-pattern "{type}_{counter:03d}.pdf"

# Custom prefix: extracted_figure_01.pdf
--naming-pattern "extracted_{type}_{counter:02d}.pdf"

# Type-independent numbering: img_001.pdf, img_002.pdf
--naming-pattern "img_{counter:03d}.pdf"

# Date-stamped: figure_20250120_01.pdf
--naming-pattern "{type}_20250120_{counter:02d}.pdf"
```

### Confidence Thresholding

Control detection sensitivity with confidence threshold.

**Higher threshold (0.8-1.0)**:
- ✅ Fewer false positives
- ✅ Higher precision
- ❌ May miss some elements

```bash
python -m src.cli.main paper.pdf --confidence 0.9
```

**Lower threshold (0.3-0.5)**:
- ✅ Catches more elements
- ✅ Higher recall
- ❌ May include false detections

```bash
python -m src.cli.main paper.pdf --confidence 0.3
```

**Recommended values**:
- **Figures**: 0.5-0.7
- **Tables**: 0.6-0.8 (tables are more structured)
- **Equations**: 0.5-0.7

### Boundary Padding

Add extra space around detected elements to avoid cropping.

**Use cases**:
- Element borders might be tight
- Caption text near element boundaries
- Ensuring complete visual context

**Example**:

```bash
# Add 10 pixels on all sides
python -m src.cli.main paper.pdf --padding 10
```

**Effect**:
- Original bounding box: 100x100 pixels
- With padding=10: 120x120 pixels (10px added to each side)

### Page Limiting

Process only first N pages for testing or large documents.

**Example**:

```bash
# Test on first 10 pages
python -m src.cli.main huge_paper.pdf --max-pages 10
```

**Use cases**:
- Quick validation before full extraction
- Large PDF files (100+ pages)
- Sampling from long documents

---

## Troubleshooting

### Common Issues

#### 1. "PDF file not found"

**Problem**: File path is incorrect or file doesn't exist.

**Solution**:
```bash
# Check file exists
ls paper.pdf

# Use absolute path
python -m src.cli.main /full/path/to/paper.pdf

# Or relative path from current directory
python -m src.cli.main ./papers/paper.pdf
```

#### 2. "Invalid element type"

**Problem**: Typo in `--types` argument.

**Solution**:
```bash
# ❌ Wrong
python -m src.cli.main paper.pdf --types figures

# ✅ Correct
python -m src.cli.main paper.pdf --types figure

# Valid types: figure, table, equation (singular)
```

#### 3. "Confidence threshold must be between 0.0 and 1.0"

**Problem**: Invalid confidence value.

**Solution**:
```bash
# ❌ Wrong
python -m src.cli.main paper.pdf --confidence 1.5

# ✅ Correct
python -m src.cli.main paper.pdf --confidence 0.8
```

#### 4. "Output directory is not writable"

**Problem**: No write permissions for output directory.

**Solution**:
```bash
# Check permissions
ls -ld ./output

# Create directory with proper permissions
mkdir -p ./output
chmod 755 ./output

# Or use a different directory
python -m src.cli.main paper.pdf --output ~/Documents/extracted
```

#### 5. "No elements detected"

**Problem**: PDF has no extractable elements or confidence threshold is too high.

**Solutions**:
```bash
# Try lower confidence threshold
python -m src.cli.main paper.pdf --confidence 0.3

# Enable verbose logging to see what's happening
python -m src.cli.main paper.pdf --verbose

# Check if PDF contains actual figures/tables
# (Some PDFs may have text-only content)
```

#### 6. Module import errors

**Problem**: Dependencies not installed or incorrect Python path.

**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "PyMuPDF|doclayout"

# Run from project root directory
cd /path/to/docscalpel
python -m src.cli.main paper.pdf
```

### Debug Mode

Enable verbose logging for detailed troubleshooting:

```bash
python -m src.cli.main paper.pdf --verbose 2> debug.log
```

**Output**: `debug.log` contains detailed execution trace:
```
2025-11-20 10:30:15 - __main__ - INFO - DocScalpel v1.0.0
2025-11-20 10:30:15 - __main__ - INFO - Processing: paper.pdf
2025-11-20 10:30:15 - src.lib.extractor - DEBUG - Configuration: ExtractionConfig(...)
2025-11-20 10:30:15 - src.lib.extractor - INFO - Validating PDF: paper.pdf
2025-11-20 10:30:16 - src.lib.extractor - INFO - Loading PDF document
...
```

### Getting Help

If you encounter issues:

1. **Check the help**: `python -m src.cli.main --help`
2. **Enable verbose mode**: `--verbose`
3. **Verify input PDF**: Use a different PDF to isolate the issue
4. **Check dependencies**: Ensure all packages are installed
5. **Review logs**: Look for ERROR or WARNING messages

---

## Performance Tips

### Optimize Extraction Speed

1. **Process fewer pages**:
   ```bash
   python -m src.cli.main paper.pdf --max-pages 20
   ```

2. **Extract single element type**:
   ```bash
   # Faster
   python -m src.cli.main paper.pdf --types figure

   # Slower (processes all types)
   python -m src.cli.main paper.pdf
   ```

3. **Use appropriate confidence threshold**:
   ```bash
   # Higher threshold = faster (fewer elements to process)
   python -m src.cli.main paper.pdf --confidence 0.8
   ```

### Optimize for Accuracy

1. **Lower confidence threshold**:
   ```bash
   python -m src.cli.main paper.pdf --confidence 0.4
   ```

2. **Add boundary padding** to avoid cutting off elements:
   ```bash
   python -m src.cli.main paper.pdf --padding 10
   ```

3. **Process all pages**:
   ```bash
   python -m src.cli.main paper.pdf  # No --max-pages limit
   ```

### Batch Processing Tips

Process multiple PDFs efficiently:

```bash
#!/bin/bash
# batch_extract.sh

INPUT_DIR="papers"
OUTPUT_BASE="extracted"

for pdf in "$INPUT_DIR"/*.pdf; do
    filename=$(basename "$pdf" .pdf)
    output_dir="$OUTPUT_BASE/$filename"

    echo "Processing: $filename"
    python -m src.cli.main "$pdf" \
        --output "$output_dir" \
        --types figure,table \
        --confidence 0.7 \
        --format json > "$output_dir/results.json"

    echo "Completed: $filename"
    echo "---"
done

echo "All PDFs processed!"
```

### Memory Management

For very large PDFs:

1. **Use page limiting**:
   ```bash
   # Process in batches of 50 pages
   python -m src.cli.main large.pdf --max-pages 50
   ```

2. **Process one type at a time**:
   ```bash
   # First figures
   python -m src.cli.main large.pdf --types figure

   # Then tables
   python -m src.cli.main large.pdf --types table
   ```

---

## Exit Codes

The CLI returns different exit codes for automation:

| Exit Code | Meaning | Description |
|-----------|---------|-------------|
| `0` | Success | Extraction completed successfully |
| `1` | Error | General error (invalid PDF, extraction failed, etc.) |
| `130` | Cancelled | User interrupted with Ctrl+C |

**Usage in scripts**:

```bash
python -m src.cli.main paper.pdf
if [ $? -eq 0 ]; then
    echo "Success!"
else
    echo "Failed!"
    exit 1
fi
```

---

## Quick Reference Card

```bash
# BASIC USAGE
python -m src.cli.main paper.pdf

# COMMON OPTIONS
python -m src.cli.main paper.pdf --types figure,table
python -m src.cli.main paper.pdf --output ./extracted
python -m src.cli.main paper.pdf --confidence 0.8
python -m src.cli.main paper.pdf --format json
python -m src.cli.main paper.pdf --verbose

# ADVANCED
python -m src.cli.main paper.pdf \
  --types figure,table,equation \
  --output ./extracted \
  --naming-pattern "{type}_{counter:03d}.pdf" \
  --padding 10 \
  --confidence 0.7 \
  --overwrite \
  --max-pages 50 \
  --format json \
  --verbose

# INFORMATION
python -m src.cli.main --help
python -m src.cli.main --version
```

---

## Appendix: Complete Option List

```
positional arguments:
  pdf_file              Path to the PDF file to process

optional arguments:
  -h, --help            show this help message and exit
  --types TYPES         Comma-separated element types to extract
                        (default: figure,table,equation)
  --output OUTPUT       Output directory for extracted elements
                        (default: current directory)
  --naming-pattern NAMING_PATTERN
                        Naming pattern for output files
                        (default: {type}_{counter:02d}.pdf)
  --padding PADDING     Boundary padding in pixels
                        (default: 0)
  --confidence CONFIDENCE
                        Minimum confidence threshold 0.0-1.0
                        (default: 0.5)
  --format {json,text}  Output format
                        (default: text)
  --overwrite           Overwrite existing output files
  --max-pages MAX_PAGES
                        Maximum number of pages to process
                        (default: all)
  --verbose, -v         Enable verbose logging
  --version             show program's version number and exit
```

---

**DocScalpel v1.0.0**
Copyright © 2025 | For support and updates, visit the project repository
