# Codex Harness Runner with Codex CLI MCP

This project configures Codex CLI as a long-running MCP server for an OpenAI Agents SDK harness team.

## What it does

- Starts `codex mcp-server`
- Connects to it with `MCPServerStdio`
- Exposes the `codex` and `codex-reply` tools to repository-capable agents
- Builds a profile-driven Harness Team Lead with Context Curator, Planner, Codex Implementer, Reviewer, Verifier, and Memory Steward specialists
- Supports `--profile`, `--mode`, and optional local JSON run summaries
- Uses long MCP timeouts suitable for real Codex work
- Keeps OpenAI API orchestration config in `.env`

## Setup

```bash
git clone https://github.com/openai/openai-agents-python.git /home/zj/workspace/openai-agents-python
cd /home/zj/workspace/openai-agents-python
python3 -m pip install --user --break-system-packages -e .
```

Then configure the runner:

```bash
cd /home/zj/workspace/codex-harness-runner
cp .env.example .env
```

Put your API key into `.env`.

If you need a custom API gateway or compatible endpoint, also set:

```bash
OPENAI_BASE_URL=https://your-base-url/v1
```

Optional Codex MCP defaults:

```bash
CODEX_MCP_MODEL=gpt-5.4
CODEX_MCP_SANDBOX=workspace-write
CODEX_MCP_APPROVAL_POLICY=never
CODEX_MCP_TIMEOUT_SECONDS=360000
```

Project/workspace defaults now live in `profiles/*.toml`.

## Smoke test

This verifies that Codex CLI starts as an MCP server and exposes tools. It does not run a full model workflow.

```bash
cd /home/zj/workspace/codex-harness-runner
python3 smoke_test.py
```

Expected output includes:

```text
codex_mcp_server=ready
profile=workspace
tools=codex,codex-reply
```

## Profiles

Available initial profiles:

- `workspace`: `/home/zj/workspace`
- `brainstorm`: `/home/zj/workspace/brainstorm`
- `stok-mapping`: `/home/zj/workspace/stok-mapping`
- `my_first_podcast`: `/home/zj/workspace/my_first_podcast`

Each profile defines cwd, model, sandbox, approval policy, rule files, verification commands, and memory targets.
Profiles can also route specific roles to a different OpenAI-compatible provider without storing secrets:

```toml
[agent_models.context_curator]
kind = "openai_chat"
base_url_env = "DEEPSEEK_BASE_URL"
api_key_env = "DEEPSEEK_API_KEY"
model = "deepseek-v4-flash"
```

Keep the actual `DEEPSEEK_API_KEY` in `.env`, not in profile files.
GPT-style model settings can also be declared per role:

```toml
[agent_models.team_lead]
kind = "default"
model = "gpt-5.5"
reasoning_effort = "high"
verbosity = "low"
```

Provider-specific body fields can be passed with `extra_body`. For DeepSeek thinking:

```toml
[agent_models.verifier]
kind = "openai_chat"
base_url_env = "DEEPSEEK_BASE_URL"
api_key_env = "DEEPSEEK_API_KEY"
model = "deepseek-v4-pro"
reasoning_effort = "high"
extra_body = { thinking = { type = "enabled" } }
```

## Run the Harness team

```bash
cd /home/zj/workspace/codex-harness-runner
python3 main.py --profile workspace --mode plan --save-run-log \
  "只读总结当前 profile 的规则文件和验证命令，不要改文件。"
```

Modes:

- `plan`: plan only; no implementation.
- `review`: read-only review/verification.
- `implement`: implementation allowed within the profile cwd.
- `full`: plan, implement, verify, and suggest memory updates.

Run logs are written to `runs/*.json` when `--save-run-log` is set.
The run summary records structured `verification_status`, `verification_evidence`,
`verification_commands`, `files_changed`, and `next_steps` from the Harness Team Lead.

Example verified commands:

```bash
python3 smoke_test.py
python3 main.py --profile workspace --mode plan --save-run-log \
  "只读总结当前 profile 的规则文件和验证命令，不要改文件。"
python3 main.py --profile workspace --mode review --save-run-log \
  "只读检查 codex-harness-runner 的 smoke test 是否仍是最小 MCP 可用性验证；不要改文件。"
```

## Core initialization

```python
async with MCPServerStdio(
    cache_tools_list=True,
    name="Codex CLI",
    params={
        "command": "codex",
        "args": ["mcp-server"],
        "cwd": "/home/zj/workspace",
    },
    client_session_timeout_seconds=360000,
) as codex_mcp:
```

Codex MCP exposes two tools:

- `codex`: start a new Codex session. Pass `prompt`, `cwd`, `sandbox`, `approval-policy`, and optionally `model`.
- `codex-reply`: continue an existing Codex session with `threadId` and `prompt`.

Do not register this server as a global MCP server for the same Codex Desktop session unless you explicitly want recursive Codex-to-Codex behavior. For multi-agent workflows, start it from the Agents SDK runner.
