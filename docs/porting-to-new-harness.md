# 为新的 Agent 运行器增加适配

Rightweight 的适配遵循三个不变量：

1. 顶层 Skill 正文只描述行为和动作，不写厂商工具名。
2. `skills/using-rightweight/references/<harness>-tools.md` 负责把动作映射到该运行器的真实工具。
3. 安装包必须在每次会话开始自动加载 `skills/using-rightweight/SKILL.md`；不能要求用户每次粘贴提示词，也不能修改用户的全局配置文件。

## 选择注入形状

- 运行器能在会话开始执行命令并读取 JSON：复制 `hooks/` 的 shell-hook 形状。
- 运行器提供 JS/TS 插件生命周期：复制 `.opencode/` 或 `.pi/` 的消息注入形状。
- 运行器只加载扩展自带的 instructions/context 文件：复制 `gemini-extension.json` + `GEMINI.md` 的形状。

Skill 发现和 bootstrap 注入可以使用不同入口，但两者都必须通过运行器自己的安装机制交付。缺少可选的子 Agent 或待办工具时，映射文件应指向 Skill 中的降级路径，而不是虚构工具调用。

## 验收标准

在干净会话中发送：

> Let's make a react todo list

模型应在第一次写代码前加载 `using-rightweight`，然后选择合适的工作流。适配提交应保存完整会话轨迹，并至少覆盖一次静态入口测试和一次实际运行器的启动注入测试。若运行器没有可验证的自动注入能力，应明确标记为不支持，而不是提供需要手动 opt-in 的“半适配”。

## 实现清单

1. 新增工具映射文件并记录缺失能力的降级行为。
2. 新增运行器自己的 manifest/extension/plugin 入口。
3. 在会话启动或第一条用户消息前注入 bootstrap，避免重复注入。
4. 更新 README 的支持矩阵和安装方式。
5. 扩展 `tests/test_adapters.py`，运行 `scripts/validate_skills.py` 与单元测试。
