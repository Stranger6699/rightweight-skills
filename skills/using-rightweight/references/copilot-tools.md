## GitHub Copilot CLI tool mapping

| Skill action | Copilot CLI equivalent |
|---|---|
| Read/search files | `view`, `grep`, `glob` (or the tools exposed by the session) |
| Create/edit files | `edit` / patch tool |
| Run shell commands | `execute` / shell tool |
| Invoke a skill | Load the relevant `SKILL.md` from the installed plugin |
| Track tasks | plan/todo tool when enabled; otherwise track in the response |
| Dispatch a subagent | task tool when enabled |

Use the exact names reported by the current Copilot CLI session. Optional
capabilities should degrade to the documented inline or file-based fallback.
