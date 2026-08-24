# Rightweight Skills

Rightweight 是一套面向编码 Agent 的可组合软件开发 Skills。它为当前任务采用最低充分流程，只在关键歧义或具体风险需要时升级。

> Use the right amount of process for the work at hand.

## 原则

- 简单明确的任务直接实施并做局部验证。
- 能从仓库查明的信息由 Agent 自行调查。
- 风险和歧义增加时，只添加解决当前问题所需的步骤。
- 用户可以指定“直接做”“先设计”“按 TDD”“不要改代码”等工作方式。
- 设计、计划、TDD、审查和 Git 隔离不是所有任务的固定流水线。
- 未经当前证据验证，不声称工作已经完成或修复。
- 分支、worktree、提交和 PR 可以推荐，但由用户决定是否执行。

## Skills

| Skill | 调用策略 | 用途 |
|---|---|---|
| `choose-workflow` | 仅显式 | 用户需要判断任务应采用何种流程 |
| `shape-solution` | 精准自动 | 关键歧义、架构取舍或高风险设计 |
| `write-plan` | 精准自动 | 已明确的复杂工作需要排序和检查点 |
| `implement-change` | 自动 | 实施已授权的软件修改 |
| `debug-systematically` | 自动 | 在原因未知时诊断错误、偶发失败或性能问题 |
| `test-driven` | 仅显式 | 用户或项目明确要求严格 TDD |
| `review-changes` | 精准自动 | 用户明确要求审查改动 |
| `handle-review` | 自动 | 核实并处理具体审查意见 |
| `verify-result` | 自动 | 在声称完成、修复或通过之前取得证据 |
| `manage-git-work` | 仅显式 | 推荐或执行用户选择的 Git 工作流 |

“精准自动”表示保留自动发现，但 `description` 明确排除普通局部任务。套件没有必须先运行的总入口，也没有 Skill 会仅因传统顺序而强制启动下一项流程。

## 典型组合

```text
简单明确、低风险
implement-change -> 局部验证

原因未知的故障
debug-systematically -> （若已授权修复）实施 -> verify-result

复杂或高风险变更
shape-solution -> 用户确认 -> write-plan -> implement-change
-> 可选 review-changes -> verify-result -> 可选 manage-git-work

用户明确覆盖
直接做 / 先设计 / 按 TDD / 只审查 / 做完让我决定是否提交
```

箭头表示常见组合，不表示强制调用链。

## 安装到 Codex

将需要的 Skill 目录复制或链接到 Codex 的个人 Skills 目录。Windows 默认位置通常为：

```text
%USERPROFILE%\.codex\skills\
```

每个目录都是独立 Skill，可以只安装其中一部分。重新打开任务后，Codex 会根据 `SKILL.md` 和 `agents/openai.yaml` 发现它们。

## 验证

安装开发依赖并运行项目级静态校验：

```powershell
python -m pip install -r requirements-dev.txt
python -X utf8 scripts/validate_skills.py
```

该命令检查全部 Skill 的 frontmatter、目录命名、`agents/openai.yaml`、README 清单、Markdown 链接和行为场景 schema。安装了 Codex `skill-creator` 时，还可以叠加官方校验器：

```powershell
python -X utf8 scripts/validate_skills.py --official
```

`--official` 使用 UTF-8 模式调用 `quick_validate.py`，避免中文 Windows 的默认 GBK 解码问题。[GitHub Actions 工作流](.github/workflows/validate.yml) 会在 GitHub 镜像的每次推送和 PR 中运行静态校验；当前 Gitee 远端可在流水线中执行相同命令。静态 CI 不调用模型。

## 行为评测

人工可读的覆盖目标见 [`tests/behavior-scenarios.md`](tests/behavior-scenarios.md)，可执行场景定义见 [`tests/behavior/scenarios.json`](tests/behavior/scenarios.json)。列出或运行场景：

```powershell
python -X utf8 tests/behavior/run.py --list
python -X utf8 tests/behavior/run.py --scenario diagnose-without-editing
python -X utf8 tests/behavior/run.py --all
python -X utf8 tests/behavior/run.py --all --model <模型 ID> --repeat 3
```

运行器会创建临时 Git 仓库，将当前 Skills 安装到仓库级 `.agents/skills/`，并使用一次性 `HOME` 和 `CODEX_HOME` 启动 `codex exec --json`。它只临时复制 `auth.json`，不加载个人配置或个人 Skills；运行结束后始终删除临时认证环境。需要检查最终 fixture 时使用 `--keep-workdir`，该选项只把工作区复制到 `.artifacts`，不会保留认证文件。

每项评测生成 `pass`、`fail` 或 `indeterminate`，完整轨迹和 verdict 保存在 `.artifacts/behavior/`。Verdict 同时记录 Codex CLI 版本、模型、Skills Git revision、未提交状态、Skill 内容 SHA-256 指纹和重复序号：

- `pass`：Codex 正常完成，并且所有确定性检查通过。
- `fail`：运行有效，但至少一个行为检查失败。
- `indeterminate`：认证、超时、空轨迹、fixture 或检查器故障，不能据此判断 Skill 行为。

真实行为评测会使用模型额度且需要本地认证，因此默认只手动或在可信的定时环境运行，不进入公共 CI。修改行为塑造文本时，应固定 Codex CLI、模型和场景，对修改前后各运行至少 3 次；概率性或压力场景建议至少 5 次，并人工阅读异常轨迹。

