import asyncio

from codex_harness.config import install_logging_filters
from codex_harness.mcp import codex_mcp_server
from codex_harness.profiles import load_profile


async def main() -> None:
    install_logging_filters()
    profile = load_profile()
    async with codex_mcp_server(profile) as codex_mcp:
        tools = await codex_mcp.list_tools()
        names = sorted(tool.name for tool in tools)
        print("codex_mcp_server=ready")
        print("profile=" + profile.name)
        print("workspace=" + str(profile.cwd))
        print("tools=" + ",".join(names))


if __name__ == "__main__":
    asyncio.run(main())
