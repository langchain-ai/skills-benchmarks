"""Minimal Google ADK agent. No tracing wired up — Claude must add it."""

import asyncio

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()


async def main() -> None:
    agent = Agent(
        name="researcher",
        model="gemini-2.0-flash",
        instruction="You answer briefly and cite sources when asked.",
    )

    session_service = InMemorySessionService()
    await session_service.create_session(app_name="bench", user_id="u", session_id="s")
    runner = Runner(agent=agent, app_name="bench", session_service=session_service)

    message = types.Content(
        role="user",
        parts=[types.Part(text="Name one good book about distributed systems.")],
    )

    async for event in runner.run_async(user_id="u", session_id="s", new_message=message):
        if event.is_final_response() and event.content:
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
