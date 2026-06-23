# Quick Start

This quick start explains how to install Codex Harness Runner and configure a project-scoped harness multi-agent workflow.

## 1. Install the Plugin and Skill

Install the plugin directly from the GitHub marketplace with Codex CLI:

```bash
export PATH="$HOME/.local/bin:$PATH"
codex plugin marketplace add Archjing/codex-harness-runner --sparse .agents/plugins
codex plugin add codex-harness-runner@codex-harness-runner
```

After installation, start a new Codex thread or restart Codex Desktop/CLI. The `$codex-harness-runner` skill and bundled MCP tools are loaded only in new sessions.

## 2. Prepare the Environment

To run local harness workflows, clone the repository and prepare local config:

```bash
git clone https://github.com/Archjing/codex-harness-runner.git
cd codex-harness-runner
uv sync
cp .env.example .env
```

Ensure `uv` is available on `PATH` in the environment that starts Codex Desktop/CLI. The bundled MCP server uses `uv run python -m codex_harness.plugin_mcp`.

Edit `.env` with your model endpoint:

```bash
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://your-base-url/v1
CODEX_HARNESS_WORKSPACE_ROOT=/path/to/your/workspace
CODEX_MCP_CWD=/path/to/your/workspace
CODEX_MCP_MODEL=gpt-5.4
CODEX_MCP_SANDBOX=workspace-write
CODEX_MCP_APPROVAL_POLICY=never
CODEX_MCP_TIMEOUT_SECONDS=360000
```

Verify prerequisites:

```bash
codex --version
python3 smoke_test.py
```

The smoke test should list `codex,codex-reply`. This only verifies that the Codex CLI MCP server starts and exposes tools; it is not a full workflow test.

## 3. Create a Project Profile

Start from the public example:

```bash
cp profiles/example.toml profiles/<project-name>.toml
```

Edit the local profile:

```toml
name = "<project-name>"
cwd = "/path/to/your/project"
model = "gpt-5.4"
sandbox = "workspace-write"
approval_policy = "never"

rules = [
  "AGENTS.md",
  "README.md"
]

verify_doc = [
  "rg -n \"important topic\" README.md docs"
]

verify_code = [
  "python3 -m pytest"
]
```

Real `profiles/*.toml` files are ignored by Git. Keep secrets in `.env`, not in profiles.

## 4. Optional Project Agents

If the project needs custom specialists, use the example beside the local ignored module:

```bash
cp codex_harness/agents.example.py codex_harness/agents.py
```

Then customize `codex_harness/agents.py` locally. Do not commit it unless you have removed private project details.

## 5. Local Setup Prompt

Use this prompt when asking an assistant to configure a local harness workflow:

```text
Use Codex Harness Runner to create a project-scoped harness multi-agent workflow for this repository.

Runner path: /path/to/codex-harness-runner
Target project path: /path/to/your/project
Profile name: <project-name>

Please do the following:
1. Read the runner README, Quick_Start.md, and profiles/example.toml.
2. Create or update runner profiles/<project-name>.toml for this project, keeping secrets out of the profile.
3. Set cwd to the target project path and set CODEX_HARNESS_WORKSPACE_ROOT / CODEX_MCP_CWD guidance if needed.
4. Add project rule files such as AGENTS.md, README.md, docs/*.md, or equivalent files that actually exist.
5. Add minimal verification commands for docs, smoke tests, unit tests, or project-specific checks.
6. If project-specific specialist agents are useful, use codex_harness/agents.example.py as the template, create a local ignored codex_harness/agents.py, and customize the builders before wiring them in.
7. Run uv sync and python3 smoke_test.py from the runner.
8. Run a plan-mode check with python3 main.py --profile <project-name> --mode plan --save-run-log "<task>".
9. Report the files changed, commands run, verification status, and any remaining manual setup.

Do not commit .env, real profiles/*.toml, run logs, local credentials, API keys, tokens, or private project notes.
```

## 6. First Workflow Run

Start in `plan` mode:

```bash
python3 main.py --profile <project-name> --mode plan --save-run-log \
  "Inspect this project profile and propose a harness workflow. Do not edit files."
```

Then use `review` mode for read-only checks:

```bash
python3 main.py --profile <project-name> --mode review --save-run-log \
  "Review the current project state and identify missing verification coverage. Do not edit files."
```

Use `implement` or `full` only after the profile boundaries and verification commands are clear.

Do not run multiple harness/Codex CLI write tasks against the same `profile.cwd` at the same time. If parallel work is required, create a separate Git worktree and a separate profile for each task.
