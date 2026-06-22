from __future__ import annotations

from agents.mcp import MCPServerStdio

from .config import codex_timeout_seconds
from .profiles import HarnessProfile


def codex_mcp_server(profile: HarnessProfile) -> MCPServerStdio:
    return MCPServerStdio(
        cache_tools_list=True,
        name="Codex CLI",
        params={
            "command": "codex",
            "args": ["mcp-server"],
            "cwd": str(profile.cwd),
        },
        client_session_timeout_seconds=codex_timeout_seconds(),
        max_retry_attempts=1,
        retry_backoff_seconds_base=2.0,
    )
