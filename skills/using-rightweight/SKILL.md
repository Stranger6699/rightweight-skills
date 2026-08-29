---
name: using-rightweight
description: Use when starting a conversation or before taking an action to discover and apply any relevant Rightweight skill.
---

<RIGHTWEIGHT-BOOTSTRAP>
Rightweight Skills are available in this workspace. Before taking any action — including asking a clarifying question, reading files, or changing code — check whether a Rightweight skill applies.

Use the smallest sufficient workflow. Explicit user instructions take precedence over skills. An implicit match does not authorize edits, Git operations, or external side effects that the user did not request.

When a skill applies, load its complete `SKILL.md` using the harness-native skill mechanism. If no native skill mechanism exists, read the relevant file directly from this package's installed skill directory. Follow the skill's scope, authorization boundary, and stopping condition. Do not invoke this bootstrap again once it is loaded.

The Skill bodies are harness-agnostic: they describe actions, not vendor-specific tool names. Use the tool mapping supplied by the current harness adapter for file access, shell commands, task tracking, and optional subagents.
</RIGHTWEIGHT-BOOTSTRAP>
