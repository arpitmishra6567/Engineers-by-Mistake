# RepairForge AI Development Guide

This guide covers setting up your local development environment, running tests, and contributing to RepairForge AI.

---

## 1. Prerequisites

- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Git
- Virtual environment tool (`venv` or `uv`)

---

## 2. Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/arpitmishra6567/Engineers-by-Mistake.git
   cd Engineers-by-Mistake
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies and editable package:**
   ```bash
   pip install --upgrade pip
   pip install -e ".[dev,openai]"
   ```

---

## 3. Running the Test Suite

Execute all unit and integration tests using `pytest`:

```bash
python -m pytest -v
```

Run tests with coverage reporting:
```bash
python -m pytest --cov=repairforge tests/
```

Run specific test modules:
```bash
python -m pytest tests/unit/test_state.py
python -m pytest tests/integration/test_demo_flow.py
```

---

## 4. Running the CLI Locally

Validate the CLI commands:

```bash
# Print version
repairforge version

# Inspect current repository
repairforge inspect --repo .

# Validate Agent Skill package
repairforge skill validate

# Run the deterministic demo
repairforge demo

# View the latest generated report
repairforge report --latest
```

---

## 5. Coding Standards

- **Type Annotations**: All new functions and methods must include Python type hints.
- **Docstrings**: Provide clear docstrings explaining component behavior and arguments.
- **Safety**: Never execute unsanitized shell commands or access filesystem paths without using `SafeFileReader`.
- **Honest Evidence**: Never mock test successes in integration tests or fabricate benchmark results.

