## Cursor tool mapping

| Skill action | Cursor Agent equivalent |
|---|---|
| Read/search files | `read_file`, `grep`, `glob` (or the tools shown by the session) |
| Create/edit files | `write`, `edit`, `apply_patch` |
| Run shell commands | `run_terminal_cmd` |
| Invoke a skill | Load the relevant `SKILL.md` from the installed skills directory |
| Track tasks | `TodoWrite`/plan UI when available; otherwise a plan response |
| Dispatch a subagent | Cursor's task/subagent tool when enabled |

Trust the exact tool names exposed by the current Cursor version over this
reference. Missing optional tools are degradable; do not invent calls.
