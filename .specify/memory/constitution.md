<!--
  SYNC IMPACT REPORT - Constitution Update
  ========================================

  Version Change: [NEW] → 1.0.0

  Principles Defined:
  - I. Library-First Architecture (NEW)
  - II. Test-Driven Development - Non-Negotiable (NEW)
  - III. Simplicity & Clear Contracts (NEW)

  Sections Added:
  - Core Principles (3 principles)
  - Development Workflow
  - Governance

  Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md - Constitution Check section updated with v1.0.0 gates
  ✅ .specify/templates/spec-template.md - User scenarios and requirements align
  ✅ .specify/templates/tasks-template.md - Test-first workflow aligned with TDD principle
  ✅ .specify/templates/checklist-template.md - Generic template, no changes needed
  ✅ .specify/templates/agent-file-template.md - Generic template, no changes needed

  Command Files Validated:
  ✅ .claude/commands/speckit.plan.md - Uses agent-agnostic update scripts
  ✅ .claude/commands/speckit.tasks.md - Aligned with TDD and library-first principles

  Follow-up TODOs:
  - None - all templates and commands are consistent with constitution v1.0.0

  Ratification: 2025-11-19
  Last Amendment: 2025-11-19
-->

# Figure Extractor Constitution

## Core Principles

### I. Library-First Architecture

Every feature in Figure Extractor MUST be designed and implemented as a standalone library before integration.

**Requirements**:
- Libraries MUST be self-contained with no implicit dependencies on parent systems
- Libraries MUST have clear, documented interfaces and contracts
- Libraries MUST be independently testable without requiring full system context
- Libraries MUST have a single, well-defined purpose
- No "organizational-only" libraries - every library must solve a concrete technical problem

**Rationale**: Library-first architecture enforces modularity, enables independent testing, facilitates reuse, and maintains clear boundaries. This prevents tight coupling and makes the system more maintainable as it grows.

---

### II. Test-Driven Development (NON-NEGOTIABLE)

Test-Driven Development is MANDATORY for all code in Figure Extractor. No exceptions.

**Requirements**:
- Tests MUST be written BEFORE implementation code
- Tests MUST be reviewed and approved by stakeholders BEFORE implementation begins
- Tests MUST fail initially (red state) to verify they actually test the feature
- Implementation MUST make the tests pass (green state)
- Code MUST be refactored while keeping tests passing (refactor state)
- The Red-Green-Refactor cycle MUST be strictly followed

**Integration Testing Focus**:
- Contract tests MUST be written for new library interfaces
- Contract tests MUST be written when library interfaces change
- Integration tests MUST be written for inter-library communication
- Integration tests MUST validate shared data schemas and contracts

**Rationale**: TDD ensures code correctness, provides living documentation, enables fearless refactoring, and catches bugs at write-time rather than runtime. The non-negotiable nature prevents technical debt accumulation and maintains long-term code quality.

---

### III. Simplicity & Clear Contracts

Figure Extractor prioritizes simplicity and explicit contracts over clever abstractions.

**Requirements**:
- Text-based I/O MUST be the default (stdin/args → stdout, errors → stderr)
- Libraries MUST support both JSON and human-readable output formats
- Structured logging MUST be used for all significant operations
- Error messages MUST be actionable and include context
- Complexity MUST be justified - if a simpler solution exists, use it (YAGNI principle)
- APIs and interfaces MUST have explicit, versioned contracts
- Breaking changes MUST follow semantic versioning (MAJOR.MINOR.PATCH)

**Rationale**: Text I/O ensures debuggability and composability with standard Unix tools. Clear contracts prevent integration surprises. Simplicity reduces cognitive load and maintenance burden. Structured logging enables observability without specialized tools.

---

## Development Workflow

### Quality Gates

All code changes MUST pass these gates before merge:

1. **Tests First**: Tests written, reviewed, approved, and failing
2. **Implementation**: Code makes tests pass
3. **Contract Verification**: Library interfaces documented and tested
4. **Constitution Compliance**: All principles verified
5. **Review Approval**: Peer review confirms quality and compliance

### Complexity Justification

Any deviation from simplicity (e.g., introducing new abstractions, patterns, or dependencies) MUST be justified in writing with:
- The specific problem requiring complexity
- Why simpler alternatives are insufficient
- The expected maintenance cost

### Integration Requirements

When libraries interact:
- Contracts MUST be explicitly defined and documented
- Contract tests MUST verify both sides of the interface
- Version compatibility MUST be tracked and validated
- Breaking changes MUST be coordinated and documented

---

## Governance

### Authority

This constitution supersedes all other development practices, guidelines, and preferences. When in conflict, the constitution takes precedence.

### Amendments

Constitution amendments require:
1. Written proposal with rationale
2. Impact analysis on existing code and templates
3. Team approval/consensus
4. Version update following semantic versioning
5. Migration plan for affected code (if applicable)
6. Update of all dependent templates and documentation

### Compliance

- All code reviews MUST verify constitutional compliance
- Pull requests MUST include a compliance statement
- Non-compliance MUST be rejected unless accompanied by an approved amendment proposal
- Regular compliance audits SHOULD be conducted

### Versioning Policy

Constitution versions follow semantic versioning:
- **MAJOR**: Backward incompatible governance changes or principle removals/redefinitions
- **MINOR**: New principles added or materially expanded guidance
- **PATCH**: Clarifications, wording improvements, typo fixes

### Runtime Development Guidance

For day-to-day development workflows, patterns, and practical implementation guidance, refer to project-specific documentation (README.md, docs/development.md, etc.). The constitution defines what MUST be done; runtime guidance documents describe how to do it effectively.

---

**Version**: 1.0.0 | **Ratified**: 2025-11-19 | **Last Amended**: 2025-11-19
