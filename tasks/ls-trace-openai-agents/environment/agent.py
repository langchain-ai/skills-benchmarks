"""Minimal OpenAI Agents SDK agent. No tracing wired up — Claude must add it."""

import asyncio

from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    agent = Agent(
        name="researcher",
        instructions="You answer briefly and cite sources when asked.",
        model="gpt-4o-mini",
    )
    result = await Runner.run(agent, "Name one good book about distributed systems.")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
