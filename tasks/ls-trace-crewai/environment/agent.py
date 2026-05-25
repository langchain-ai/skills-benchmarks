"""Minimal CrewAI agent. No tracing wired up — Claude must add it."""

from crewai import LLM, Agent, Crew, Task
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    llm = LLM(model="gpt-4o-mini")

    researcher = Agent(
        role="Researcher",
        goal="Answer briefly and cite sources when asked.",
        backstory="You are a concise researcher.",
        llm=llm,
        allow_delegation=False,
    )

    question = Task(
        description="Name one good book about distributed systems.",
        expected_output="A book title and one short sentence on why.",
        agent=researcher,
    )

    crew = Crew(agents=[researcher], tasks=[question])
    result = crew.kickoff()
    print(result)


if __name__ == "__main__":
    main()
