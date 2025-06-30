from agents.registry import agent_registry
from services.gsheet_service import append_item_to_sheet


@agent_registry.register(name="expire_item", description="Takes a product and put it into expired products sheets")
class ExpireItemAgent:
    @staticmethod
    def execute(arguments: dict) -> str:
        item_name = arguments.get("item_name")
        item_price = arguments.get("item_price")

        if not item_name or item_price is None:
            return "Missing item name or price."

        append_item_to_sheet(item_name, item_price)

        return f"✅ Added expired item '{item_name}' (€{item_price:.2f}) to the Google Sheets."
