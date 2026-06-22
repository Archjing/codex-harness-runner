from __future__ import annotations

import argparse
import asyncio

from codex_harness.profiles import available_profiles
from codex_harness.runner import VALID_MODES, run_team


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a profile-driven Codex Harness team.")
    parser.add_argument(
        "prompt",
        nargs="?",
        default=(
            "Inspect the current profile through the Harness team and summarize the available "
            "Codex CLI MCP server workflow."
        ),
    )
    parser.add_argument(
        "--profile",
        default=None,
        help="Profile name from profiles/*.toml. Available: " + ", ".join(available_profiles()),
    )
    parser.add_argument(
        "--mode",
        choices=VALID_MODES,
        default="full",
        help="Execution mode. plan/review avoid implementation; implement/full may edit files.",
    )
    parser.add_argument(
        "--save-run-log",
        action="store_true",
        help="Write a local JSON run summary under runs/.",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    output, log_path = await run_team(
        args.prompt,
        profile_name=args.profile,
        mode=args.mode,
        save_run_log=args.save_run_log,
    )
    print(output)
    if log_path:
        print(f"\nrun_log={log_path}")


if __name__ == "__main__":
    asyncio.run(main())
