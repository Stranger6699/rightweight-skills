---
name: debug-systematically
description: Use when software is broken, failing, flaky, hanging, unexpectedly slow, or otherwise behaving differently from expectations and the cause is not yet established. Use for diagnosis requests; do not treat diagnosis alone as authorization to edit files.
---

# 系统化诊断

## 核心原则

先取得根因证据，再提出修复。区分观察到的事实、可检验假设和结论；不能复现时不要用猜测填补证据空白。

## 诊断循环

1. 明确实际症状、预期行为、发生条件和最近变化。
2. 尽可能复现；记录错误、日志、状态、时序和环境差异。
3. 沿数据流或调用链定位最早出现异常的位置，而不只处理最终报错。
4. 提出一个可证伪的假设，用最小实验验证；失败就更新假设。
5. 用证据说明根因、影响范围和适当的修复方向。

对于偶发问题，检查共享状态、测试顺序、时间与随机性、异步等待、资源清理和外部依赖。避免把重复重跑成功当作修复证据。

## 授权边界

- 用户只要求“诊断”“找原因”或明确说“不改代码”时，只进行非写入调查并报告，不修改源码、测试或配置。
- 用户同时要求修复时，在根因成立后实施最小修复，并进行针对性验证。
- 为诊断而需要临时插桩或改变环境状态时，先确认这仍在用户授权范围内，并确保不会留下无关改动。

## 停止条件

能确认根因时，给出证据和修复方向。不能唯一确认时，列出已验证事实、已排除项、剩余假设和下一项最有信息量的检查；不要声称问题已解决。

