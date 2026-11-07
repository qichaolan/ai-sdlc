@AGENTS.md

## Claude Code

- Skills live in `.claude/skills/`. Name the skill in a prompt when it
  matters ("use python-code-review on this diff").
- `.claude/settings.json` asks before pushes and deploys and blocks
  force-pushes, hard resets, and reading `.env`. Its session-start
  hook prints `docs/PROGRESS.md`; still follow `session-memory`.
- Run tests and builds inside the devcontainer (`.devcontainer/`), not
  on the host.
