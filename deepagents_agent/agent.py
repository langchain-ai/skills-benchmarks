from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend


def make_graph(config):
    model = config["configurable"].get("model", "anthropic/claude-sonnet-4-6")

    project_skills = Path(__file__).parent / "skills"
    skills = [str(project_skills)] if project_skills.exists() else None

    return create_deep_agent(
        model=model,
        backend=FilesystemBackend(root_dir="/workspace"),
        skills=skills,
    )
