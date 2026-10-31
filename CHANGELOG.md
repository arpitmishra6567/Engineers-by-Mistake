# Changelog

All notable changes to RepairForge AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-31

### Added
- **Core Orchestrator**: Checkpoint-based state machine managing the 7-phase repair lifecycle (`INITIALIZED` through `COMPLETED`).
- **Model Adapter Layer**: Abstract `BaseModelAdapter` with deterministic `MockModelAdapter` and configurable `OpenAICompatibleModelAdapter`.
- **Repository Analyzer**: File reader with path-traversal prevention, language detection, dependency parsing, and directory exclusion.
- **Bug Investigation**: `IssueParser`, `BugInvestigator`, `BugReproducer`, and evidence-grounded `RootCauseAnalyzer`.
- **Patch Generation & Verification**: Unified diff generator, `PatchApplier` with rollback capabilities, and `PatchVerifier` enforcing regression testing.
- **Execution Safety Policy**: Command whitelisting, timeout enforcement, path containment, and blocked dangerous commands (`rm -rf`, `git push`).
- **Evaluation & Reporting**: Metrics calculation, structured JSON exports, and GitHub-flavored Markdown reports.
- **CLI**: Typer-based CLI with `version`, `inspect`, `demo`, `skill validate`, and `report` commands.
- **Agent Skill**: `bugrepro` standard Agent Skill package with `SKILL.md`, supporting references, validation script, and bug report template.
- **Example Fixture**: Deterministic `buggy_average` zero-division repair demonstration.
- **Testing Suite**: 25 unit and integration tests covering models, state transitions, repository safety, and end-to-end repair.
- **Documentation**: Comprehensive architecture, security guidelines, development instructions, and Kaggle Qwen experiment setup.

