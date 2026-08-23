---
name: verify-result
description: Use before claiming that software work is complete, fixed, passing, built, or ready when that claim depends on current executable evidence. Do not use for pure discussion, explanation, design, or planning.
---

# 验证结果

## 核心原则

证据先于完成声明。验证力度与影响和风险相称，不等于每次都运行完整测试套件。

## 验证方法

1. 明确即将声称什么，例如缺陷已修复、测试通过或构建成功。
2. 为每项声明选择最低充分证据，并运行最新检查。
3. 阅读退出状态和完整的关键输出；不要根据旧结果、代码外观或预期推断成功。
4. 只报告证据支持的结论，并说明未覆盖的风险。

| 风险 | 典型证据 |
|---|---|
| 轻量 | 目标测试、静态检查、构建局部或直接行为确认 |
| 标准 | 相关测试集，加类型检查或构建 |
| 严谨 | 完整相关测试、构建、迁移/安全检查和必要人工验证 |

改动只有一行不代表无需验证；测试很慢只意味着应先选择更窄但有意义的检查。

## 失败与限制

验证失败时不要改写成成功。若修复仍在原任务授权内，可继续定位和处理；否则报告失败及下一步。

若环境、依赖或时间限制使验证无法完成，明确区分“已修改”“静态检查正常”和“运行时已验证”。不得说“应该没问题”“看起来修好了”来替代证据。

