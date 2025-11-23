# CLI Interface Contract: PDF Element Extractor

**Version**: 1.0.0
**Date**: 2025-11-19
**Stability**: Draft

---

## Overview

This document defines the command-line interface contract for the PDF Element Extractor application. The CLI is a thin wrapper around the core library, providing text-based I/O following Unix conventions.

---

## Command Syntax

```bash
pdf-extractor [OPTIONS] INPUT_PDF
```

**Positional Arguments**:
- `INPUT_PDF`: Path to the PDF file to process (required)

**Options**:
- `-t`, `--types`: Element types to extract (figure, table, equation)
- `-o`, `--output`: Output directory for extracted files
- `-n`, `--naming-pattern`: Custom naming pattern for output files
- `-p`, `--padding`: Boundary padding in pixels
- `-c`, `--confidence`: Minimum confidence threshold (0.0-1.0)
- `-f`, `--format`: Output format (json or text)
- `--overwrite`: Overwrite existing output files
- `--max-pages`: Maximum number of pages to process
- `-h`, `--help`: Show help message
- `-v`, `--version`: Show version information
- `--verbose`: Enable verbose logging

---

## Detailed Option Specifications

### `-t`, `--types`

**Purpose**: Specify which element types to extract

**Values**:
- `figure`, `table`, `equation` (case-insensitive)
- Can specify multiple types: `--types figure table`
- Default: All types (`figure table equation`)

**Examples**:
```bash
# Extract only figures
pdf-extractor --types figure paper.pdf

# Extract figures and tables
pdf-extractor --types figure table paper.pdf
```

---

### `-o`, `--output`

**Purpose**: Specify output directory for extracted files

**Values**:
- Valid directory path (absolute or relative)
- Directory will be created if it doesn't exist
- Default: Current working directory (`.`)

**Examples**:
```bash
# Output to specific directory
pdf-extractor --output ./extracted paper.pdf

# Output to absolute path
pdf-extractor --output /tmp/figures paper.pdf
```

---

### `-n`, `--naming-pattern`

**Purpose**: Custom template for output filenames

**Values**:
- String template with placeholders: `{type}` and `{counter}`
- Must include both placeholders
- `{counter:02d}` for zero-padded numbers
- Default: `{type}_{counter:02d}.pdf`

**Examples**:
```bash
# Custom pattern with 3-digit padding
pdf-extractor --naming-pattern "img_{counter:03d}.pdf" paper.pdf

# Pattern with prefix
pdf-extractor --naming-pattern "paper_{type}_{counter:02d}.pdf" paper.pdf
```

---

### `-p`, `--padding`

**Purpose**: Add padding around detected element boundaries

**Values**:
- Integer >= 0 (pixels)
- Default: 0

**Examples**:
```bash
# Add 10 pixels of padding
pdf-extractor --padding 10 paper.pdf
```

---

### `-c`, `--confidence`

**Purpose**: Set minimum confidence threshold for accepting detections

**Values**:
- Float in range [0.0, 1.0]
- Higher value = stricter filtering (fewer elements, higher precision)
- Lower value = more permissive (more elements, lower precision)
- Default: 0.5

**Examples**:
```bash
# Only extract high-confidence elements
pdf-extractor --confidence 0.8 paper.pdf

# More permissive extraction
pdf-extractor --confidence 0.3 paper.pdf
```

---

### `-f`, `--format`

**Purpose**: Set CLI output format

**Values**:
- `json`: Machine-readable JSON output
- `text`: Human-readable text output (default)

**Examples**:
```bash
# JSON output for scripting
pdf-extractor --format json paper.pdf | jq '.statistics'

# Human-readable output (default)
pdf-extractor --format text paper.pdf
```

---

### `--overwrite`

**Purpose**: Allow overwriting existing output files

**Values**:
- Flag (no value required)
- Default: False (do not overwrite)

**Behavior**:
- Without flag: If output file exists, add error and skip
- With flag: Overwrite existing files without warning

**Examples**:
```bash
# Overwrite existing files
pdf-extractor --overwrite paper.pdf
```

---

### `--max-pages`

**Purpose**: Limit processing to first N pages (for testing or large documents)

**Values**:
- Integer > 0
- Default: None (process all pages)

**Examples**:
```bash
# Process only first 10 pages
pdf-extractor --max-pages 10 paper.pdf
```

---

### `--verbose`

**Purpose**: Enable detailed logging output

**Values**:
- Flag (no value required)
- Default: False

**Behavior**:
- Logs detection progress, timing, and internal operations to stderr
- Useful for debugging and monitoring

**Examples**:
```bash
# Verbose output
pdf-extractor --verbose paper.pdf 2> extraction.log
```

---

## Input/Output Behavior

### Standard Input/Output Streams

**stdin**: Not used (file path required as argument)

**stdout**:
- Primary output channel for extraction results
- Format determined by `--format` option (JSON or text)
- Can be piped to other commands

**stderr**:
- Error messages
- Warnings
- Logging output (when `--verbose` enabled)

---

### Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Extraction completed successfully |
| 1 | General error | Unexpected error occurred |
| 2 | Invalid arguments | Invalid command-line arguments |
| 3 | File not found | Input PDF file does not exist |
| 4 | Invalid PDF | File is not a valid PDF or is corrupted |
| 5 | Permission error | Cannot read input or write to output |
| 6 | Configuration error | Invalid configuration values |
| 7 | Extraction failed | Extraction process failed |

---

## Output Formats

### Text Format (Default)

```
PDF Element Extraction Complete
================================

Document: paper.pdf (20 pages)
Output Directory: ./extracted
Extraction Time: 23.45 seconds

Elements Extracted:
  Figures: 8
    - figure_01.pdf (page 2, confidence: 0.96)
    - figure_02.pdf (page 5, confidence: 0.94)
    - figure_03.pdf (page 8, confidence: 0.91)
    ...
  Tables: 3
    - table_01.pdf (page 7, confidence: 0.89)
    - table_02.pdf (page 12, confidence: 0.87)
    - table_03.pdf (page 15, confidence: 0.93)
  Equations: 12
    - equation_01.pdf (page 3, confidence: 0.92)
    ...

Total Elements: 23

Warnings:
  - Element overlap detected on page 5

Status: SUCCESS
```

### JSON Format

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

## Error Messages

### Format

All error messages follow this structure:
```
Error: {error_type}: {description}
```

### Examples

**File Not Found**:
```
Error: File not found: paper.pdf
```

**Invalid PDF**:
```
Error: Invalid PDF file: paper.pdf. File appears to be corrupted.
```

**Permission Denied**:
```
Error: Permission denied: Cannot read paper.pdf
```

**Invalid Argument**:
```
Error: Invalid confidence threshold: 1.5. Must be between 0.0 and 1.0.
```

**Extraction Failed**:
```
Error: Extraction failed: Model loading failed. Check dependencies.
```

---

## Usage Examples

### Basic Usage

```bash
# Extract all element types to current directory
pdf-extractor paper.pdf
```

### Extract Specific Types

```bash
# Extract only figures
pdf-extractor --types figure paper.pdf

# Extract figures and tables
pdf-extractor --types figure table paper.pdf
```

### Custom Output Location

```bash
# Output to specific directory
pdf-extractor --output ./figures paper.pdf
```

### Configuration Options

```bash
# Full configuration
pdf-extractor \
  --types figure \
  --output ./extracted \
  --naming-pattern "fig_{counter:03d}.pdf" \
  --padding 15 \
  --confidence 0.8 \
  --format json \
  --overwrite \
  paper.pdf
```

### Piping and Scripting

```bash
# JSON output piped to jq
pdf-extractor --format json paper.pdf | jq '.statistics.figure_count'

# Process multiple PDFs
for pdf in *.pdf; do
  pdf-extractor --output "./extracted_$(basename $pdf .pdf)" "$pdf"
done

# Extract only first page (testing)
pdf-extractor --max-pages 1 --verbose paper.pdf
```

### Error Handling in Scripts

```bash
#!/bin/bash

if pdf-extractor --types figure paper.pdf; then
  echo "Extraction successful"
else
  exit_code=$?
  echo "Extraction failed with code $exit_code"
  exit $exit_code
fi
```

---

## Help Message

```bash
pdf-extractor --help
```

**Output**:
```
PDF Element Extractor v1.0.0

Extract figures, tables, and equations from PDF documents.

Usage:
  pdf-extractor [OPTIONS] INPUT_PDF

Positional Arguments:
  INPUT_PDF           Path to the PDF file to process

Options:
  -t, --types TYPE [TYPE ...]
                      Element types to extract: figure, table, equation
                      (default: all types)

  -o, --output DIR    Output directory for extracted files
                      (default: current directory)

  -n, --naming-pattern PATTERN
                      Custom naming pattern for output files
                      Use {type} and {counter} placeholders
                      (default: "{type}_{counter:02d}.pdf")

  -p, --padding PIXELS
                      Boundary padding in pixels (default: 0)

  -c, --confidence THRESHOLD
                      Minimum confidence threshold (0.0-1.0)
                      (default: 0.5)

  -f, --format FORMAT
                      Output format: json or text (default: text)

  --overwrite         Overwrite existing output files

  --max-pages N       Process only first N pages

  --verbose           Enable verbose logging output

  -h, --help          Show this help message and exit

  -v, --version       Show version information and exit

Examples:
  # Extract all elements
  pdf-extractor paper.pdf

  # Extract only figures with custom output
  pdf-extractor --types figure --output ./figures paper.pdf

  # JSON output for scripting
  pdf-extractor --format json paper.pdf | jq '.statistics'

For more information, visit: https://github.com/username/figure-extractor
```

---

## Version Information

```bash
pdf-extractor --version
```

**Output**:
```
PDF Element Extractor v1.0.0
Python 3.11
PyMuPDF 1.x.x
doclayout-yolo 1.x.x
```

---

## Logging Output

When `--verbose` is enabled, detailed logs are written to stderr:

```
[2025-11-19 10:23:15] INFO: Loading PDF: paper.pdf
[2025-11-19 10:23:15] INFO: Document loaded: 20 pages
[2025-11-19 10:23:16] INFO: Initializing detection model...
[2025-11-19 10:23:18] INFO: Model loaded successfully
[2025-11-19 10:23:18] INFO: Processing page 1/20...
[2025-11-19 10:23:18] DEBUG: Detected 2 elements on page 1
[2025-11-19 10:23:19] INFO: Processing page 2/20...
[2025-11-19 10:23:19] DEBUG: Detected 3 elements on page 2
...
[2025-11-19 10:23:35] INFO: Extraction complete: 23 elements in 17.34s
[2025-11-19 10:23:35] INFO: Saved figure_01.pdf
[2025-11-19 10:23:35] INFO: Saved figure_02.pdf
...
```

---

## Environment Variables

### `PDF_EXTRACTOR_OUTPUT_DIR`

**Purpose**: Default output directory (overridden by `--output` flag)

**Example**:
```bash
export PDF_EXTRACTOR_OUTPUT_DIR=./extracted
pdf-extractor paper.pdf  # Uses ./extracted as default
```

### `PDF_EXTRACTOR_CONFIG`

**Purpose**: Path to JSON configuration file with default settings

**Example**:
```bash
export PDF_EXTRACTOR_CONFIG=~/.pdf-extractor-config.json
pdf-extractor paper.pdf
```

---

## Configuration File

Optional JSON configuration file for default settings:

**Location**: `~/.pdf-extractor-config.json` or via `PDF_EXTRACTOR_CONFIG`

**Format**:
```json
{
  "element_types": ["figure", "table"],
  "output_directory": "./extracted",
  "naming_pattern": "{type}_{counter:02d}.pdf",
  "boundary_padding": 10,
  "confidence_threshold": 0.6,
  "output_format": "text",
  "overwrite_existing": false
}
```

**Precedence**: CLI arguments > config file > built-in defaults

---

## Integration with Core Library

The CLI is a thin wrapper that:
1. Parses command-line arguments
2. Constructs `ExtractionConfig` object
3. Calls `extract_elements(pdf_path, config)`
4. Formats and prints `ExtractionResult`
5. Returns appropriate exit code

**Implementation Contract**:
- CLI must not contain extraction logic
- CLI must not directly interact with PDF processing libraries
- CLI must only format library outputs
- All business logic resides in core library

---

## Testing Contract

### Required CLI Tests

1. **test_cli_basic_usage**: Run with minimal arguments
2. **test_cli_all_options**: Run with all options specified
3. **test_cli_json_output**: Verify JSON format
4. **test_cli_text_output**: Verify text format
5. **test_cli_exit_codes**: Verify correct exit codes for each error type
6. **test_cli_help**: Verify help message
7. **test_cli_version**: Verify version output
8. **test_cli_invalid_args**: Test error handling for invalid arguments
9. **test_cli_piping**: Test stdout can be piped to other commands
10. **test_cli_verbose_logging**: Verify logging output to stderr

---

## Backward Compatibility

**v1.x.x Guarantees**:
- Command syntax will not change
- Options will not be removed or renamed
- Output formats (JSON, text) will remain compatible
- Exit codes will remain consistent

**Deprecation Policy**:
- Deprecated options will show warning for at least one MINOR version
- Removed in next MAJOR version with migration guide

---

## Summary

This CLI contract defines a Unix-friendly interface that:
- Follows standard CLI conventions (stdin/stdout/stderr, exit codes)
- Provides both human-readable and machine-readable output
- Offers comprehensive configuration options
- Maintains clear separation from core library logic
- Supports scripting and automation workflows
