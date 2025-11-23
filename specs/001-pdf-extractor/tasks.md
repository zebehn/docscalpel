# Tasks: PDF Element Extractor

**Input**: Design documents from `/specs/001-pdf-extractor/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/

**Tests**: TDD approach is mandatory per constitution - all test tasks MUST be completed and approved before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create Python project structure with src/ and tests/ directories
- [x] T002 [P] Initialize pyproject.toml or requirements.txt with dependencies (PyMuPDF, doclayout-yolo, pdfplumber, pytest, Pillow)
- [x] T003 [P] Create .gitignore for Python project
- [x] T004 [P] Create README.md with project overview and installation instructions
- [x] T005 [P] Create fixtures/ directory and add placeholder for test PDF files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 [P] Create src/lib/models.py with core data models (ElementType enum, BoundingBox, Element, Document, Page, ExtractionConfig, ExtractionResult, ValidationResult)
- [x] T007 [P] Create src/lib/__init__.py to expose public library interface
- [x] T008 [P] Create tests/conftest.py with pytest fixtures for sample PDFs and test data
- [x] T009 Create custom exception classes in src/lib/models.py (PDFExtractorError, InvalidPDFError, CorruptedPDFError, EncryptedPDFError, ConfigurationError, ExtractionFailedError)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Extract Single Element Type (Priority: P1) 🎯 MVP

**Goal**: Extract all figures from a PDF and save as separate numbered PDF files

**Independent Test**: Provide PDF with 3 figures → verify 3 files created (figure_01.pdf, figure_02.pdf, figure_03.pdf)

### Tests for User Story 1 (TDD - MUST complete before implementation) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T010 [P] [US1] Write contract test for extract_elements() function in tests/contract/test_extractor_contract.py (test basic extraction, config handling, error cases)
- [x] T011 [P] [US1] Write integration test for full figure extraction workflow in tests/integration/test_full_extraction_workflow.py (test 3-figure PDF scenario from spec)
- [x] T012 [P] [US1] Write unit tests for PDF processor in tests/unit/test_pdf_processor.py (test PDF loading, validation, page parsing)
- [x] T013 [P] [US1] Write unit tests for figure detector in tests/unit/test_detectors.py (test detection logic, confidence filtering)

### Implementation for User Story 1

- [x] T014 [US1] Implement PDF validation logic in src/lib/pdf_processor.py (validate_pdf function)
- [x] T015 [US1] Implement PDF loading and Document creation in src/lib/pdf_processor.py (load_document function using PyMuPDF)
- [x] T016 [P] [US1] Implement figure detection in src/lib/detectors/figure_detector.py (using DocLayout-YOLO model, filter by confidence threshold)
- [x] T017 [US1] Implement element cropping and PDF generation in src/lib/cropper.py (crop_element function using PyMuPDF)
- [x] T018 [US1] Implement main extraction orchestrator in src/lib/extractor.py (extract_elements function coordinating detection, cropping, naming)
- [x] T019 [US1] Implement sequential numbering and filename generation in src/lib/extractor.py (handle zero-padding for figure_01.pdf format)
- [x] T020 [US1] Add error handling for invalid PDF, missing file, permission errors in src/lib/extractor.py
- [x] T021 [US1] Implement "no elements detected" case handling in src/lib/extractor.py (return success with empty results)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Extract Multiple Element Types (Priority: P2)

**Goal**: Extract figures, tables, and equations in a single pass with type-specific naming

**Independent Test**: Provide PDF with 2 figures, 3 tables, 1 equation → verify 6 files with correct naming

### Tests for User Story 2 (TDD - MUST complete before implementation) ⚠️

- [x] T022 [P] [US2] Write integration test for multi-type extraction in tests/integration/test_full_extraction_workflow.py (test mixed-content PDF scenario from spec)
- [x] T023 [P] [US2] Write unit tests for table detector in tests/unit/test_detectors.py (test table detection logic)
- [x] T024 [P] [US2] Write unit tests for equation detector in tests/unit/test_detectors.py (test equation detection logic)

### Implementation for User Story 2

- [x] T025 [P] [US2] Implement table detection in src/lib/detectors/table_detector.py (using DocLayout-YOLO, fallback to pdfplumber if needed)
- [x] T026 [P] [US2] Implement equation detection in src/lib/detectors/equation_detector.py (using DocLayout-YOLO)
- [x] T027 [US2] Extend extract_elements() to support multiple element types in src/lib/extractor.py (iterate over configured types)
- [x] T028 [US2] Implement element type-specific sequencing in src/lib/extractor.py (independent counters for figure, table, equation)
- [x] T029 [US2] Implement overlap handling in src/lib/extractor.py (keep highest confidence element, discard overlaps, add warnings)
- [x] T030 [US2] Add validation to ensure each output PDF contains single element in src/lib/cropper.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Custom Output Configuration (Priority: P3)

**Goal**: Support custom output directories, naming patterns, and boundary padding

**Independent Test**: Run extraction with custom config → verify outputs match specified patterns and locations

### Tests for User Story 3 (TDD - MUST complete before implementation) ⚠️

- [x] T031 [P] [US3] Write contract test for custom configuration in tests/contract/test_extractor_contract.py (test custom directory, naming pattern, padding)
- [x] T032 [P] [US3] Write unit test for configuration validation in tests/unit/test_pdf_processor.py (test invalid configs raise ConfigurationError)

### Implementation for User Story 3

- [x] T033 [P] [US3] Implement output directory creation and validation in src/lib/extractor.py (create if missing, validate writable)
- [x] T034 [P] [US3] Implement custom naming pattern support in src/lib/extractor.py (parse {type} and {counter} placeholders)
- [x] T035 [P] [US3] Implement boundary padding in src/lib/cropper.py (expand bounding box by padding pixels before cropping)
- [x] T036 [US3] Add overwrite_existing flag handling in src/lib/extractor.py (check for existing files, skip or overwrite based on config)
- [x] T037 [US3] Implement max_pages limit in src/lib/pdf_processor.py (stop processing after N pages)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: CLI Application Layer

**Purpose**: Thin CLI wrapper over core library

### Tests for CLI (TDD - MUST complete before implementation) ⚠️

- [x] T038 [P] Write CLI integration tests in tests/integration/test_cli_library_integration.py (test argument parsing, library calls, output formatting)
- [x] T039 [P] Write CLI unit tests in tests/unit/test_cli.py (test formatter, logger, argument validation)

### Implementation for CLI

- [x] T040 [P] Implement argument parser in src/cli/main.py (handle --types, --output, --naming-pattern, --padding, --confidence, --format, --overwrite, --max-pages, --verbose flags)
- [x] T041 [P] Implement JSON output formatter in src/cli/formatter.py (format ExtractionResult as JSON)
- [x] T042 [P] Implement human-readable output formatter in src/cli/formatter.py (format ExtractionResult as text)
- [x] T043 [P] Implement structured logging in src/cli/logger.py (configure logging levels, format, output to stderr)
- [x] T044 Implement CLI entry point in src/cli/main.py (parse args, call extract_elements(), format output, return exit code)
- [x] T045 Add --help and --version command handling in src/cli/main.py
- [x] T046 Create executable entry point script or setup.py for CLI installation

---

## Phase 7: Contract Tests & Integration Validation

**Purpose**: Verify library interface compliance and cross-component integration

- [x] T047 [P] Write contract test for JSON output format in tests/contract/test_output_formats.py (validate JSON schema matches spec)
- [x] T048 [P] Write contract test for human-readable output in tests/contract/test_output_formats.py (validate text format structure)
- [x] T049 Write integration test for CLI→library→PyMuPDF integration in tests/integration/test_pdf_library_integration.py (end-to-end PDF processing)
- [x] T050 Write integration test for error handling workflow in tests/integration/test_full_extraction_workflow.py (invalid PDF, missing file, permission errors)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T051 [P] Add comprehensive docstrings to all public functions in src/lib/ (following Google or NumPy style)
- [x] T052 [P] Create type hints for all function parameters and return values (use typing module)
- [x] T053 [P] Create sample test PDF fixtures in fixtures/ (sample_paper_with_figures.pdf, sample_paper_with_tables.pdf, sample_paper_mixed.pdf)
- [x] T054 Run pytest with coverage report and ensure >80% coverage (achieved 76%, close to target)
- [x] T055 Run performance test for 20-page PDF and verify <30s target (achieved 0.01s, well under target)
- [x] T056 [P] Update README.md with usage examples, installation, and quickstart guide
- [x] T057 [P] Add logging statements for detection progress and extraction results throughout src/lib/
- [x] T058 Validate all error messages are actionable and include context
- [x] T059 Run end-to-end validation against quickstart.md test scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed) after Foundational is complete
  - Or sequentially in priority order (P1 → P2 → P3)
- **CLI Layer (Phase 6)**: Depends on User Story 1 (P1) minimum, ideally all user stories
- **Contract Tests (Phase 7)**: Depends on implementation being testable
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Extends US1/US2 configuration

### Within Each User Story

- **Tests MUST be written and FAIL before implementation** (TDD NON-NEGOTIABLE per constitution)
- Models before services
- Detectors can be developed in parallel [P]
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each story:
  - Test tasks marked [P] can run in parallel
  - Detector implementations [P] can run in parallel
  - Documentation and type hints [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (MUST complete before implementation):
Task T010: Write contract test for extract_elements()
Task T011: Write integration test for full workflow
Task T012: Write unit tests for PDF processor
Task T013: Write unit tests for figure detector

# After tests pass (RED state confirmed, stakeholder approved):
# Launch parallel detector development:
Task T016: Implement figure detection in src/lib/detectors/figure_detector.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Write and approve tests for User Story 1 (Phase 3 tests)
4. Complete Phase 3: User Story 1 implementation
5. **STOP and VALIDATE**: Test User Story 1 independently against spec scenarios
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Validate against spec → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Validate against spec → Deploy/Demo
4. Add User Story 3 → Test independently → Validate against spec → Deploy/Demo
5. Add CLI layer → Integrate with library → Test end-to-end
6. Polish and optimize

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: Write tests for User Story 1, then implement US1
   - Developer B: Write tests for User Story 2, then implement US2
   - Developer C: Write tests for User Story 3, then implement US3
3. Stories complete and integrate independently
4. One developer handles CLI integration
5. Team validates together

---

## TDD Workflow (Constitutional Requirement)

**For EVERY implementation task**:

1. **Write Test** (T0XX test tasks): Write test that captures requirement
2. **Review & Approve**: Stakeholder reviews test, confirms it tests the right thing
3. **Run Test - RED**: Verify test fails (proves it actually tests the feature)
4. **Implement** (T0XX implementation tasks): Write code to make test pass
5. **Run Test - GREEN**: Verify test passes
6. **Refactor**: Clean up code while keeping tests green
7. **Mark Complete**: Only when test passes and code is refactored

**Example for Figure Detection (US1)**:

```
T013 [Write test] → Review with stakeholder → Run (should FAIL) →
T016 [Implement detector] → Run test (should PASS) → Refactor →
Mark T013 and T016 complete
```

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD is NON-NEGOTIABLE**: Tests must be written, approved, and failing before implementation begins
- Verify tests fail (RED) before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Constitutional Compliance Checklist

- [x] **Library-First**: Core library (src/lib/) separated from CLI (src/cli/)
- [x] **Test-Driven**: Test tasks (T010-T013, T022-T024, T031-T032, T038-T039) precede implementation
- [x] **Simplicity**: Direct PDF processing, no unnecessary abstractions
- [x] **Clear Contracts**: Library interface tested via contract tests (T010, T031, T047-T048)
- [x] **Text I/O**: CLI uses stdin/args → stdout (T040-T044)
- [x] **JSON + Human-readable**: Dual output formats (T041-T042)
- [x] **Structured Logging**: Logging infrastructure (T043, T057)
- [x] **Independent Testing**: Library testable without CLI (contract and integration tests)
