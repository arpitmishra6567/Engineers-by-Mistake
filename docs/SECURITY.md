# RepairForge AI Security Model & Policy

RepairForge AI operates on source code repositories, executes test suites, and processes arbitrary bug descriptions. This document defines our security model, threat mitigations, and execution boundaries.

---

## 1. Threat Model

When an autonomous repair agent inspects a repository, several threat vectors arise:

1. **Malicious Code Execution**: Untrusted test suites or setup scripts executing destructive shell commands on the host machine.
2. **Path Traversal Attacks**: Malicious bug reports or patches specifying paths like `../../etc/passwd` or `../../.ssh/id_rsa`.
3. **Prompt Injection**: Injected system instructions embedded within issue descriptions or source code comments designed to hijack agent reasoning or extract secrets.
4. **Credential Exfiltration**: Environmental secrets (e.g. `GITHUB_TOKEN`, `OPENAI_API_KEY`) being printed to logs or exfiltrated via network requests.
5. **Denial of Service**: Infinite loops in tests or multi-gigabyte log generation exhausting CPU, disk, or memory.

---

## 2. Security Controls & Mitigations

### 2.1 Untrusted Repository Handling
- **Workspace Isolation**: In demonstration and evaluation runs, repositories are copied into ephemeral temporary directories (`tempfile.mkdtemp()`). The original user repository is never modified directly during evaluation.
- **Path Traversal Protection**: All file read and patch write operations are passed through `SafeFileReader.resolve_safe_path()`. Any target resolving outside the designated repository root raises `PathTraversalError`.
- **File Size Limits**: File reading is capped at a strict upper bound (default 1MB). Oversized files raise `FileSizeExceededError`.

### 2.2 Execution Containment & Policies
- **Execution Policy Modes**:
  - `SAFE_FIXTURE`: Allowed commands are restricted to known test frameworks (`pytest`, `unittest`).
  - `DOCKER_SANDBOX`: Commands execute inside isolated, unprivileged Docker containers with resource limits (future/optional backend).
  - `RESTRICTED_HOST`: Host commands require explicit user approval.
- **Blocked Commands**: The policy engine strictly blocks known destructive shell tokens:
  - `rm -rf`, `format`, `dd`, `mkfs`, `shutdown`, `reboot`
  - Version control commands that alter remote state: `git push`, `git commit`, `git merge`
- **Execution Timeouts**: All subprocesses run under hard timeouts (default 60 seconds). If a command exceeds the limit, it is forcibly terminated, and the execution is logged as `BLOCKED`.

### 2.3 Prompt Injection Defense
- Source code, commit messages, and issue texts are categorized as **data**, never system instructions.
- System prompts are fixed and instruct model adapters to reject instructions embedded in inputs that attempt to override security controls.

### 2.4 Credential Protection
- Secrets are loaded strictly from environment variables (`REPAIRFORGE_API_KEY`, `OPENAI_API_KEY`).
- Secret values are never printed, displayed on the CLI, or written to markdown/JSON repair reports.
- HTTP Authorization headers are stripped from exception messages prior to logging.

### 2.5 Human-in-the-Loop Gate
- RepairForge requires an explicit human review gate before any patch is accepted or deployed.
- Autonomous commits, merges, or deployments to remote repositories are prohibited.

---

## 3. Reporting Security Issues

If you discover a security vulnerability or bypass in RepairForge, please open a private security advisory on GitHub or email the maintainers directly. Do not open public issues for sensitive vulnerabilities.

