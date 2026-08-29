# OpenCode 安装

将本仓库作为 OpenCode 包加载。`package.json` 会注册 `.opencode/plugins/rightweight.js`，插件会把 `skills/` 注册为 Skill 路径，并在首条用户消息前注入 bootstrap。

安装完成后开启一个新会话，确认模型能识别 Rightweight，并在适用时通过 native `skill` 工具加载具体 Skill。插件不会修改用户的 OpenCode 配置文件。
