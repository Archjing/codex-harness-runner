from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .profiles import HarnessProfile, PROJECT_ROOT
from .schemas import VerificationStatus


RUNS_DIR = PROJECT_ROOT / "runs"


@dataclass
class RunSummary:
    run_id: str
    created_at: str
    profile: str
    cwd: str
    mode: str
    prompt: str
    output: str
    model: str
    sandbox: str
    approval_policy: str
    rules: list[str]
    missing_rules: list[str]
    verification_status: VerificationStatus
    verification_commands: list[str]
    verification_evidence: list[str]
    files_changed: list[str]
    next_steps: list[str]


def make_run_id(prompt: str) -> str:
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", prompt.strip().lower()).strip("-")[:48]
    return now.strftime("%Y%m%d-%H%M%S") + ("-" + slug if slug else "")


def build_summary(
    *,
    run_id: str,
    profile: HarnessProfile,
    mode: str,
    prompt: str,
    output: str,
    verification_status: VerificationStatus = "not_run",
    verification_commands: list[str] | None = None,
    verification_evidence: list[str] | None = None,
    files_changed: list[str] | None = None,
    next_steps: list[str] | None = None,
) -> RunSummary:
    commands = verification_commands
    if commands is None:
        commands = list(profile.verify_doc if mode in {"plan", "review"} else profile.verify_code)
    return RunSummary(
        run_id=run_id,
        created_at=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        profile=profile.name,
        cwd=str(profile.cwd),
        mode=mode,
        prompt=prompt,
        output=output,
        model=profile.model,
        sandbox=profile.sandbox,
        approval_policy=profile.approval_policy,
        rules=list(profile.existing_rules),
        missing_rules=list(profile.missing_rules),
        verification_status=verification_status,
        verification_commands=commands,
        verification_evidence=verification_evidence or [],
        files_changed=files_changed or [],
        next_steps=next_steps or [],
    )


def save_summary(summary: RunSummary) -> Path:
    RUNS_DIR.mkdir(exist_ok=True)
    path = RUNS_DIR / f"{summary.run_id}.json"
    path.write_text(
        json.dumps(asdict(summary), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path
