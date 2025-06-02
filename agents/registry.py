class Registry:
    def __init__(self):
        self.agents = {}

    def register(self, name: str):
        def decorator(agent_class):
            self.agents[name] = agent_class
            return agent_class
        return decorator

    def get_agent(self, name: str):
        return self.agents[name]

    def list_agents(self):
        return self.agents

agent_registry = Registry()
