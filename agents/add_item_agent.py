# from agent_system.registry import agent_registry
from services.gsheet_service import append_item_to_sheet


# @agent_registry.register("add_item")
class AddItemAgent:
    @staticmethod
    def execute(arguments: dict) -> str:
        item_name = arguments.get("item_name")
        item_price = arguments.get("item_price")

        if not item_name or item_price is None:
            return "Missing item name or price."

        append_item_to_sheet(item_name, item_price)

        return f"✅ Added '{item_name}' (${item_price:.2f}) to the Google Doc."
