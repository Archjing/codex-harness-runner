from __future__ import annotations

from agents import Runner

from .config import configure_openai_client, install_logging_filters
from .mcp import codex_mcp_server
from .profiles import HarnessProfile, load_profile
from .run_log import build_summary, make_run_id, save_summary
from .schemas import HarnessOutput
from .team import build_team


VALID_MODES = ("plan", "review", "implement", "full")


def build_mode_prompt(prompt: str, profile: HarnessProfile, mode: str) -> str:
    return (
        f"Profile: {profile.name}\n"
        f"Mode: {mode}\n"
        f"Workspace: {profile.cwd}\n"
        "Rules: the relevant rule digest is already injected into the orchestrator instructions; "
        "use it before acting.\n"
        "Task:\n"
        f"{prompt}"
    )


async def run_team(
    prompt: str,
    *,
    profile_name: str | None = None,
    mode: str = "full",
    save_run_log: bool = False,
) -> tuple[str, str | None]:
    if mode not in VALID_MODES:
        raise RuntimeError(f"Invalid mode {mode!r}. Expected one of: {', '.join(VALID_MODES)}")

    install_logging_filters()
    configure_openai_client()
    profile = load_profile(profile_name)
    run_id = make_run_id(prompt)

    async with codex_mcp_server(profile) as codex_mcp:
        team = build_team(codex_mcp, profile, mode)
        result = await Runner.run(team, build_mode_prompt(prompt, profile, mode))
        structured = _coerce_output(result.final_output)
        output = structured.answer

    log_path = None
    if save_run_log:
        summary = build_summary(
            run_id=run_id,
            profile=profile,
            mode=mode,
            prompt=prompt,
            output=output,
            verification_status=structured.verification_status,
            verification_commands=structured.verification_commands,
            verification_evidence=structured.verification_evidence,
            files_changed=structured.files_changed,
            next_steps=structured.next_steps,
        )
        log_path = str(save_summary(summary))

    return output, log_path


def _coerce_output(final_output: object) -> HarnessOutput:
    if isinstance(final_output, HarnessOutput):
        return final_output
    if isinstance(final_output, dict):
        return HarnessOutput.model_validate(final_output)
    return HarnessOutput(
        answer=str(final_output),
        verification_status="not_run",
        verification_evidence=["Final output was unstructured; verification status was not machine-readable."],
    )
