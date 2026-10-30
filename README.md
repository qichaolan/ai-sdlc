# ai-sdlc

Agent skills for the Python development lifecycle, for use with Claude Code, Codex, and similar coding agents.

## Skills

| Skill | Use it when |
| --- | --- |
| [python-project-setup](python-project-setup/SKILL.md) | Scaffolding or modernizing a project (uv, Ruff, mypy, pytest, GitHub Actions, GCP Cloud Run) |
| [python-development](python-development/SKILL.md) | Implementing, fixing, or refactoring code |
| [python-testing](python-testing/SKILL.md) | Writing, running, or debugging pytest tests with coverage |
| [python-code-review](python-code-review/SKILL.md) | Reviewing code, diffs, or pull requests |

## Installation

Copy the skills into `.claude/skills/` in a project, or into `~/.claude/skills/` to use them everywhere:

```bash
cp -r python-* .claude/skills/
```
