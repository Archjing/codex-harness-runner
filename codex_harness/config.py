from __future__ import annotations

import logging
import os
from pathlib import Path

from agents import set_default_openai_client, set_tracing_disabled
from dotenv import load_dotenv
from openai import AsyncOpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TIMEOUT_SECONDS = 360000


class _CodexEventValidationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return not (
            "Failed to validate notification" in message and "codex/event" in message
        )


def install_logging_filters() -> None:
    """Codex CLI MCP server emits codex/event notifications that older MCP clients log noisily."""
    logging.getLogger().addFilter(_CodexEventValidationFilter())


def configure_openai_client() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=True)

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    set_tracing_disabled(os.getenv("OPENAI_AGENTS_DISABLE_TRACING", "true").lower() != "false")
    set_default_openai_client(
        AsyncOpenAI(api_key=api_key, base_url=base_url or None),
        use_for_tracing=False,
    )


def codex_timeout_seconds() -> float:
    return float(os.getenv("CODEX_MCP_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))
