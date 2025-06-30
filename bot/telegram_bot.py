import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

from agents.executor_agent import ExecutorAgent
from agents.expire_item_agent import ExpireItemAgent
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
    context.user_data['product_list'] = suitable_products
    await send_product_options(update, suitable_products)

    # # Show options
    # await send_buttons(update, context)

async def send_product_options(update: Update, product_list: list[dict]):
    keyboard = []

    for idx, product_data in enumerate(product_list, 1):
        # Each row has two buttons: open link and select product
        row = [
            InlineKeyboardButton("🌐 Open Link", url=product_data["productUrl"]),  # Opens the product page
            InlineKeyboardButton(f"✅ Select Product {idx}", callback_data=f'product_select_{idx}')  # Tracks selection
        ]
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = 'Please review the products using the links and then select the best match:'

    await update.message.reply_text(message_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def handle_product_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_option = query.data  # Example: 'product_select_1'

    # Extract product index
    product_index = int(selected_option.split('_')[2]) - 1

    # Retrieve product info (you should store it in user context/session)
    selected_product = context.user_data['product_list'][product_index]
    context.user_data["selected_product"] = selected_product

    expired_button = InlineKeyboardButton("🗑️ Expired", callback_data="expired")
    finished_button = InlineKeyboardButton("✅ Finished", callback_data="finished")

    keyboard = [[expired_button, finished_button]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=f'You selected:\n{selected_product["productUrl"]}\n', reply_markup=reply_markup)

async def handle_expiration_finishing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_option = query.data
    if selected_option == "expired":
        text = ExpireItemAgent.execute({
            "item_name": context.user_data["selected_product"]["productTitle"],
            "item_price": context.user_data["selected_product"]["price"]
        })

        await query.edit_message_text(text=text)

# Register all handlers
def register_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(handle_product_selection, pattern='^product_select_'))
    application.add_handler(CallbackQueryHandler(handle_expiration_finishing, pattern='^(expired|finished)$'))

# Run the bot
def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    register_handlers(app)
    print("🤖 Bot is running...")
    app.run_polling()
