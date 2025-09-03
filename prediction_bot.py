import logging
import random
from datetime import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ---- Aapka Bot Token ----
BOT_TOKEN = "8277402061:AAFee5gZHZq5BCG50FtAtHaQ7iL5lvlOt2I"

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Function to send prediction
async def send_prediction(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    prediction = round(random.uniform(1.0, 2.0), 2)  # Random between 1.0x - 2.0x
    msg = f"🎯 Prediction: {prediction}x\n✅ Safe Cash Out!"
    await context.bot.send_message(chat_id=chat_id, text=msg)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Remove old jobs
    old_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in old_jobs:
        job.schedule_removal()

    await update.message.reply_text(
        "🚀 Prediction Bot Started!\n"
        "Har exact 1 minute pe ek prediction milega.\n"
        "❌ Stop karne ke liye /stop type karein."
    )

    # Har clock ke start of minute pe prediction bhejna
    # context.job_queue.run_minutely is not available, use run_repeating with interval 60 seconds
    context.job_queue.run_repeating(
        send_prediction, interval=60, first=0, chat_id=chat_id, name=str(chat_id)
    )

# Stop command
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if not jobs:
        await update.message.reply_text("❌ Koi active prediction job nahi mila.")
        return
    for job in jobs:
        job.schedule_removal()
    await update.message.reply_text("🛑 Prediction Bot Stopped!")

# Main function
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
