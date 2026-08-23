---
name: test-driven
description: Use when the user explicitly requests TDD, test-first, or red-green-refactor, or when binding project instructions require test-driven development for the requested implementation.
---

# 测试驱动开发

## 核心原则

先用失败测试定义行为，再写最小实现。只有亲眼看到测试因缺失目标行为而失败，才能证明它有能力捕获问题。

## Red-Green-Refactor

1. **RED**：写一个聚焦于可观察行为的最小测试。
2. 运行该测试，确认它失败而不是配置报错，并且失败原因正是目标行为尚未实现。
3. **GREEN**：编写使该测试通过的最小生产代码，不顺手增加功能。
4. 重新运行目标测试及必要的相关测试，确认真实通过。
5. **REFACTOR**：仅在绿色状态下清理重复和命名；重构后再次验证。
6. 对下一个独立行为重复循环。

## 严格边界

生产实现已先写出时，这不再是 TDD。若用户明确要求严格 TDD，应撤销当前任务中尚未验证的提前实现，再从失败测试开始；不要把实现留作“参考”后补测试。

探索性代码可以帮助理解未知接口，但必须明确为可丢弃实验，不能作为正式实现悄悄保留。

若目标没有可行的自动化测试入口，或项目约束与 TDD 冲突，说明具体障碍并与用户决定替代验证方式，不要假装遵循了 TDD。

## 范围与停止

TDD 只约束当前已授权的实现，不自动要求设计文档、详细计划、正式审查、子 Agent、分支、worktree 或提交。相关行为通过测试且必要回归检查通过后停止，并报告实际的红绿证据。

