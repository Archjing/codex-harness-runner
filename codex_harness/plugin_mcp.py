from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .profiles import DEFAULT_PROFILE, PROJECT_ROOT, available_profiles
from .runner import run_team


INSTRUCTIONS = (
    "Codex Harness Runner exposes project-scoped harness engineering workflows. "
    "Use list_profiles before running a harness task when the profile is unknown. "
    "Prefer plan or review mode before implement or full mode. Never write secrets "
    "to tracked files, and keep work scoped to the selected profile cwd."
)

mcp = FastMCP(
    "Codex Harness Runner",
    instructions=INSTRUCTIONS,
    log_level="WARNING",
)


def _result(
    *,
    ok: bool,
    profile: str,
    mode: str | None = None,
    output: str = "",
    run_log: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    return {
        "ok": ok,
        "profile": profile,
        "mode": mode,
        "output": output,
        "run_log": run_log,
        "error": error,
    }


@mcp.tool()
def list_profiles() -> dict[str, Any]:
    """List local harness profiles without starting a model run."""
    return {
        "ok": True,
        "runner_root": str(PROJECT_ROOT),
        "default_profile": DEFAULT_PROFILE,
        "profiles": available_profiles(),
        "profiles_dir": str(PROJECT_ROOT / "profiles"),
    }


async def _run_harness(
    *,
    prompt: str,
    profile: str,
    mode: str,
    save_run_log: bool,
) -> dict[str, Any]:
    try:
        output, log_path = await run_team(
            prompt,
            profile_name=profile,
            mode=mode,
            save_run_log=save_run_log,
        )
    except Exception as exc:  # MCP tools should report failures instead of crashing the server.
        return _result(
            ok=False,
            profile=profile,
            mode=mode,
            error=f"{type(exc).__name__}: {exc}",
        )
    return _result(
        ok=True,
        profile=profile,
        mode=mode,
        output=output,
        run_log=str(Path(log_path)) if log_path else None,
    )


@mcp.tool()
async def run_harness_plan(
    prompt: str,
    profile: str = DEFAULT_PROFILE,
    save_run_log: bool = True,
) -> dict[str, Any]:
    """Run the harness team in plan mode. This mode must not edit files."""
    return await _run_harness(
        prompt=prompt,
        profile=profile,
        mode="plan",
        save_run_log=save_run_log,
    )


@mcp.tool()
async def run_harness_review(
    prompt: str,
    profile: str = DEFAULT_PROFILE,
    save_run_log: bool = True,
) -> dict[str, Any]:
    """Run the harness team in read-only review mode."""
    return await _run_harness(
        prompt=prompt,
        profile=profile,
        mode="review",
        save_run_log=save_run_log,
    )


@mcp.tool()
async def run_harness_implement(
    prompt: str,
    profile: str = DEFAULT_PROFILE,
    save_run_log: bool = True,
) -> dict[str, Any]:
    """Run the harness team in implement mode, scoped to the selected profile cwd."""
    return await _run_harness(
        prompt=prompt,
        profile=profile,
        mode="implement",
        save_run_log=save_run_log,
    )


@mcp.tool()
async def run_harness_full(
    prompt: str,
    profile: str = DEFAULT_PROFILE,
    save_run_log: bool = True,
) -> dict[str, Any]:
    """Run the full harness workflow: plan, implement, verify, and suggest memory updates."""
    return await _run_harness(
        prompt=prompt,
        profile=profile,
        mode="full",
        save_run_log=save_run_log,
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
