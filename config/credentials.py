from dotenv import load_dotenv
import os

# Load variables from .env into environment
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if TELEGRAM_BOT_TOKEN is None:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in your environment.")

# Google Credentials path
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "config/credentials.json")

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')