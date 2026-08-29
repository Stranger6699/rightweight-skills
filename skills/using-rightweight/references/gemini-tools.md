## Gemini CLI tool mapping

| Skill action | Gemini CLI equivalent |
|---|---|
| Read a file | `read_file` |
| Read multiple files | `read_many_files` |
| Create a file | `write_file` |
| Edit a file | `replace` |
| Run shell commands | `run_shell_command` |
| Search/find files | `grep_search`, `glob`, `list_directory` |
| Fetch/search web | `web_fetch`, `google_web_search` |
| Invoke a skill | `activate_skill`, or read its `SKILL.md` |
| Track tasks | `write_todos` |
| Dispatch a subagent | `invoke_agent` with `agent_name: "generalist"` |

If a tool is not enabled, use the fallback described by the skill (for
example, a plan file instead of a todo tool).
