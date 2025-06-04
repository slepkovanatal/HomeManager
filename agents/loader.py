import os
import importlib

EXCLUDED_MODULES = {"__init__", "loader", "executor_agent", "registry"}

def load_all_agents():
    """
    Dynamically import all agent modules (except excluded ones)
    so that their decorators run and they are registered in the Registry.
    """
    agent_dir = os.path.dirname(__file__)
    base_package = __name__.rsplit('.', 1)[0] if '.' in __name__ else "agents"

    for filename in os.listdir(agent_dir):
        if filename.endswith(".py"):
            module_name = filename[:-3]  # strip .py extension
            if module_name in EXCLUDED_MODULES:
                continue

            full_module_path = f"{base_package}.{module_name}"
            importlib.import_module(full_module_path)
