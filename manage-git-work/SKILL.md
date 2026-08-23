---
name: manage-git-work
description: Use when the user explicitly asks for Git workflow advice or actions involving branches, worktrees, commits, pull requests, merging, or cleanup, or asks to choose among those options.
---

# 管理 Git 工作

## 核心原则

区分“建议 Git 方案”和“授权执行 Git 操作”。根据隔离需求给出推荐，让用户决定后再执行。

## 开始工作前

先了解任务规模、当前工作区状态和是否需要并行工作，再推荐：

| 情况 | 通常推荐 |
|---|---|
| 小改动、当前上下文合适 | 保持当前工作区 |
| 需要独立历史但不并行 | 新分支 |
| 当前目录有其他工作，或任务需并行隔离 | 新分支 + worktree |

如果用户只要求判断而禁止 Git 操作，不运行任何 Git 命令；改用已知信息给出条件化建议。

## 完成工作后

在验证结果和改动范围清楚后，给出实际适用的选项，例如：

- 保留未提交改动
- 创建本地提交
- 创建或更新 PR
- 合并已完成分支
- 保留或清理 worktree

解释推荐及影响，等待用户选择。不要为了凑选项列出不适用或破坏性的操作。

## 授权与安全

- 实现授权不等于提交授权；提交授权不等于推送、建 PR 或合并授权。
- 未经选择不创建分支/worktree，不暂存、不提交、不推送、不合并，也不删除分支或 worktree。
- 执行前核对准确目标和工作区中的无关改动；不得夹带、覆盖或丢弃用户已有工作。
- 对删除、强制更新、重写历史等难恢复操作，必须说明影响并取得明确授权。

## 停止条件

咨询请求在给出推荐后停止。执行请求只完成用户选定的 Git 动作并报告结果，不自动进入下一个动作。

