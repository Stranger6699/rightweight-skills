## OpenCode tool mapping

| Skill action | OpenCode equivalent |
|---|---|
| Read/search files | `read`, `grep`, `glob` |
| Create/edit files | `apply_patch` |
| Run shell commands | `bash` |
| Invoke a skill | native `skill` tool |
| Track tasks | `todowrite` |
| Dispatch a subagent | `task` with `subagent_type: "general"` |
| Fetch a URL | `webfetch` |

Use the native `skill` tool to list and load skills; if it is unavailable, read
the corresponding `SKILL.md` directly.
