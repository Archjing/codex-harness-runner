# Codex Harness Runner with Codex CLI MCP Server

This project runs Codex CLI as a stdio MCP server process for an OpenAI Agents SDK harness team.

Chinese documentation: [README.zh-CN.md](README.zh-CN.md)

Description: Harness engineering runner for project-scoped multi-agent workflows. Uses Codex CLI as a stdio MCP server execution channel.

Terminology used here:

- `MCP` means Model Context Protocol.
- `Codex CLI MCP server` means the local process started with `codex mcp-server`.
- The MCP server exposes tools named `codex` and `codex-reply`; those are the tools the Agents SDK agents call.
- `Codex MCP` may appear as shorthand in older notes, but the precise meaning is `Codex CLI MCP server`.

## What it does

- Starts `codex mcp-server`
- Connects to it with `MCPServerStdio`
- Exposes the `codex` and `codex-reply` tools to repository-capable agents
- Builds a profile-driven Harness Team Lead with Context Curator, Planner, Codex Implementer, Reviewer, Verifier, and Memory Steward specialists
- Supports `--profile`, `--mode`, and optional local JSON run summaries
- Uses long MCP client session timeouts suitable for real Codex work
- Keeps OpenAI API orchestration config in `.env`

## Requirements

Local runner requirements:

- Python 3.12 or newer.
- OpenAI Agents SDK and Python dependencies from `requirements.txt`.
- Codex CLI available on `PATH`; verify with `codex --version`.
- A working Codex CLI login/config under the same user that runs the runner.
- `.env` with `OPENAI_API_KEY` and, for compatible gateways, `OPENAI_BASE_URL` including `/v1`.
- At least one local `profiles/*.toml` file copied from `profiles/example.toml`.
- Target project paths must stay under `CODEX_HARNESS_WORKSPACE_ROOT`; by default this is the current user's home directory.

Containerization status:

- No Docker image is provided for now.
- Do not pursue a Docker image unless the final image can stay under 500 MB.
- A first Docker attempt was intentionally stopped because Debian `nodejs` / `npm` packages alone were projected to add about 370 MB before Python dependencies and Codex CLI, making a sub-500 MB image unlikely.
- Prefer local execution for now; revisit containers later only with a lighter base, a prebuilt Codex binary strategy, or a narrower runtime target.

## Setup

```bash
python3 -m pip install --user -r requirements.txt
```

Then configure the runner:

```bash
cp .env.example .env
```

Put your API key into `.env`.

If you need a custom API gateway or compatible endpoint, also set:

```bash
OPENAI_BASE_URL=https://your-base-url/v1
```

Optional defaults passed to Codex tool calls through the MCP server:

```bash
CODEX_MCP_CWD=/path/to/your/workspace
CODEX_MCP_MODEL=gpt-5.4
CODEX_MCP_SANDBOX=workspace-write
CODEX_MCP_APPROVAL_POLICY=never
CODEX_MCP_TIMEOUT_SECONDS=360000
CODEX_HARNESS_WORKSPACE_ROOT=/path/to/your/workspace
```

Project/workspace defaults live in local `profiles/*.toml` files. These files are ignored by Git because they can contain local paths and provider choices. Start from `profiles/example.toml`.

## Smoke test

This verifies that Codex CLI starts as a stdio MCP server process and exposes the expected tools. It does not run a full model workflow.

```bash
python3 smoke_test.py
```

Expected output includes:

```text
codex_mcp_server=ready
profile=workspace
tools=codex,codex-reply
```

## Profiles

Create local profiles by copying the example:

```bash
cp profiles/example.toml profiles/workspace.toml
```

Common local profile names:

- `workspace`
- `app`
- `docs`
- `research`

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

## Use With Agent Tools

You can ask Codex, Claude Code, or another coding agent to wire this runner into a project. Give the agent the runner path, target project path, expected roles, rule files, verification commands, and the boundary that secrets must stay in `.env`.

Recommended instruction:

```text
Use Codex Harness Runner to create a project-scoped harness multi-agent workflow for this repository.

Runner path: /path/to/codex-harness-runner
Target project path: /path/to/your/project
Profile name: <project-name>

Please do the following:
1. Read the runner README and profiles/example.toml.
2. Create or update runner profiles/<project-name>.toml for this project, keeping secrets out of the profile.
3. Set cwd to the target project path and set CODEX_HARNESS_WORKSPACE_ROOT / CODEX_MCP_CWD guidance if needed.
4. Add project rule files such as AGENTS.md, README.md, docs/*.md, or equivalent files that actually exist.
5. Add minimal verification commands for docs, smoke tests, unit tests, or project-specific checks.
6. If project-specific specialist agents are useful, use codex_harness/agents.example.py as the template, create a local ignored codex_harness/agents.py, and customize the builders before wiring them in.
7. Run python3 smoke_test.py from the runner.
8. Run a plan-mode check with python3 main.py --profile <project-name> --mode plan --save-run-log "<task>".
9. Report the files changed, commands run, verification status, and any remaining manual setup.

Do not commit .env, real profiles/*.toml, run logs, local credentials, API keys, tokens, or private project notes.
```

For most projects, start with `plan` or `review` mode first. Use `implement` or `full` only after the profile boundaries and verification commands are clear.

## Run the Harness team

```bash
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
  "只读检查 codex-harness-runner 的 smoke test 是否仍是最小 Codex CLI MCP server 可用性验证；不要改文件。"
```

## Core initialization

```python
async with MCPServerStdio(
    cache_tools_list=True,
    name="Codex CLI",
    params={
        "command": "codex",
        "args": ["mcp-server"],
        "cwd": "/path/to/your/workspace",
    },
    client_session_timeout_seconds=360000,
) as codex_mcp:
```

The Codex CLI MCP server exposes two tools:

- `codex`: start a new Codex session. Pass `prompt`, `cwd`, `sandbox`, `approval-policy`, and optionally `model`.
- `codex-reply`: continue an existing Codex session with `threadId` and `prompt`.

Do not register this server as a global MCP server for the same Codex Desktop session unless you explicitly want recursive Codex-to-Codex behavior. For multi-agent workflows, start the stdio MCP server from this Agents SDK runner.
