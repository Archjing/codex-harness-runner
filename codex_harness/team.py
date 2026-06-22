from __future__ import annotations

from agents import Agent
from agents.mcp import MCPServerStdio

from .models import resolve_agent_model, resolve_model_settings
from .profiles import HarnessProfile
from .schemas import HarnessOutput


def codex_call_policy(profile: HarnessProfile) -> str:
    return (
        "When calling the Codex MCP `codex` tool, always include these arguments unless the "
        f"user explicitly overrides them: cwd={str(profile.cwd)!r}, model={profile.model!r}, "
        f"sandbox={profile.sandbox!r}, approval-policy={profile.approval_policy!r}. "
        "Keep changes scoped to the profile cwd, avoid destructive commands, and return the "
        "Codex threadId when a continuing conversation is useful."
    )


def profile_context(profile: HarnessProfile) -> str:
    existing = ", ".join(profile.existing_rules) or "(none)"
    missing = ", ".join(profile.missing_rules) or "(none)"
    verify_doc = "; ".join(profile.verify_doc) or "(none)"
    verify_code = "; ".join(profile.verify_code) or "(none)"
    agent_models = ", ".join(
        f"{role}:{config.kind}/{config.model}" for role, config in sorted(profile.agent_models.items())
    ) or "(default)"
    return (
        f"Profile: {profile.name}\n"
        f"CWD: {profile.cwd}\n"
        f"Existing rule files: {existing}\n"
        f"Missing rule files: {missing}\n"
        f"Doc verification commands: {verify_doc}\n"
        f"Code verification commands: {verify_code}\n"
        f"Agent model routing: {agent_models}\n"
        f"Rule digest:\n{profile.rule_digest()}\n"
    )


def build_team(codex_mcp: MCPServerStdio, profile: HarnessProfile, mode: str) -> Agent:
    context_curator_model = profile.agent_models.get("context_curator")
    planner_model = profile.agent_models.get("planner")
    implementer_model = profile.agent_models.get("implementer")
    reviewer_model = profile.agent_models.get("reviewer")
    verifier_model = profile.agent_models.get("verifier")
    memory_steward_model = profile.agent_models.get("memory_steward")
    team_lead_model = profile.agent_models.get("team_lead")

    context_curator = Agent(
        name="Context Curator",
        model=resolve_agent_model(context_curator_model),
        model_settings=resolve_model_settings(context_curator_model),
        instructions=(
            "Read the profile context and identify the smallest useful rule files and facts for "
            "the task. Separate facts, assumptions, missing context, and recommended next reads. "
            "Do not edit files."
        ),
    )

    planner = Agent(
        name="Planner",
        model=resolve_agent_model(planner_model),
        model_settings=resolve_model_settings(planner_model),
        instructions=(
            "Create short, decision-complete plans. Include goal, scope, non-goals, risks, "
            "verification commands, and rollback. Do not edit files."
        ),
    )

    implementer = Agent(
        name="Codex Implementer",
        model=resolve_agent_model(implementer_model),
        model_settings=resolve_model_settings(implementer_model),
        instructions=(
            "Use the Codex MCP tools for repository inspection and implementation. "
            f"{codex_call_policy(profile)}"
        ),
        mcp_servers=[codex_mcp],
    )

    reviewer = Agent(
        name="Reviewer",
        model=resolve_agent_model(reviewer_model),
        model_settings=resolve_model_settings(reviewer_model),
        instructions=(
            "Use Codex MCP tools to inspect repository state, diffs, risks, missing tests, and "
            "documentation drift. Findings first, ordered by severity. "
            f"{codex_call_policy(profile)}"
        ),
        mcp_servers=[codex_mcp],
    )

    verifier = Agent(
        name="Verifier",
        model=resolve_agent_model(verifier_model),
        model_settings=resolve_model_settings(verifier_model),
        instructions=(
            "Use the profile verification commands as the source of truth. If you cannot run a "
            "command, state why and mark verification as not_run. Do not claim success without "
            "evidence."
        ),
        mcp_servers=[codex_mcp],
    )

    memory_steward = Agent(
        name="Memory Steward",
        model=resolve_agent_model(memory_steward_model),
        model_settings=resolve_model_settings(memory_steward_model),
        instructions=(
            "Identify only stable lessons or documentation updates worth saving. Never write or "
            "repeat API keys, tokens, cookies, or secrets. Prefer repo-local docs over chat memory."
        ),
    )

    tools = [
        context_curator.as_tool(
            tool_name="curate_context",
            tool_description="Identify the smallest relevant profile context and missing facts.",
        ),
        planner.as_tool(
            tool_name="make_plan",
            tool_description="Create a concise implementation or review plan.",
        ),
        reviewer.as_tool(
            tool_name="review_repo",
            tool_description="Review repository state with Codex MCP.",
        ),
        verifier.as_tool(
            tool_name="verify_repo",
            tool_description="Run or assess profile verification commands with Codex MCP.",
        ),
        memory_steward.as_tool(
            tool_name="suggest_memory_updates",
            tool_description="Suggest safe durable documentation or memory updates.",
        ),
    ]
    if mode in {"implement", "full"}:
        tools.insert(
            2,
            implementer.as_tool(
                tool_name="implement_with_codex",
                tool_description="Use Codex MCP to make scoped repository changes.",
            ),
        )

    return Agent(
        name="Harness Team Lead",
        model=resolve_agent_model(team_lead_model),
        model_settings=resolve_model_settings(team_lead_model),
        instructions=(
            "You are a profile-driven Harness Engineer orchestrator. Use specialists as tools; "
            "do not hand off the user-facing conversation. Keep outputs evidence-based and concise. "
            f"Current mode: {mode}. In plan mode, do not edit files. In review mode, inspect and "
            "verify without implementing. In implement/full mode, keep changes scoped and verify. "
            "Use the rule digest below as already-read context. If deeper detail is needed, ask "
            "the Codex MCP-backed specialists to inspect files. Final answer must include "
            "verification status: passed, failed, or not_run. Set verification_status to passed "
            "only when concrete command/file evidence proves the check. Set failed when a check "
            "ran and failed. Set not_run when no verification command ran or evidence is indirect. "
            "Put runnable commands in verification_commands, concrete proof in verification_evidence, "
            "and changed files in files_changed.\n\n"
            + profile_context(profile)
        ),
        tools=tools,
        output_type=HarnessOutput,
    )
