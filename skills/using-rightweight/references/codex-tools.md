## Codex tool mapping

Rightweight skills describe actions rather than tool names. On Codex, use the
native tools exposed by the current session:

| Action | Codex equivalent |
|---|---|
| Read/search files | `exec_command` with `rg`, `Get-Content`, or equivalent |
| Create/edit files | `apply_patch` (or the native file-edit tool) |
| Run commands | `exec_command` |
| Invoke a skill | Native skill discovery/invocation; otherwise read its `SKILL.md` |
| Track a multi-step task | `update_plan` |
| Dispatch an agent | `spawn_agent`/`followup_task` when multi-agent support is enabled |

If a native capability is unavailable, use the fallback stated by the skill.
Never invent a tool call or silently broaden the user's authorization.
