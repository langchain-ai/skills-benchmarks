"""Minimal AutoGen agent. No tracing wired up — Claude must add it."""

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    assistant = AssistantAgent(
        name="researcher",
        model_client=model_client,
        system_message="You answer briefly and cite sources when asked.",
    )

    result = await assistant.run(task="Name one good book about distributed systems.")
    print(result.messages[-1].content)


if __name__ == "__main__":
    asyncio.run(main())
