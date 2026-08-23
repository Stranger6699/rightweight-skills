---
name: handle-review
description: Use when the user provides concrete code-review feedback, requested changes, or reviewer comments and asks to evaluate, respond to, or implement them. Do not use for general product feedback or new requirements unrelated to a review.
---

# 处理审查反馈

## 核心原则

审查意见是需要验证的技术主张，不是自动执行的命令。先判断它是否适用于当前代码，再做与证据相称的处理。

## 工作方式

1. 逐条解析反馈对应的代码、预期行为和声称的风险。
2. 阅读当前实现、调用方、测试和约束；必要时复现问题。
3. 将反馈区分为：真实缺陷、合理改进、基于错误假设的意见、已过期意见或新的范围要求。
4. 对已授权且技术成立的事项实施最小充分修改，并进行针对性验证。
5. 对不成立或范围过大的意见，用证据解释，并提出更合适的处理方式。

## 边界

- 不为表示配合而盲目同意或全面重写。
- “处理反馈”可以授权合理的局部修复，但若核实后需要破坏兼容、架构重写或明显扩展范围，先说明取舍并取得用户决定。
- 反馈含义不清且不同理解会改变结果时才提问；能从仓库查明的先调查。
- 不自动提交、推送、回复外部评论或创建 PR。

## 输出与停止

说明每条反馈的判断、证据、已做修改和验证结果。若用户只要求核实，则在给出结论后停止，不修改代码。超出授权的剩余事项作为选项提出，不自行继续。

