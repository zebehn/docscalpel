# Changelog

All notable changes to DocScalpel will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-09

### Added
- **Subfigure merging**: Automatically merge multiple detected figures that share the same caption (e.g., subfigures a, b, c that belong to "Figure 7")
- **Synthetic caption detection**: When YOLO misses a caption but the figure number exists in the text, create synthetic captions to maintain correct numbering
- **Position-based caption matching**: For pages with multiple figures and captions, use spatial position to correctly associate them

### Improved
- **Caption association logic**: Better handling of pages with multiple figures and/or captions
- **Figure numbering accuracy**: More robust extraction of figure numbers from various caption formats
- **Logging**: More informative debug messages for caption parsing and figure merging

### Fixed
- Fixed issue where subfigures detected separately would get incorrect sequential numbers instead of sharing their parent figure number

## [1.0.0] - 2025-01-08

### Added
- Initial release
- Extract figures, tables, and equations from PDF documents
- DocLayout-YOLO integration for deep learning-based detection
- Caption parsing for intelligent figure/table numbering
- Multi-part figure merging for overlapping detections
- CLI application with comprehensive options
- Library API for programmatic use
- JSON and text output formats
- Configurable confidence thresholds and boundary padding
