import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# === Config ===
TOKEN = ''  # Replace with your bot's token
VOTE_LIMIT = 8  # Max votes for "Yes, I'm in!"

POLL_QUESTION = "Americano padel matcha."
OPTIONS = [
    "Yes, I'm in!",
    "No, I can't",
    "I want to, but all seats are already taken"
]

# === In-memory storage ===
votes = {opt: set() for opt in OPTIONS}  # option -> set of user_ids

# === Logging ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Bot Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(opt, callback_data=opt)] for opt in OPTIONS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"{POLL_QUESTION}\nPlease vote:", reply_markup=reply_markup)
    await send_poll_status(update, context)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    selected_option = query.data

    # Remove user vote from other options (only allow one vote per user)
    for opt in OPTIONS:
        votes[opt].discard(user_id)

    # Handle vote limit for the first option
    if selected_option == OPTIONS[0]:
        if len(votes[OPTIONS[0]]) >= VOTE_LIMIT:
            await query.answer("All seats for 'Yes, I'm in!' are already taken!", show_alert=True)
            return
        else:
            votes[OPTIONS[0]].add(user_id)
            await query.answer("You voted: Yes, I'm in!")
    else:
        votes[selected_option].add(user_id)
        await query.answer(f"You voted: {selected_option}")

    await send_poll_status(query, context, edit=True)

async def send_poll_status(update_or_query, context, edit=False):
    text = f"{POLL_QUESTION}\n\n"
    text += f"1. Yes, I'm in! ({len(votes[OPTIONS[0]])}/{VOTE_LIMIT})\n"
    text += f"2. No, I can't ({len(votes[OPTIONS[1]])})\n"
    text += f"3. I want to, but all seats are already taken ({len(votes[OPTIONS[2]])})\n"

    if edit:
        await update_or_query.edit_message_text(text)
    else:
        await update_or_query.message.reply_text(text)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == "__main__":
    main()
