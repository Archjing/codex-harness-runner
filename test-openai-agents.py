import os

from agents import RunConfig, Runner, set_default_openai_client, set_tracing_disabled
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.entries import GitRepo
from agents.sandbox.sandboxes.unix_local import UnixLocalSandboxClient
from dotenv import load_dotenv
from openai import AsyncOpenAI


load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")
if not base_url:
    raise RuntimeError("OPENAI_BASE_URL is not set")

set_tracing_disabled(True)
set_default_openai_client(
    AsyncOpenAI(api_key=api_key, base_url=base_url),
    use_for_tracing=False,
)

agent = SandboxAgent(
    name="Workspace Assistant",
    default_manifest=Manifest(
        entries={
            "repo": GitRepo(repo="openai/openai-agents-python", ref="main"),
        }
    ),
    instructions=(
        "Inspect files under `repo/`. Read `repo/README.md` before answering. "
        "Summarize only facts supported by the README. Answer in concise Chinese."
    ),
)

result = Runner.run_sync(
    agent,
    "Inspect the repo README and summarize what this project does.",
    run_config=RunConfig(
        sandbox=SandboxRunConfig(client=UnixLocalSandboxClient()),
        tracing_disabled=True,
    ),
)

print(result.final_output)
