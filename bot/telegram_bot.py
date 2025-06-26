import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from agents.executor_agent import ExecutorAgent
from agents.product_info_collector import ProductInfoCollector

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

    user_input = {"action": "expire_item", "arguments": {"item_name": item_name, "item_price": float(price)}}
    # response = AddItemAgent.execute(user_input)

    # user_input = f"Add food item: {item_name} with price {price}"
    response = ExecutorAgent.execute(user_input)

    await update.message.reply_text(f"✅ {response}")

# === Handle Received Photo ===
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Get photo file ID (the highest resolution version)
    photo_file_id = update.message.photo[-1].file_id

    tmp_folder = 'tmp'
    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)

    product_file_path = os.path.join(tmp_folder, 'product_photo.jpg')

    # Download the photo immediately
    product_photo_file = await context.bot.get_file(photo_file_id)
    await product_photo_file.download_to_drive(product_file_path)

    # Save photo ID in user's session
    context.user_data['photo_file_path'] = product_file_path

    suitable_products = ProductInfoCollector().execute()
    text = ""
    for i, url in enumerate(suitable_products):
        text += url
        if i < len(suitable_products) - 1:
            text += "\n"

    await context.bot.send_message(chat_id=chat_id, text=f"Image received!\n{text}")

    # # Show options
    # await send_buttons(update, context)

# Register all handlers
def register_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# Run the bot
def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    register_handlers(app)
    print("🤖 Bot is running...")
    app.run_polling()
