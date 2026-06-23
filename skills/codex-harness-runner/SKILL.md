---
name: codex-harness-runner
description: Use when the user wants to create, configure, or run a Codex Harness Runner project-scoped multi-agent workflow, set up harness profiles, invoke bundled MCP tools, or wire Codex/Claude Code style agents into a repository workflow.
---

# Codex Harness Runner

Use this skill to help a user create and run project-scoped harness engineering teams with Codex Harness Runner.

## What this plugin provides

- A reusable workflow for creating local `profiles/*.toml` files from `profiles/example.toml`.
- Bundled MCP tools for running the harness team in `plan`, `review`, `implement`, or `full` mode.
- Guidance for using Codex CLI as the repository execution channel through the runner.

## Safety boundaries

- Do not write secrets to tracked files.
- Do not commit `.env`, real `profiles/*.toml`, `runs/*.json`, local credentials, API keys, tokens, cookies, or private project notes.
- Keep target project paths under `CODEX_HARNESS_WORKSPACE_ROOT`.
- Prefer `plan` or `review` mode before `implement` or `full` mode.
- Report whether verification passed, failed, or was not run.

## Standard workflow

1. Read the repository `README.md` or `README.en.md`.
2. Confirm Python dependencies are synchronized with `uv`:

```bash
uv sync
```

3. Ensure `uv` is available on `PATH` in the environment that starts Codex Desktop/CLI.
4. Ensure `.env` exists locally and contains `OPENAI_API_KEY`; compatible gateways should set `OPENAI_BASE_URL` including `/v1`.
5. Create a local profile from `profiles/example.toml`; do not commit the real profile.
6. Run `python3 smoke_test.py` to verify the Codex CLI MCP server can start and expose `codex` / `codex-reply`.
7. Use the bundled MCP tools when available:
   - `list_profiles`
   - `run_harness_plan`
   - `run_harness_review`
   - `run_harness_implement`
   - `run_harness_full`
8. Start with `run_harness_plan` unless the user explicitly asks to implement.

## Local setup prompt

When the user needs help configuring this plugin for a local project, offer this prompt for Codex, Claude Code, or another coding agent:

```text
Use Codex Harness Runner to configure a local harness workflow for this project.

Runner repository path: <path-to-codex-harness-runner>
Target project path: <path-to-target-project>
Profile name: <project-name>

Please do the following:
1. Read the runner README, docs/快速上手.md or docs/Use-With-Agent-Tools.md, and profiles/example.toml.
2. Verify `uv` is available on PATH and run `uv sync` from the runner repository.
3. If `.env` does not exist, create it from `.env.example`; do not fill in or print secret values.
4. Tell me exactly which environment variables I need to fill in, including `OPENAI_API_KEY`, optional `OPENAI_BASE_URL`, `CODEX_HARNESS_WORKSPACE_ROOT`, and Codex MCP defaults.
5. Create or update `profiles/<project-name>.toml` from `profiles/example.toml`, with `cwd` set to the target project path and rule/verification entries based only on files that actually exist.
6. Keep `.env`, real `profiles/*.toml`, run logs, credentials, API keys, tokens, and private project notes untracked and uncommitted.
7. Run `python3 smoke_test.py` from the runner repository.
8. Run a first plan check with `python3 main.py --profile <project-name> --mode plan --save-run-log "<task>"`.
9. Report changed local files, commands run, verification status, and any values I still need to fill manually.
```

## Output expectations

- State the profile, mode, and verification status.
- Include the run log path when a run log was saved.
- Mention any missing setup, missing profile, missing API key, or Codex CLI availability problem directly.
