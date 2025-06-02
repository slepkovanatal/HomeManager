from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from agents.add_item_agent import AddItemAgent
from agents.executor_agent import ExecutorAgent

from config.credentials import TELEGRAM_BOT_TOKEN

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hi! Send /add <item name> <price> to add a food item.")

# /add command (e.g. /add Pizza 12.5)
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("⚠️ Usage: /add <item name> <price>")
        return

    # Merge everything except the last arg into item name (in case it's multi-word)
    *item_parts, price = context.args
    item_name = " ".join(item_parts)

    user_input = {"action": "add_item", "arguments": {"item_name": item_name, "item_price": float(price)}}
    # response = AddItemAgent.execute(user_input)

    # user_input = f"Add food item: {item_name} with price {price}"
    response = ExecutorAgent.execute(user_input)

    await update.message.reply_text(f"✅ {response}")

# Register all handlers
def register_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))

# Run the bot
def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    register_handlers(app)
    print("🤖 Bot is running...")
    app.run_polling()
