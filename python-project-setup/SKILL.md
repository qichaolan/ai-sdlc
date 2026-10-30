---
name: python-project-setup
description: "Use when scaffolding a new Python project or modernizing an existing one, especially AI-agent services: uv dependencies, src layout, Ruff/mypy/pytest quality gates, agent instruction files, GitHub Actions CI/CD, GCP Cloud Run deployment, and Secret Manager configuration."
---

# Python Project Setup

Create a **small, reproducible, secure Python project** suitable for AI agents and deployment on Google Cloud. Prefer the repository's existing standards; do not overwrite working configuration just to use these defaults. This skill sets the project up; use `python-development`, `python-testing`, and `python-code-review` for later implementation, tests, and review.

## 1. Inspect Before Changing Anything

- Read `README.md`, `pyproject.toml`, lockfiles, `.gitignore`, `git status`, entry points, CI, and deployment files. Identify the Python version, Git host, CI system, and GCP runtime.
- **Existing project:** propose targeted additions and get agreement before restructuring. Never delete or replace files, branches, secrets, or cloud resources without explicit approval.
- **New project defaults:** `uv`, `pyproject.toml`, `src/` layout, pytest, Ruff, mypy, GitHub Actions, Docker, Artifact Registry, and a **Cloud Run service** for HTTP APIs. Use **Cloud Run Jobs** for finite batch tasks; choose GKE only when requirements justify it.

## 2. Dependencies and Virtual Environments

- Declare a supported Python version in `requires-python` and `.python-version`, and use the same version in the Docker base image. Do not assume a version is installed in the target runtime.
- Start fresh with `uv init --package <name>` (creates the `src/` layout). Add runtime dependencies with `uv add <pkg>` and tools with `uv add --dev pytest pytest-cov ruff mypy` (plus `httpx` for API tests if needed).
- **Commit `uv.lock`**; never edit it by hand. Use `uv sync --locked` in CI and Docker builds so lock drift fails the build.
- Keep `.venv/`, caches, and credentials out of Git and images. No global `pip install` or shared virtualenvs. Prefer few, maintained dependencies.
- Document the required Python/uv versions and a `uv sync` / `uv run` quick start in `README.md`.

## 3. Layout for AI-Agent and GCP Projects

Create **only the directories the application needs**; avoid empty layers and framework lock-in:

```text
project/
├── .claude/skills/             # Existing agent skills; preserve them
├── AGENTS.md                   # Shared agent rules; read by Codex
├── CLAUDE.md                   # Read by Claude Code; imports AGENTS.md
├── codex.md                    # Optional Codex supplement, linked from AGENTS.md
├── .github/workflows/          # ci.yml, deploy.yml
├── src/<package>/
│   ├── api/                    # HTTP routes, health endpoint (if serving HTTP)
│   ├── agents/                 # Orchestration, state, decisions
│   ├── tools/                  # Typed tools and permission boundaries
│   ├── prompts/                # Versioned prompt templates
│   ├── schemas/                # Input/output contracts and validation
│   ├── services/               # Business logic, independent of the LLM
│   ├── integrations/           # GCP/LLM/database adapters, retries
│   └── config.py               # Typed, environment-driven settings
├── tests/                      # unit/, integration/ as needed
├── deploy/                     # Dockerfile, deployment docs
├── .dockerignore               # At the build-context root (repo root)
├── .env.example                # Variable names and harmless placeholders only
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md
```

- Keep orchestration separate from tools and infrastructure adapters. Give tools typed inputs/outputs, explicit timeouts, retries, and error behavior, and least-privilege permissions; no unrestricted arbitrary command execution by default.
- Cloud Run instances are stateless: keep persistent agent state in an external store. Log structured JSON to stdout/stderr, handle `SIGTERM` for graceful shutdown, and bind HTTP servers to `0.0.0.0` on the `PORT` environment variable. Use `/health` (not `/healthz`, which Cloud Run may reserve).
- Follow PEP 8; one responsibility per function (5–20 lines ideal, flag over 50) and cohesive modules (under 300 lines ideal, flag over 500).

## 4. Agent Instruction Files

- If template files (`agent.md`, `claude.md`, `codex.md`) are bundled next to this `SKILL.md`, start from them and adapt package names, commands, and deployment details to the actual repository. Otherwise write the files from the guidance below.
- **New project:**
  - `AGENTS.md`: the shared rules (read automatically by Codex and other agents).
  - `CLAUDE.md`: a line `@AGENTS.md` to import the shared rules, plus only Claude-specific notes (e.g. which `.claude/skills/` to use).
  - `codex.md`: optional Codex workflow notes, linked from `AGENTS.md`.
  - Use these exact filenames; lowercase template names like `agent.md` are not auto-loaded.
- **Existing project:** merge selectively into existing `AGENTS.md` / `CLAUDE.md`; never overwrite them. Do not duplicate content across files.
- Keep instructions short and actionable: layout, coding standards, exact test/lint commands, sandbox boundaries, Git safety, approval requirements, GCP identity, and secret handling. Reference skills only if they exist in the project.

## 5. Code Quality Configuration

Write the configuration into `pyproject.toml` and add starter tests; do not just describe the tools.

- **Ruff:** `line-length = 79`, `target-version` matching `requires-python`, and `[tool.ruff.lint.pycodestyle] max-doc-length = 72`. Select at least `E`, `W`, `F`, `I`, `B`, `UP` (includes `E501` and `W505`). Use `ruff format` for formatting.
- **mypy:** `strict = true` for newly scaffolded code, scoped to `src/<package>`. Add narrow, commented per-module exemptions only when needed.
- **pytest / coverage:** `testpaths = ["tests"]`, branch coverage on, `fail_under = 85` (or the repo's established threshold). Starter tests cover normal cases, boundaries, exceptions, security-relevant inputs, and mocked external services.
- Add `.pre-commit-config.yaml` only if the project wants hooks; CI enforces the checks regardless.
- Quality-gate commands:

```bash
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy src/
uv run pytest -q --cov=<package> --cov-branch --cov-report=term-missing
```

Ruff checks may run on the host. mypy (if plugins are configured), pytest, imports, and builds run project code, so run them **only in a disposable sandbox** (no production credentials, no network by default, unprivileged, bounded resources). A virtualenv is **not** a sandbox. GitHub-hosted CI runners count as disposable; persistent self-hosted runners do not. Never report a check as passed unless it ran.

## 6. Git Pipeline and GCP Deployment

- **Git:** run `git init` only for a new, non-Git project and only when requested. Preserve existing history and uncommitted changes. Work on a task branch such as `agent/project-setup`; never auto-push, merge, force-push, or reset user work.
- **CI (`ci.yml`):** on pull requests and pushes to the main branch: checkout → install a pinned `uv` and Python → `uv sync --locked` → Ruff check/format → mypy → pytest with coverage → optional secret/dependency scanning. Set `permissions: contents: read` at the workflow level, pin third-party actions to a commit SHA, and use `pull_request` (never `pull_request_target`) so fork PRs get no secrets.
- **CD (`deploy.yml`), as a gated template:** runs only after CI succeeds on an approved branch, via a protected GitHub **environment** with required reviewers and a `concurrency` group. Build a minimal multi-stage, non-root image (`docker build -f deploy/Dockerfile .`, `uv sync --locked --no-dev`), tag it with the commit SHA, push to **Artifact Registry**, deploy that immutable image to **Cloud Run**, then check rollout and health. Never deploy from a pull request.
- **Identity:** authenticate with **Workload Identity Federation (OIDC)** via `google-github-actions/auth` (job needs `id-token: write`). Use separate least-privilege **deploy** and **runtime** service accounts, and restrict the provider's attribute condition to the intended repository and branch/environment. **Never create or download long-lived service-account JSON keys.**
- **Parameters:** `GCP_PROJECT_ID`, `GCP_REGION`, `ARTIFACT_REPOSITORY`, `CLOUD_RUN_SERVICE`, `WIF_PROVIDER`, `DEPLOY_SERVICE_ACCOUNT`, `RUNTIME_SERVICE_ACCOUNT`. Document required API enablement, Artifact Registry setup, IAM grants, image retention, observability, and separate staging/production.
- **Approvals:** require explicit user approval for the first deployment, IAM changes, public (unauthenticated) access, and production promotion.
- **Runtime settings:** set CPU/memory, concurrency, request timeout, min/max instances, and egress deliberately. After deploying, verify the service and record the revision; roll back by routing traffic to a previously healthy **Cloud Run revision**, not by rewriting Git history.
- If the organization uses GitLab CI or Cloud Build, adapt to that system instead of adding a second pipeline.

## 7. Configuration and Secrets

- Define **typed settings** with `pydantic-settings` (or a lightweight validated equivalent) and validate required settings at startup. Non-secret configuration comes from environment variables; `.env.example` lists names with safe placeholders.
- Add `.env`, `.env.*` (with `!.env.example`), keys, credential files, and service-account JSON to both `.gitignore` and `.dockerignore`.
- **Local development:** optionally load a Git-ignored `.env`.
- **GCP:** store secrets in **Secret Manager** and grant the runtime service account `roles/secretmanager.secretAccessor` **on specific secrets**, not the project. Prefer reading via the API or a mounted secret volume; if exposing a secret as a Cloud Run environment variable, pin a specific version and document rotation.
- Keep separate `dev`, `staging`, and `prod` configuration and secrets. Mask secrets in logs, errors, test reports, CI output, and agent prompts. Never commit real keys, even as examples, and never expose production credentials to test runs.
- For Vertex AI/Gemini, use **Application Default Credentials** with the runtime service account rather than hard-coded API keys.

## 8. Verify and Hand Off

1. Review every generated file: parse TOML/YAML, confirm `.gitignore`/`.dockerignore` coverage, check for secrets and destructive commands, and review `git diff --check` plus the full diff.
2. Run static checks; run imports, tests, and builds **only in a sandbox** (Section 5). If no sandbox is available, report them as **not run**.
3. Report the file tree, files created or changed, commands actually run and their results, required GCP resources/IAM/variables, and next steps. State clearly which items are **templates** versus actually created, tested, provisioned, or deployed. Never deploy or spend cloud resources without user approval.

**Completion checklist:** agent instruction files · `uv.lock` committed and `uv sync --locked` works · only needed layout directories · Ruff/mypy/pytest configured with starter tests · CI plus gated Cloud Run CD with WIF · typed settings, ignored local secrets, Secret Manager · verification report.
