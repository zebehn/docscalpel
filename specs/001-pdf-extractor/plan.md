# Implementation Plan: PDF Element Extractor

**Branch**: `001-pdf-extractor` | **Date**: 2025-11-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-pdf-extractor/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a PDF element extraction application that detects and extracts figures, tables, and equations from technical papers. The system is organized as a core library providing extraction functionality, with a CLI application layer for user interaction. The library must be independently testable and support both JSON and human-readable output formats.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: PyMuPDF (fitz), doclayout-yolo, pdfplumber, pytest
**Storage**: Files only (input PDFs, output extracted PDFs)
**Testing**: pytest with contract, integration, and unit test layers
**Target Platform**: Cross-platform desktop (Linux, macOS, Windows)
**Project Type**: Single project (library + CLI application)
**Performance Goals**: Process 20-page PDF in 15-25 seconds (target <30s), 100-page PDFs without degradation
**Constraints**: 85-90% detection accuracy baseline (path to 95% via fine-tuning), preserve original PDF quality (lossless)
**Scale/Scope**: Single-user CLI tool processing one PDF at a time, academic paper PDFs (typically 5-100 pages)

**Note**: All NEEDS CLARIFICATION items resolved via research.md. See research.md for detailed technology selection rationale.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

This section verifies compliance with the Figure Extractor Constitution (v1.0.0).

### I. Library-First Architecture
- [x] Feature designed as standalone library (core extraction library + thin CLI wrapper)
- [x] Library has clear, documented interface (extract() function with typed parameters and results)
- [x] Library is independently testable (can test extraction logic without CLI)
- [x] Library has single, well-defined purpose (PDF element detection and extraction)
- [x] No implicit dependencies on parent systems (library accepts file paths, returns results)

### II. Test-Driven Development (NON-NEGOTIABLE)
- [x] Tests will be written BEFORE implementation
- [x] Tests will be reviewed and approved BEFORE coding begins
- [x] Red-Green-Refactor cycle will be followed
- [x] Contract tests planned for library interfaces (test extract() function contract, input/output formats)
- [x] Integration tests planned for inter-library communication (test CLI→library interaction, PDF library integration)

### III. Simplicity & Clear Contracts
- [x] Text-based I/O planned (stdin/args → stdout for CLI, library returns structured data)
- [x] JSON and human-readable output supported (CLI can output both formats)
- [x] Structured logging included (detection progress, extraction results, errors)
- [x] APIs have explicit, versioned contracts (library interface v1.0.0 with typed parameters)
- [x] Complexity justified (no unnecessary abstractions - direct PDF processing, no over-engineering)

**Status**: [x] PASS

**Complexity Justifications** (if any): None - design follows all constitutional principles without exceptions.

**Post-Design Verification** (Phase 1 complete):
- ✅ **data-model.md**: Entities (Document, Element, BoundingBox, etc.) are simple dataclasses, no unnecessary abstraction
- ✅ **contracts/library-interface.md**: `extract_elements()` function has explicit v1.0.0 contract with typed parameters and results
- ✅ **contracts/cli-interface.md**: CLI uses stdin/args → stdout pattern, supports JSON and text output, follows Unix conventions
- ✅ **quickstart.md**: Test scenarios validate library independently of CLI, demonstrating Library-First Architecture
- ✅ **research.md**: Technology choices (PyMuPDF, DocLayout-YOLO) are mature, well-documented libraries; no over-engineering

**Final Gate Status**: PASS - All constitutional requirements verified in design artifacts.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── lib/                    # Core extraction library
│   ├── extractor.py       # Main extraction orchestrator
│   ├── detectors/         # Element detection implementations
│   │   ├── figure_detector.py
│   │   ├── table_detector.py
│   │   └── equation_detector.py
│   ├── pdf_processor.py   # PDF parsing and page handling
│   ├── cropper.py         # PDF cropping and output generation
│   └── models.py          # Data models (Document, Element, BoundingBox, etc.)
│
└── cli/                   # CLI application layer
    ├── main.py            # CLI entry point and argument parsing
    ├── formatter.py       # Output formatting (JSON, human-readable)
    └── logger.py          # Structured logging configuration

tests/
├── contract/              # Library interface contract tests
│   ├── test_extractor_contract.py
│   └── test_output_formats.py
│
├── integration/           # Cross-component integration tests
│   ├── test_cli_library_integration.py
│   ├── test_full_extraction_workflow.py
│   └── test_pdf_library_integration.py
│
└── unit/                  # Unit tests for individual components
    ├── test_detectors.py
    ├── test_pdf_processor.py
    ├── test_cropper.py
    └── test_cli.py

fixtures/                  # Test PDF files
├── sample_paper_with_figures.pdf
├── sample_paper_with_tables.pdf
└── sample_paper_mixed.pdf
```

**Structure Decision**: Single project structure selected. The design follows Library-First Architecture with clear separation between the core library (`src/lib/`) and CLI application (`src/cli/`). The library is independently testable and has no dependencies on the CLI layer. Test organization follows TDD principles with contract tests for library interfaces, integration tests for component interactions, and unit tests for individual components.

## Complexity Tracking

No constitutional violations - this section is not applicable.
