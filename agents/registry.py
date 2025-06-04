from dataclasses import dataclass
from typing import Type, Any


@dataclass
class Action:
    name: str
    description: str
    agent_class: Type[Any] #TODO use a base class for all agents


class Registry:
    def __init__(self):
        self.agents: dict[str, Action] = {}

    def register(self, name: str, description: str):
        def decorator(agent_class):
            self.agents[name] = Action(name=name, description=description, agent_class=agent_class)
            return agent_class
        return decorator

    def get_agent(self, name: str) -> Type[Any]:
        if name not in self.agents:
            raise ValueError(f"No agent registered under the name {name}")
        return self.agents[name].agent_class

    def get_description(self, name: str) -> str:
        if name not in self.agents:
            raise ValueError(f"No agent registered under the name {name}")
        return self.agents[name].description

    def list_agents(self):
        return self.agents.copy()

agent_registry = Registry()
