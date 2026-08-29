## Claude Code tool mapping

| Skill action | Claude Code equivalent |
|---|---|
| Read/search files | `Read`, `Grep`, `Glob` |
| Create/edit files | `Write`, `Edit` |
| Run shell commands | `Bash` |
| Invoke a skill | `Skill` |
| Track tasks | `TodoWrite` |
| Dispatch a subagent | `Task` (when available) |

When a listed tool is unavailable, use the closest built-in fallback and state
the limitation instead of inventing a call.
