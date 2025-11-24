# Installation Guide

## For Users

### From Source (Editable Install)

```bash
# Clone the repository
git clone https://github.com/zebehn/docscalpel.git
cd docscalpel

# Install in editable mode
pip install -e .

# Verify installation
docscalpel --version
```

### From PyPI (Coming Soon)

```bash
pip install docscalpel
```

## For Developers

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/zebehn/docscalpel.git
cd docscalpel

# Install with development dependencies
pip install -e .
pip install -r requirements-dev.txt

# Or use the dev extras
pip install -e ".[dev]"

# Verify installation
python -m pytest tests/
```

## Requirements

- **Python**: 3.11 or higher
- **OS**: Linux, macOS, Windows
- **Memory**: 500MB minimum, 2GB recommended for large PDFs
- **Disk**: 250MB for model cache

## Dependencies

### Runtime Dependencies (automatically installed)
- PyMuPDF >= 1.23.0
- pdfplumber >= 0.10.0
- doclayout-yolo >= 0.0.1
- Pillow >= 10.0.0

### Development Dependencies (optional)
- pytest >= 7.4.0
- pytest-cov >= 4.1.0
- mypy >= 1.5.0
- black >= 23.7.0
- flake8 >= 6.1.0
- ruff >= 0.1.0

## Verify Installation

After installation, verify everything works:

```bash
# Check CLI is available
docscalpel --version

# Test module import
python -c "from docscalpel import extract_elements; print('✓ Import successful')"

# Run help
docscalpel --help

# Test with a sample PDF (if available)
docscalpel sample.pdf --types figure
```

## Troubleshooting

### Model Download Issues

The DocLayout-YOLO model (~250MB) is downloaded automatically on first run from Hugging Face. If download fails:

1. Check internet connection
2. Verify firewall settings
3. Try manual download from: https://huggingface.co/

### Import Errors

If you get import errors after installation:

```bash
# Ensure the package is installed
pip list | grep docscalpel

# Try reinstalling
pip uninstall docscalpel
pip install -e .
```

### Permission Errors

If you get permission errors on Linux/macOS:

```bash
# Use user install
pip install --user -e .
```

## Uninstallation

```bash
pip uninstall docscalpel
```

## Additional Resources

- [README](README.md) - Main documentation
- [Quick Start Guide](docs/QUICKSTART_CLI.md) - Get started quickly
- [CLI Manual](docs/CLI_MANUAL.md) - Complete CLI reference
- [GitHub Issues](https://github.com/zebehn/docscalpel/issues) - Report bugs
