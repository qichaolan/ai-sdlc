# Harness

A starter kit that wraps the ai-sdlc skills in the parts skills can't
provide on their own: a router, enforced rules, a sandbox, a
session-start hook, and human approval gates. Copy it into a Python
project, fill in the placeholders, and agents follow the same workflow
in every repo.

Skills are instructions an agent may load. Anything that must happen
belongs in this harness (CI, permission rules, hooks), and judgment
calls stay in the skills.

## What's in it

| Layer | File | What it does |
| --- | --- | --- |
| Router | [AGENTS.md](AGENTS.md) | Routes tasks to skills; holds project settings, the Definition of Done, standards, and safety rules. Read by Claude Code, Codex, and similar agents. |
| Router | [CLAUDE.md](CLAUDE.md) | Imports `AGENTS.md` and adds Claude Code notes. |
| Enforcement | [.github/workflows/ci.yml](.github/workflows/ci.yml) | Lint, mypy, tests, the coverage gate, and OpenSpec validation on every push and pull request. |
| Enforcement | [scripts/check_coverage.py](scripts/check_coverage.py) | Fails when branch or function coverage is under the threshold, per file or overall. Standard library only. |
| Enforcement | [.claude/settings.json](.claude/settings.json) | Asks before pushes, merges, and deploys; blocks force-pushes (any argument order, `+refspec`), hard resets, service-account key creation, and reading `.env` or credential files. |
| Sandbox | [scripts/test-offline.sh](scripts/test-offline.sh) | Runs tests and the coverage gate in Docker with no network, no Linux capabilities, a non-root user, CPU, memory, and process limits, and a timeout. Meets the sandbox rules in `python-development` and `python-testing`. |
| Sandbox | [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json) | Python 3.12, uv, Node (for OpenSpec), and Claude Code in a container with no Linux capabilities, no `sudo`, and CPU, memory, and process limits. The place to run the agent itself. |
| Session start | [.claude/settings.json](.claude/settings.json) | Hook that prints `docs/PROGRESS.md` at startup, resume, clear, and compaction, so the handoff loads even if the `session-memory` skill isn't matched. |
| Human gates | [.github/CODEOWNERS](.github/CODEOWNERS) | Requires the owner's review on specs, agent rules, the harness, and coverage settings. |
| Human gates | [openspec/config.yaml](openspec/config.yaml) | Makes proposals flag changes that need owner approval and keeps deploy, push, and IAM steps out of task lists. |

## Set up a project

1. Copy the harness and the skills into the project root. From a clone
   of ai-sdlc:

   ```bash
   cd /path/to/project
   AI_SDLC=/path/to/ai-sdlc
   cp -r "$AI_SDLC"/harness/{AGENTS.md,CLAUDE.md,scripts,.claude,.github,.devcontainer} .
   cp -r "$AI_SDLC"/harness/openspec .    # only if you use OpenSpec
   mkdir -p .claude/skills
   cp -r "$AI_SDLC"/{python-*,web-app-security-review,backend-security-review-gcp-docker,design-review-web-ux,tech-doc-writer-reviewer,openspec-*,session-memory} .claude/skills/
   ```

   This overwrites files with the same names. Merge by hand if the
   project already has an `AGENTS.md`, `.claude/settings.json`, or a CI
   workflow.

2. Replace every `<placeholder>` in `AGENTS.md`,
   `openspec/config.yaml`, `.github/workflows/ci.yml`, and
   `.github/CODEOWNERS`. Delete sections that don't apply, such as
   OpenSpec. To find what's left:

   ```bash
   grep -rn '<[A-Za-z]' AGENTS.md openspec/config.yaml .github/
   ```

3. Add the dev tools and their settings to `pyproject.toml`. The
   values match the standards in `AGENTS.md`; change both together.

   ```bash
   uv add --dev pytest pytest-cov ruff mypy
   ```

   ```toml
   [tool.ruff]
   line-length = 79

   [tool.mypy]
   strict = true
   files = ["src", "tests", "scripts"]

   [tool.coverage.run]
   source = ["src"]
   branch = true

   [tool.coverage.report]
   fail_under = 90
   ```

4. If you use OpenSpec, run `openspec init` and pin its version in the
   `specs` CI job.

5. Open the project in the devcontainer and start Claude Code there,
   or work on the host and run tests with `scripts/test-offline.sh`.
   Ask the agent to "set up session memory" to create
   `docs/PROGRESS.md`.

6. On GitHub, protect `main`: require pull requests, make the CI jobs
   required checks, and require review from code owners. If you add a
   deploy workflow, run it in a GitHub environment with required
   reviewers so every deploy waits for your approval.

## Daily workflow

- **New feature:** `openspec-explore` → `openspec-propose` → you
  approve → `openspec-apply-change` (with `python-development` and
  `python-testing`) → `python-code-review` in a fresh session →
  `openspec-archive-change` → `python-release`.
- **Bug fix or refactor:** `python-development` and `python-testing`,
  then `python-code-review`.
- **Security:** `web-app-security-review` and
  `backend-security-review-gcp-docker` before a launch or after a
  security-sensitive change.
- **Docs and UX:** `tech-doc-writer-reviewer` and
  `design-review-web-ux` before the review.
- **Every session:** `session-memory` at the start and end. The hook
  only *reads* the handoff file; the agent must still *write* it before
  stopping or before the context is compacted.

## Limits

- **Permission rules match command text.** They stop accidents, not a
  determined workaround such as a script or alias that pushes. Branch
  protection and required CI checks are the real backstop.
- **The session-start hook is Claude Code only.** Codex and other
  agents rely on the `session-memory` line in `AGENTS.md`. Nothing
  forces the handoff to be written before compaction.
- **The devcontainer keeps network access,** so the agent can install
  packages and reach APIs. Don't forward cloud credentials or SSH
  agents into it. For network-free tests, run `scripts/test-offline.sh`
  on the host. The Claude Code feature's optional firewall script needs
  `sudo` and `NET_ADMIN`, which this hardening removes.
- **`scripts/test-offline.sh` needs Docker** and a project path shared
  with the Docker VM. Docker Desktop and Colima share your home folder
  by default. The script picks the uv image from `.python-version`.
- **CODEOWNERS can't gate a PR its owner opened.** GitHub doesn't allow
  approving your own PR, so give agents a separate bot account if you
  want this gate.
- **The coverage gate needs function data in the JSON report.** It was
  tested with coverage.py 7.13 and exits with code 2 on a report
  without it.
- **CI doesn't deploy.** Deployment stays a separate, approved step;
  see the `python-release` skill.
