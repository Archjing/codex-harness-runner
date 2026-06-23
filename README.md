[![English](https://img.shields.io/badge/README-English-blue)](README.en.md) [![快速上手](https://img.shields.io/badge/%E5%BF%AB%E9%80%9F%E4%B8%8A%E6%89%8B-%E4%B8%AD%E6%96%87-green)](docs/快速上手.md)

# Codex Harness Runner 中文说明

这是一个基于 OpenAI Agents SDK 的本地 runner。它会把 Codex CLI 作为一个 stdio MCP server 进程启动，然后让多角色 agent 通过该 MCP server 暴露的 `codex` 与 `codex-reply` tools，对真实项目目录执行只读检查、规划、实现和验证。

Description: Harness engineering runner for project-scoped multi-agent workflows. Uses Codex CLI as a stdio MCP server execution channel.

中文描述：面向项目级多智能体工作流的 Harness Engineering runner，使用 Codex CLI stdio MCP server 作为代码仓库执行通道。

## 术语

- `MCP`：Model Context Protocol。
- `Codex CLI MCP server`：本地通过 `codex mcp-server` 启动的进程。
- `codex` / `codex-reply`：上面这个 MCP server 暴露给 Agents SDK 使用的 tools。

## 这个仓库做什么

- 启动 `codex mcp-server`
- 用 `MCPServerStdio` 连接它
- 为多角色 agent 暴露 `codex` / `codex-reply`
- 提供基于 profile 的 Harness Team Lead、Context Curator、Planner、Codex Implementer、Reviewer、Verifier、Memory Steward
- 支持 `--profile`、`--mode` 和本地 JSON run log

## 运行要求

- Python 3.12+
- `uv` 可用，并且在 Codex Desktop/CLI 启动环境的 `PATH` 中
- `PATH` 中可用的 Codex CLI
- 当前运行用户下已有可用的 Codex CLI 登录/配置
- `.env` 中至少有 `OPENAI_API_KEY`
- 如果走兼容网关，还需要 `OPENAI_BASE_URL`，并且要包含 `/v1`
- 至少创建一个本地 `profiles/*.toml`，从 `profiles/example.toml` 复制

当前 profile 的 `cwd` 必须位于 `CODEX_HARNESS_WORKSPACE_ROOT` 之下；默认值是当前用户的 home 目录。

## 容器化状态

当前不提供 Docker image。

原因不是“不能做”，而是“不值得现在做”：

- 这个 runner 依赖本地 Codex CLI、`~/.codex`、`.env`、本地 profiles 和目标 workspace 挂载。
- 第一轮 Docker 尝试中，仅 Debian 的 `nodejs` / `npm` 依赖体积就已经很重，再加 Python 依赖和 Codex CLI，镜像大概率超过 500 MB。
- 当前阈值是：如果最终镜像无法稳定低于 500 MB，就不继续推进。

因此现阶段优先本地运行。只有当后续能通过更轻的 base、预编译 Codex CLI 或更窄的运行时边界把镜像压到阈值内，才再重启容器化。

## 初始化

先用 `uv` 同步项目依赖：

```bash
uv sync
```

`uv` 必须在 Codex Desktop/CLI 启动环境的 `PATH` 中，因为 bundled MCP server 使用 `uv run python -m codex_harness.plugin_mcp` 启动。

然后准备本仓库环境变量：

```bash
cp .env.example .env
```

常见环境变量：

```bash
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://your-base-url/v1
CODEX_MCP_CWD=/path/to/your/workspace
CODEX_MCP_MODEL=gpt-5.4
CODEX_MCP_SANDBOX=workspace-write
CODEX_MCP_APPROVAL_POLICY=never
CODEX_MCP_TIMEOUT_SECONDS=360000
CODEX_HARNESS_WORKSPACE_ROOT=/path/to/your/workspace
```

这些 `CODEX_MCP_*` 变量不是启动一个全局 MCP server 的系统配置，而是这个 runner 在调用 `codex` tool 时传入的默认参数。

## Profiles

先从模板创建：

```bash
cp profiles/example.toml profiles/workspace.toml
```

常见 profile 名称：

- `workspace`
- `app`
- `docs`
- `research`

profile 用来定义：

- `cwd`
- `model`
- `sandbox`
- `approval_policy`
- `rules`
- `verify_doc`
- `verify_code`
- `memory_targets`
- `agent_models.<role>`

这些本地 profile 默认不提交到 Git。

## 在 Codex / Claude Code 等 Agent 工具中使用

快速上手：[docs/快速上手.md](docs/快速上手.md)

## Plugin 安装

这个仓库本身也是一个 Codex plugin，包含：

- `codex-harness-runner` skill
- bundled stdio MCP server
- `list_profiles`
- `run_harness_plan`
- `run_harness_review`
- `run_harness_implement`
- `run_harness_full`

先确认 `uv` 在 Codex Desktop/CLI 启动环境的 `PATH` 中，然后直接从 GitHub marketplace 安装 plugin：

```bash
export PATH="$HOME/.local/bin:$PATH"
codex plugin marketplace add Archjing/codex-harness-runner --sparse .agents/plugins
codex plugin add codex-harness-runner@codex-harness-runner
```

安装后需要新开 Codex thread 或重启 Codex Desktop/CLI，新的 skill 和 MCP tools 才会被加载。

如果要本地运行 harness workflow，再 clone 仓库并执行 `uv sync`、配置 `.env` 和本地 profile。

## Smoke Test

最小可用性验证：

```bash
python3 smoke_test.py
```

期望输出至少包含：

```text
codex_mcp_server=ready
profile=workspace
tools=codex,codex-reply
```

这只说明：

- Codex CLI MCP server 可以启动
- Agents SDK client 能列出 tools

它不代表完整多 agent 流程已经验证通过。

## 运行方式

例子：

```bash
python3 main.py --profile workspace --mode plan --save-run-log \
  "只读总结当前 profile 的规则文件和验证命令，不要改文件。"
```

模式说明：

- `plan`：只规划，不改文件
- `review`：只读审查/验证
- `implement`：允许在 profile `cwd` 内做实现
- `full`：规划、实现、验证、给出记忆更新建议

如果指定 `--save-run-log`，会把结构化 run summary 写到 `runs/*.json`。

## 核心实现边界

当前设计重点是“本地 project harness”，不是“全局 Codex 递归代理”。

所以要点是：

- 不把这个 runner 启动的 Codex CLI MCP server 再注册成当前 Codex Desktop 会话自己的全局 MCP server
- 不把 secrets、profiles、workspace 状态打进镜像
- 不把一次 smoke test 误当成完整工作流验证

这个仓库更像一个可编排的本地执行入口，而不是一个独立 SaaS 服务。
