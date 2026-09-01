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
| `using-rightweight` | 自动 | 会话启动时发现并加载适用 Skill |
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

## 跨 Agent 适配

本仓库采用与 Superpowers 相同的三层适配模型：

1. `skills/*/SKILL.md` 是共享且不依赖工具名称的行为规范。
2. `skills/using-rightweight/references/*-tools.md` 将“读文件、编辑、运行命令、调用 Skill”等动作映射到具体 Agent 的工具。
3. 各运行器的安装入口在会话开始注入 `using-rightweight` bootstrap，使 Skill 能自动触发。

不要为不同 Agent 复制或改写 Skill 正文；新增运行器时只增加适配层，并通过该运行器自己的插件/扩展安装机制分发。

| Agent | 适配入口 | 会话启动方式 |
|---|---|---|
| Codex App / CLI | `.codex-plugin/plugin.json` | 原生 Skill 发现，`using-rightweight` 自动触发 |
| Claude Code | `.claude-plugin/plugin.json` + `hooks/` | `SessionStart` hook |
| Cursor | `.cursor-plugin/plugin.json` + `hooks/` | `sessionStart` hook |
| Gemini CLI | `gemini-extension.json` + `GEMINI.md` | 扩展声明的 context file |
| GitHub Copilot CLI | `.claude-plugin/plugin.json` + `hooks/` | SDK `additionalContext` hook |
| OpenCode | `package.json` + `.opencode/plugins/rightweight.js` | 消息 transform 注入 |
| Pi | `package.json` + `.pi/extensions/rightweight.ts` | `session_start` / `context` 注入 |

各 Agent 的精确工具名以运行时暴露的工具列表为准；缺少可选能力时，Skill 中的降级路径（例如计划文件或当前会话内执行）仍然适用。

新增运行器的完整清单见 [`docs/porting-to-new-harness.md`](docs/porting-to-new-harness.md)。

## 安装到 Codex

`skills/` 下的每个目录都是独立 Skill，可以只安装其中一部分。将完整仓库作为插件安装，或将需要的 Skill 目录复制/链接到以下任一位置：

| 范围 | Windows 路径 | 用途 |
|---|---|---|
| 个人 | `%USERPROFILE%\.agents\skills\` | 在该用户的所有项目中使用 |
| 仓库 | `<仓库根目录>\.agents\skills\` | 随仓库共享，只在该仓库中使用 |

例如，手动安装后应存在如下文件：

```text
%USERPROFILE%\.agents\skills\implement-change\SKILL.md
```

`SKILL.md` 是发现 Skill 所需的入口；`agents/openai.yaml` 是可选的界面与调用策略元数据。Codex 通常会自动检测新增或更新的 Skill；若没有出现，请重启 Codex。完整位置和元数据规则见 [OpenAI 的 Build skills 文档](https://developers.openai.com/codex/skills/)。

### 其他运行器

- Claude Code：从包含本仓库的插件目录安装，插件会自动发现 `SKILL.md` 并运行 `SessionStart` hook。
- Cursor：通过插件市场安装，或将仓库作为本地插件加载；`hooks-cursor.json` 负责启动注入。
- Gemini CLI：`gemini extensions install <仓库地址>`，扩展会加载仓库内的 `GEMINI.md`。
- GitHub Copilot CLI：使用兼容的插件市场安装；启动 hook 会输出 SDK 标准的 `additionalContext`。
- OpenCode：将仓库作为包加载（`package.json` 的 `main` 指向插件），无需修改用户配置文件。
- Pi：`pi install git:<仓库地址>`；扩展会注册 Skill 路径，并在新会话和压缩后重新注入 bootstrap。

安装后用一个全新会话发送“帮我实现一个功能”，确认 Agent 在第一次文件操作前先检查并加载适用 Skill。若要验证具体运行器的自动触发，应记录完整会话轨迹，而不只检查文件是否存在。

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

## 第三方署名与许可证

部分运行器适配基础设施参考并改编自 [obra/superpowers](https://github.com/obra/superpowers)，版权归 Jesse Vincent 所有，并按原项目 MIT License 保留第三方声明。涉及文件和完整许可证文本见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

Rightweight Skills 自身的 Skill 内容、文档、测试和原创代码采用 MIT License；第三方改编部分保留 Superpowers 原项目的版权声明和 MIT 条款。

## 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

