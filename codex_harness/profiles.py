from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .models import AgentModelConfig, parse_agent_models


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILES_DIR = PROJECT_ROOT / "profiles"
DEFAULT_PROFILE = "workspace"
ALLOWED_WORKSPACE_ROOT = Path("/home/zj/workspace").resolve()


@dataclass(frozen=True)
class HarnessProfile:
    name: str
    cwd: Path
    model: str = "gpt-5.4"
    sandbox: str = "workspace-write"
    approval_policy: str = "never"
    rules: tuple[str, ...] = field(default_factory=tuple)
    verify_doc: tuple[str, ...] = field(default_factory=tuple)
    verify_code: tuple[str, ...] = field(default_factory=tuple)
    memory_targets: tuple[str, ...] = field(default_factory=tuple)
    agent_models: dict[str, AgentModelConfig] = field(default_factory=dict)

    @property
    def existing_rules(self) -> tuple[str, ...]:
        return tuple(rule for rule in self.rules if (self.cwd / rule).exists())

    @property
    def missing_rules(self) -> tuple[str, ...]:
        return tuple(rule for rule in self.rules if not (self.cwd / rule).exists())

    def rule_digest(self, *, max_chars_per_file: int = 1800) -> str:
        chunks: list[str] = []
        for rule in self.existing_rules:
            path = self.cwd / rule
            text = path.read_text(encoding="utf-8", errors="replace")
            if len(text) > max_chars_per_file:
                text = text[:max_chars_per_file].rstrip() + "\n...[truncated]"
            chunks.append(f"--- {rule} ---\n{text}")
        return "\n\n".join(chunks) if chunks else "(no existing rule files)"


def available_profiles() -> list[str]:
    if not PROFILES_DIR.exists():
        return []
    return sorted(path.stem for path in PROFILES_DIR.glob("*.toml"))


def load_profile(name: str | None = None) -> HarnessProfile:
    profile_name = name or os.getenv("CODEX_HARNESS_PROFILE") or DEFAULT_PROFILE
    path = PROFILES_DIR / f"{profile_name}.toml"
    if not path.exists():
        choices = ", ".join(available_profiles()) or "(none)"
        raise RuntimeError(f"Unknown profile {profile_name!r}. Available profiles: {choices}")

    with path.open("rb") as handle:
        data = tomllib.load(handle)

    cwd = Path(str(data["cwd"])).expanduser().resolve()
    _validate_cwd(cwd)

    return HarnessProfile(
        name=str(data.get("name", profile_name)),
        cwd=cwd,
        model=str(data.get("model", os.getenv("CODEX_MCP_MODEL", "gpt-5.4"))),
        sandbox=str(data.get("sandbox", os.getenv("CODEX_MCP_SANDBOX", "workspace-write"))),
        approval_policy=str(
            data.get("approval_policy", os.getenv("CODEX_MCP_APPROVAL_POLICY", "never"))
        ),
        rules=tuple(str(item) for item in data.get("rules", [])),
        verify_doc=tuple(str(item) for item in data.get("verify_doc", [])),
        verify_code=tuple(str(item) for item in data.get("verify_code", [])),
        memory_targets=tuple(str(item) for item in data.get("memory_targets", [])),
        agent_models=parse_agent_models(data.get("agent_models")),
    )


def _validate_cwd(cwd: Path) -> None:
    if not cwd.exists():
        raise RuntimeError(f"Profile cwd does not exist: {cwd}")
    if not cwd.is_dir():
        raise RuntimeError(f"Profile cwd is not a directory: {cwd}")
    try:
        cwd.relative_to(ALLOWED_WORKSPACE_ROOT)
    except ValueError as exc:
        raise RuntimeError(
            f"Profile cwd must stay under {ALLOWED_WORKSPACE_ROOT}: {cwd}"
        ) from exc
