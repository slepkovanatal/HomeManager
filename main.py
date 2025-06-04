from bot.telegram_bot import run_bot

from agents.loader import load_all_agents

if __name__ == "__main__":
    load_all_agents()
    run_bot()