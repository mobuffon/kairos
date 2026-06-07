# CLAUDE.md
# Claude reads this file automatically when working in this repository.
# This file shares the same instruction set as .cursor/rules — both tools operate identically.

This file imports the shared agent rules. All instructions are in `.cursor/rules`.
Claude: read `.cursor/rules` now and treat it as your primary instruction set for this project.

In addition to those rules, note the following Claude-specific context:

## Running in Claude Code or claude.ai

- You have access to bash, file tools, and the full codebase
- Treat every session as potentially unattended unless the user says otherwise
- If running via `claude` CLI with no active user session, default to unattended mode automatically
- Commit after each significant unit of work — do not batch everything into one final commit

## Memory across sessions

You do not have persistent memory between sessions. Compensate for this:
- Always read `docs/agent/PLAN.md` at the start of a session to understand current state
- Always read `docs/agent/SCRATCHPAD.md` to see if a previous session left in-progress notes
- Always check `git log --oneline -20` to understand what was last done
- Check `BLOCKERS.md` if it exists — it means a previous run hit a wall

## Starting a new session checklist

Run this mentally at the start of every session:
1. `git log --oneline -20` — what was done last?
2. `cat docs/agent/PLAN.md` — what is the current task plan?
3. `cat docs/agent/SCRATCHPAD.md` — any in-progress notes?
4. `cat BLOCKERS.md` — any unresolved blockers?
5. Then proceed with the user's request or the next planned task
