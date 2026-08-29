---
name: write-plan
description: Use when a software change is already understood but needs sequencing across dependent stages, coordinated modules, migration steps, or explicit implementation checkpoints, or when the user asks for an implementation plan. Do not use for simple work or unresolved product decisions.
---

# 编写实施计划

## 核心原则

计划应降低执行风险，而不是复述需求。粒度以可验证成果和依赖关系为准，不强制拆成固定时长的小步骤。

## 工作方式

1. 确认目标、约束和关键决策已经足够明确。若产品或架构选择尚未解决，指出缺口并停止，不用计划掩盖歧义。
2. 读取相关项目结构、约定和测试方式。
3. 按依赖顺序拆分工作；每一步产生可检查的成果。
4. 标注相关文件或模块、验证方法、关键风险，以及必要时的迁移或回退措施。
5. 明确完成标准。只在并行任务彼此独立且平台支持时建议并行。

简单任务只需几步；复杂任务可以更详细。不要为了形式加入逐步提交、TDD、审查或 worktree，除非用户要求或具体风险需要。

## 交付与停止

默认把计划写在对话中。用户说“不要保存文件”时不得创建计划文件；只有用户要求或任务明确受益时才建议保存。

只写计划的请求在交付后停止，不修改实现。若原请求明确要求“计划后直接执行”，才可继续；否则不得自动启动实现、Git 操作或其他工作流。

