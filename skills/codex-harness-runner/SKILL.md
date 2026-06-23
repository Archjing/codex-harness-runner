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

## Output expectations

- State the profile, mode, and verification status.
- Include the run log path when a run log was saved.
- Mention any missing setup, missing profile, missing API key, or Codex CLI availability problem directly.
