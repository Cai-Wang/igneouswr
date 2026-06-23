# Repo Documentation Strategy

Three files at repo root, each for a DIFFERENT audience. Never conflate them.

## README.md — End users (geologists / reviewers / supervisors)

- Describes the tool's value proposition in user terms
- No mention of AI agents, skills, or LLMs
- Chinese-facing: pip install, figure list with Chinese names, data quality notes
- The narrative that convinces a PI to allocate manpower
- What NOT to include: API signatures, known pitfalls, workflow rules for agents

## SKILL.md — AI agents (Hermes / Claude Code / Codex, etc.)

- Technical usage manual for the agent that is being asked to USE this tool
- No pip install, no git clone (the agent doesn't execute these)
- API function signatures with parameter tables and return value schemas
- Standard agent workflow (step 1-4)
- Diagram catalog with `Requires` column (which elements needed per diagram)
- Known pitfalls from past fixes (agent reads these before writing code)
- Related skills the agent should load

## AGENTS.md — Code contributors (agent modifying the source)

- Project-specific code style rules (no pytest, boundary JSON not function code, etc.)
- Workflow rules (run quick_validate.py after any change, update registry)
- Files the agent should NOT modify without explicit instruction
- Architecture overview for navigation

## Git pushing rules

- Commit only: code, boundary JSONs, test scripts, README, AGENTS.md, pyproject.toml, .gitignore
- Do NOT commit: audit reports, review checklists, dev notes, fix annotations in docstrings
- Hermes skill `references/` is local-only (under ~/.hermes/skills/) — never pushed to GitHub
- Always `git status` before commit to catch unintended new files picked up by `git add -A`
