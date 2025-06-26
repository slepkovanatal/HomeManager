import logging
import openai

from services.openai_client import client
from agents.registry import agent_registry

class ExecutorAgent:
    @staticmethod
    def execute(user_input: dict) -> str:
        action_name = ExecutorAgent.decide_action(user_input)
        logging.info(f"ExecutorAgent: chosen action = {action_name}")

        try:
            action_class = agent_registry.get_agent(action_name)
            return action_class.execute(user_input["arguments"])
        except Exception as e:
            logging.exception("Failed to execute action.")
            return f"❌ Error: {str(e)}"

    @staticmethod
    def decide_action(user_input: dict) -> str:
        actions = agent_registry.list_agents()
        function_list = "\n".join(
            f"- {name}: {info.description}" for name, info in actions.items()
        )

        prompt = f"""
You are a smart router for a Telegram bot that manages groceries and food items.
You are given a user message and must decide which function from available functions to use.

Available functions:
{function_list}

User message:
\"\"\"{user_input["action"]}\"\"\"

Which one of the functions should be used? Just reply with the function name or 
with "none" if you can't find appropriate function.
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        return response.choices[0].message.content.strip().lower()
