from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


# Optional: if you want to use environment variables or config files
# from agent_system.base import ExecutorAgent
from config.credentials import TELEGRAM_BOT_TOKEN

# Create a global instance of the ExecutorAgent
# executor = ExecutorAgent()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hi! Send /add <item name> <price> to add a food item.")

# /add command (e.g. /add Pizza 12.5)
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # if not context.args or len(context.args) < 2:
    #     await update.message.reply_text("⚠️ Usage: /add <item name> <price>")
    #     return
    #
    # # Merge everything except the last arg into item name (in case it's multi-word)
    # *item_parts, price = context.args
    # item_name = " ".join(item_parts)
    #
    # # user_input = {"action": "add_item", "item_name": item_name, "item_price": price}
    # user_input = f"Add food item: {item_name} with price {price}"
    # response = executor.execute(user_input)
    response = "test"
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
