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

所有已安装的 Skill 都会被 Codex 发现；调用策略只决定它们能否在未点名时被隐式调用：

- **仅显式**：`allow_implicit_invocation: false`，需要通过 `$skill-name` 或 Skill 选择器调用。
- **自动**：允许隐式调用，`description` 覆盖常见的直接触发场景。
- **精准自动**：同样允许隐式调用，但 `description` 主动排除普通局部任务，只匹配更明确的风险或流程需求。

套件没有必须先运行的总入口，也没有 Skill 会仅因传统顺序而强制启动下一项流程。

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

每个目录都是独立 Skill，可以只安装其中一部分。将完整的 Skill 目录复制或链接到以下任一位置：

| 范围 | Windows 路径 | 用途 |
|---|---|---|
| 个人 | `%USERPROFILE%\.agents\skills\` | 在该用户的所有项目中使用 |
| 仓库 | `<仓库根目录>\.agents\skills\` | 随仓库共享，只在该仓库中使用 |

例如，安装后应存在如下文件：

```text
%USERPROFILE%\.agents\skills\implement-change\SKILL.md
```

`SKILL.md` 是发现 Skill 所需的入口；`agents/openai.yaml` 是可选的界面与调用策略元数据。Codex 通常会自动检测新增或更新的 Skill；若没有出现，请重启 Codex。完整位置和元数据规则见 [OpenAI 的 Build skills 文档](https://developers.openai.com/codex/skills/)。

## 开发环境

项目级静态校验需要 Python 和 `requirements-dev.txt` 中的依赖；GitHub Actions 当前以 Python 3.12 为基准。行为评测还需要：

- Git，且支持 `git init -b`
- 已安装并可从 `PATH` 调用的 Codex CLI
- 支持 `--ephemeral`、`--ignore-user-config` 和 `--sandbox` 的 Codex CLI 版本
- 可用的本地 Codex 认证或 `OPENAI_API_KEY`

运行行为评测前可用 `python --version`、`git --version` 和 `codex --version` 记录实际环境；比较修改前后结果时应保持这些版本一致。

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

运行器会创建临时 Git 仓库，将当前 Skills 安装到仓库级 `.agents/skills/`，并使用一次性 `HOME` 和 `CODEX_HOME` 启动 `codex exec --json`。它不加载个人配置或个人 Skills；使用本地 Codex 认证时，会把 `auth.json` 临时复制到一次性 `CODEX_HOME`，并在正常退出路径中删除整个临时环境。

`auth.json` 包含敏感凭据。只对已经审查、可信的 Skill revision 运行真实行为评测，不要用个人认证直接执行来源不明的分支或补丁。`--keep-workdir` 只让运行器复制 fixture 工作区，不会主动复制临时认证目录；但被评测内容仍可能把敏感数据写入工作区或工具输出，因此共享 `.artifacts` 前必须检查其内容。

每个已启动的场景都会在 `.artifacts/behavior/` 中生成 verdict，状态为 `pass`、`fail` 或 `indeterminate`。模型、Skills Git revision、未提交状态、Skill 内容 SHA-256 指纹和重复序号会写入 verdict；找到 Codex CLI 后还会记录其版本。`codex exec` 返回后会保存 `trace.jsonl` 和 `stderr.log`，但认证缺失、找不到可执行文件、场景初始化失败或超时等提前结束路径可能只有 verdict。

- `pass`：Codex 正常完成，并且所有确定性检查通过。
- `fail`：运行有效，但至少一个行为检查失败。
- `indeterminate`：认证、超时、空轨迹、fixture 或检查器故障，不能据此判断 Skill 行为。

真实行为评测会使用模型额度且需要本地认证，因此默认只手动或在可信的定时环境运行，不进入公共 CI。修改行为塑造文本时，应固定 Codex CLI、模型和场景，对修改前后各运行至少 3 次；概率性或压力场景建议至少 5 次，并人工阅读异常轨迹。

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 开源许可证。

