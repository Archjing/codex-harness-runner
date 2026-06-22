from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from agents import ModelSettings, OpenAIChatCompletionsModel
from openai.types.shared import Reasoning
from openai import AsyncOpenAI


@dataclass(frozen=True)
class AgentModelConfig:
    kind: str
    model: str
    base_url_env: str | None = None
    api_key_env: str | None = None
    reasoning_effort: str | None = None
    verbosity: str | None = None
    extra_body: dict[str, Any] | None = None


def parse_agent_models(raw: dict[str, Any] | None) -> dict[str, AgentModelConfig]:
    if not raw:
        return {}
    parsed: dict[str, AgentModelConfig] = {}
    for role, value in raw.items():
        if not isinstance(value, dict):
            raise RuntimeError(f"agent_models.{role} must be a table")
        kind = str(value.get("kind", "default"))
        model = value.get("model")
        if not model:
            raise RuntimeError(f"agent_models.{role}.model is required")
        parsed[str(role)] = AgentModelConfig(
            kind=kind,
            model=str(model),
            base_url_env=_optional_str(value.get("base_url_env")),
            api_key_env=_optional_str(value.get("api_key_env")),
            reasoning_effort=_optional_str(value.get("reasoning_effort")),
            verbosity=_optional_str(value.get("verbosity")),
            extra_body=_optional_dict(value.get("extra_body"), f"agent_models.{role}.extra_body"),
        )
    return parsed


def resolve_agent_model(config: AgentModelConfig | None) -> str | OpenAIChatCompletionsModel | None:
    if config is None:
        return None

    if config.kind == "default":
        return config.model

    if config.kind == "openai_chat":
        if not config.base_url_env or not config.api_key_env:
            raise RuntimeError("openai_chat agent model requires base_url_env and api_key_env")
        base_url = os.getenv(config.base_url_env)
        api_key = os.getenv(config.api_key_env)
        if not base_url:
            raise RuntimeError(f"Missing environment variable: {config.base_url_env}")
        if not api_key:
            raise RuntimeError(f"Missing environment variable: {config.api_key_env}")
        return OpenAIChatCompletionsModel(
            model=config.model,
            openai_client=AsyncOpenAI(base_url=base_url, api_key=api_key),
            strict_feature_validation=False,
        )

    raise RuntimeError(f"Unsupported agent model kind: {config.kind}")


def resolve_model_settings(config: AgentModelConfig | None) -> ModelSettings:
    if config is None:
        return ModelSettings()
    reasoning = None
    if config.reasoning_effort:
        reasoning = Reasoning(effort=config.reasoning_effort)  # type: ignore[arg-type]
    return ModelSettings(
        reasoning=reasoning,
        verbosity=config.verbosity,  # type: ignore[arg-type]
        extra_body=config.extra_body,
    )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_dict(value: object, label: str) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} must be a table")
    return value
