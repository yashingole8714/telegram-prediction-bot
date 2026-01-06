import asyncio
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler
)

nest_asyncio.apply()

# =========================
# CONFIG
# =========================
BOT_TOKEN = "8563537238:AAHw8DL2QHCZ5uQKcoA868pBwNvVBkzH1fw"
GROUP_CHAT_ID = -1002058295574
ADMIN_ID = 2035800544

GAME_NAME = "RAJA GAME"
INTERVAL_SECONDS = 60

# ✅ WIN STICKERS
WIN_STICKER_1 = "CAACAgEAAx0Ceq8ZFgACAXRpWkDBzQ6TrYAV7r08EzeDCnSFCQACnwMAAonfWETOikC8ytx7RTgE"
WIN_STICKER_2 = "CAACAgIAAx0Ceq8ZFgACAXVpWkDDLuge9sy6RW96QRBH3kozFwACKQADWbv8JWiEdiw7SWZ7OAQ"

# =========================
# RUNTIME DATA
# =========================
LAST_ROUND_ID = None
LAST_RESULT = None
LAST_PREDICTION = "SMALL"

BOT_ACTIVE = False   # 🔴 ON / OFF FLAG

# =========================
# HELPERS
# =========================
def safe_numbers(pred):
    return [1, 2, 3] if pred == "SMALL" else [6, 7, 8]

def opposite(pred):
    return "BIG" if pred == "SMALL" else "SMALL"

# =========================
# BUILD MESSAGE
# =========================
def build_message():
    nums = safe_numbers(LAST_PREDICTION)
    return (
        f"📊 *RAJA GAME Prediction*\n\n"
        f"⏭️ *NEXT LIVE ROUND:* {LAST_ROUND_ID}\n\n"
        f"🎯 *BET TYPE:* {LAST_PREDICTION}\n\n"
        f"🔢 *SAFE NUMBERS:* {' • '.join(map(str, nums))}"
    )

# =========================
# COMMANDS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_ACTIVE

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Admin only")
        return

    BOT_ACTIVE = True
    await update.message.reply_text("✅ Bot STARTED")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_ACTIVE

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Admin only")
        return

    BOT_ACTIVE = False
    await update.message.reply_text("⛔ Bot STOPPED")

async def set_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global LAST_ROUND_ID, LAST_RESULT

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Admin only")
        return

    try:
        LAST_ROUND_ID = int(context.args[0])
        LAST_RESULT = int(context.args[1])
        await update.message.reply_text(
            f"✅ Data Set\nRound: {LAST_ROUND_ID}\nResult: {LAST_RESULT}"
        )
    except:
        await update.message.reply_text("Usage: /set <round> <0-9>")

# =========================
# AUTO JOB
# =========================
async def auto_job(context: ContextTypes.DEFAULT_TYPE):
    global LAST_ROUND_ID, BOT_ACTIVE

    if not BOT_ACTIVE:
        return   # 🔕 bot OFF hai

    if LAST_ROUND_ID is None:
        return

    LAST_ROUND_ID += 1

    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=build_message(),
        parse_mode="Markdown"
    )

    keyboard = [[
        InlineKeyboardButton("✅ WIN", callback_data="win"),
        InlineKeyboardButton("❌ LOSS", callback_data="loss")
    ]]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🎯 Confirm Result\nRound: {LAST_ROUND_ID}",
        reply_markup=markup
    )

# =========================
# BUTTON HANDLER
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global LAST_PREDICTION

    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Not allowed", show_alert=True)
        return

    if query.data == "win":
        await context.bot.send_message(GROUP_CHAT_ID, "✅ WIN CONFIRMED")
        await context.bot.send_sticker(GROUP_CHAT_ID, WIN_STICKER_1)
        await context.bot.send_sticker(GROUP_CHAT_ID, WIN_STICKER_2)

    elif query.data == "loss":
        await context.bot.send_message(GROUP_CHAT_ID, "❌ LOSS CONFIRMED")
        LAST_PREDICTION = opposite(LAST_PREDICTION)

    await query.edit_message_reply_markup(reply_markup=None)

# =========================
# MAIN
# =========================
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("set", set_data))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.job_queue.run_repeating(auto_job, interval=INTERVAL_SECONDS, first=5)

    print("🔥 RAJA GAME Bot Running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
