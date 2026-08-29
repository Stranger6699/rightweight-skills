---
name: implement-change
description: Use when the user asks to add, change, fix, or refactor software and authorizes code or project-file edits. Do not use when the user only wants explanation, diagnosis, design, planning, review, or status.
---

# 实施变更

## 核心原则

使用满足任务的最小流程，在用户授权范围内完成修改，并按风险提供足够证据。清晰的局部任务应直接完成，不需要仪式性的设计、计划或批准。

## 工作方式

1. 读取相关代码、测试和项目约定；保护工作区中与任务无关的现有改动。
2. 能从仓库查明的信息自行调查。只有不同答案会显著改变结果或风险时才询问用户。
3. 在最小相关范围内修改，沿用现有模式，避免顺手重构和范围扩张。
4. 运行与影响面相称的检查，并阅读真实结果。
5. 简洁汇报改动、验证证据以及任何未验证风险。

## 流程升级

不要自动要求设计、计划、TDD、正式审查、文档、分支或 worktree。只有公共契约、安全/支付/重要数据、不可逆迁移、跨模块架构或关键需求歧义等具体风险才值得暂停或建议升级。

用户说“直接做”时优先执行；这不允许跳过破坏性操作确认、授权边界或诚实验证。用户明确要求 TDD 时，必须先写并观察目标测试失败。

## 停止条件

完成请求范围内的修改和最低充分验证后停止。不要自动创建提交或 PR。若验证受限或失败，如实说明，不得用“应该修好”代替证据。

