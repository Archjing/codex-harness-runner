from __future__ import annotations

from agents import Agent
from agents.mcp import MCPServerStdio

from codex_harness.models import resolve_agent_model, resolve_model_settings
from codex_harness.profiles import HarnessProfile


def build_project_architect(profile: HarnessProfile) -> Agent:
    model_config = profile.agent_models.get("project_architect")
    return Agent(
        name="Project Architect",
        model=resolve_agent_model(model_config),
        model_settings=resolve_model_settings(model_config),
        instructions=(
            "You are the project architect for this profile. Check whether the task fits the "
            "project boundaries, roadmap, and non-goals. Separate facts, assumptions, risks, "
            "and next steps. Do not edit files."
        ),
    )


def build_project_verifier(profile: HarnessProfile, codex_mcp: MCPServerStdio) -> Agent:
    model_config = profile.agent_models.get("project_verifier")
    return Agent(
        name="Project Verifier",
        model=resolve_agent_model(model_config),
        model_settings=resolve_model_settings(model_config),
        instructions=(
            "You are the project verifier for this profile. Prefer the profile verification "
            "commands and record whether checks passed, failed, or were not run. Do not claim "
            "success without command or file evidence."
        ),
        mcp_servers=[codex_mcp],
    )
