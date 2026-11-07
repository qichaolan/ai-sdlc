@AGENTS.md

## Claude Code

- Skills live in `.claude/skills/`. Name the skill in a prompt when it
  matters ("use python-code-review on this diff").
- `.claude/settings.json` asks before pushes and deploys and blocks
  force-pushes, hard resets, and reading `.env`. Its session-start
  hook prints `docs/PROGRESS.md` but never writes it: refresh the file
  with `session-memory` before the context is compacted or cleared.
- Run tests inside the devcontainer (`.devcontainer/`), or on the host
  with `scripts/test-offline.sh`, never with a plain `uv run pytest` on
  the host.
