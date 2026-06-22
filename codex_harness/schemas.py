from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


VerificationStatus = Literal["passed", "failed", "not_run"]


class HarnessOutput(BaseModel):
    answer: str = Field(description="Concise user-facing answer in Chinese unless asked otherwise.")
    verification_status: VerificationStatus = Field(
        description="Overall verification state: passed, failed, or not_run."
    )
    verification_evidence: list[str] = Field(
        default_factory=list,
        description="Specific evidence such as command output summaries, file paths, or why not run.",
    )
    verification_commands: list[str] = Field(
        default_factory=list,
        description="Commands that were run or should be run for verification.",
    )
    files_changed: list[str] = Field(
        default_factory=list,
        description="Files changed by this run, or an empty list if none.",
    )
    next_steps: list[str] = Field(
        default_factory=list,
        description="Concrete follow-up actions, if any.",
    )
