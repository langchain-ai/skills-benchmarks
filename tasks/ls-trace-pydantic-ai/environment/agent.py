"""Minimal PydanticAI agent. No tracing wired up — Claude must add it."""

from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()


def main() -> None:
    agent = Agent("openai:gpt-4o-mini")
    result = agent.run_sync("Name one good book about distributed systems.")
    print(result.output)


if __name__ == "__main__":
    main()
