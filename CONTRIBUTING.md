# Contributing to RepairForge AI

Thank you for your interest in contributing to RepairForge AI! We welcome contributions from developers, researchers, and reliability engineers.

## Contribution Guidelines

1. **Evidence-Driven**: Every fix, patch, or feature must be accompanied by automated tests demonstrating before-and-after behavior.
2. **Safety First**: Do not bypass execution containment policies or path traversal guards.
3. **No Fabricated Benchmarks**: We believe in honest evaluation. Never submit synthetic metrics presented as real LLM benchmark results.

## Pull Request Workflow

1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. Set up your virtual environment and install test dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Ensure all tests pass:
   ```bash
   python -m pytest
   ```
4. Verify the CLI demo runs cleanly:
   ```bash
   repairforge demo
   ```
5. Submit your pull request with a detailed description of your changes and test evidence.

