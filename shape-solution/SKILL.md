---
name: shape-solution
description: Use when a software change has consequential requirement ambiguity, architectural trade-offs, cross-module contracts, elevated security or data risk, or when the user explicitly asks to design before implementation. Do not use for clear, localized changes.
---

# 塑造解决方案

## 核心原则

只消除会改变方案或风险的未知项。能从仓库、文档和现有约定查明的信息先自行调查；不要把调查工作转交给用户。

## 工作方式

1. 读取相关代码、文档和项目约束，划定影响范围。
2. 区分可调查事实、合理默认值和必须由用户决定的关键选择。
3. 必要时一次询问一个关键问题。避免为了完整感而盘问。
4. 当存在真实取舍时，给出可行方案、影响和推荐；不强制凑出固定数量的方案。
5. 形成足以指导下一步工作的设计，覆盖相关边界、数据流、错误处理、迁移和验证策略。

设计深度随风险变化。普通功能可用几段对话说明；安全边界、公共接口或不可逆迁移需要更明确的设计与回退策略。

## 用户控制

- 用户要求“只设计”时，不修改实现文件。
- 用户同时授权实施时，只有关键决策仍未确认或风险显著时才暂停等待确认。
- 默认在对话中交付。只有用户要求或复杂任务明确受益时才建议保存到 `docs/`；未经选择不创建或提交文档。
- 不自动创建计划、分支、worktree、提交或 PR。

## 停止条件

当关键选择、边界、风险和成功标准已经足以支持下一步工作时停止。不要仅因传统流程顺序而自动调用计划或实现 Skill；只有原请求已授权继续时才继续。

