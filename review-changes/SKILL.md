---
name: review-changes
description: Use when the user asks to review, inspect, audit, or assess software changes, a branch, pull request, patch, or work in progress, or explicitly requests an independent check of high-risk changes. Do not use merely because ordinary implementation finished.
---

# 审查变更

## 核心原则

审查的首要产物是可执行的缺陷发现，而不是改动摘要或风格偏好。默认只报告，不修改。

## 工作方式

1. 确认审查基准、范围和原始需求；若上下文可从仓库取得，先自行读取。
2. 阅读完整差异及必要的调用方、测试和契约，不孤立评论单行代码。
3. 优先检查行为错误、回归、安全、数据损坏、兼容性和缺失测试。
4. 只报告开发者会据此采取行动的问题，按严重度排序，并给出精确位置、触发条件和影响。
5. 没有发现时明确说明，并列出未覆盖的测试或残余风险。

测试和静态检查可以作为审查证据，但未经用户授权不要使用会重写文件的自动修复或格式化命令。

## 边界

- 用户说“不要修改”时保持只读。
- 不把个人偏好、无关重构或没有具体影响的猜测包装成缺陷。
- 不因为审查完成而自动修复发现、创建提交或发起 PR。
- 用户要求修复发现项时，先确认其技术成立并在授权范围内实施。

## 输出

发现优先，按严重度排列，并附文件与行号。随后再写必要的假设、测试缺口和简短总结。若没有问题，直接说没有发现问题。

