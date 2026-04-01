"""
{{ project_name }} — LangChain / LangGraph application entry point.

Run:
    uv run python main.py
"""
import asyncio

from app.agents.assistant import AssistantAgent
from app.config import settings


async def main() -> None:
    print(f"🤖  {settings.app_name} starting up …\n")

    agent = AssistantAgent()

    # Interactive REPL
    print("Type your message (Ctrl-C to quit):\n")
    history: list[dict[str, str]] = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        response = await agent.invoke(user_input, history=history)
        print(f"AI:  {response}\n")

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    asyncio.run(main())
