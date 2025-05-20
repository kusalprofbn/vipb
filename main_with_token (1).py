
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import re

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Lot Size Bot!\n\n"
        "Set your account with:\n"
        "`/setbalance <amount>` (e.g., /setbalance 1000)\n"
        "`/setrisk <percent>` (e.g., /setrisk 1)\n\n"
        "Then paste your trade signal.",
        parse_mode="Markdown"
    )

async def set_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        balance = float(context.args[0])
        user_id = update.effective_user.id
        user_data[user_id] = user_data.get(user_id, {})
        user_data[user_id]['balance'] = balance
        await update.message.reply_text(f"✅ Balance set to ${balance}")
    except:
        await update.message.reply_text("❌ Use format: /setbalance 1000")

async def set_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        risk = float(context.args[0])
        user_id = update.effective_user.id
        user_data[user_id] = user_data.get(user_id, {})
        user_data[user_id]['risk'] = risk
        await update.message.reply_text(f"✅ Risk set to {risk}%")
    except:
        await update.message.reply_text("❌ Use format: /setrisk 1")

async def handle_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_data or 'balance' not in user_data[user_id] or 'risk' not in user_data[user_id]:
        await update.message.reply_text("⚠️ Please set balance and risk using /setbalance and /setrisk")
        return

    entry_match = re.search(r"Entry:\s*([\d,\.]+)", text, re.IGNORECASE)
    sl_match = re.search(r"SL:\s*([\d,\.]+)", text, re.IGNORECASE)

    if not entry_match or not sl_match:
        await update.message.reply_text("❌ Could not extract Entry or SL. Check the format.")
        return

    entry = float(entry_match.group(1).replace(",", ""))
    sl = float(sl_match.group(1).replace(",", ""))
    pip_diff = abs(entry - sl)

    if pip_diff == 0:
        await update.message.reply_text("❌ Entry and SL are the same. Cannot calculate lot size.")
        return

    balance = user_data[user_id]['balance']
    risk_percent = user_data[user_id]['risk']
    dollar_risk = balance * (risk_percent / 100)
    lot_size = dollar_risk / pip_diff

    await update.message.reply_text(
        f"📊 *Lot Size Calculation:*\n\n"
        f"🔹 Entry: `{entry}`\n"
        f"📍 SL: `{sl}` (Pip diff: `{pip_diff}`)\n"
        f"💸 Risk: `${dollar_risk:.2f}`\n"
        f"📦 *Lot Size*: `{lot_size:.4f}`",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /setbalance and /setrisk, then paste your signal.")

def main():
    bot_token = "7381167194:AAHhjKr0NmL1FXHu2WdJgrzxHYaZ5ChfFZc"
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setbalance", set_balance))
    app.add_handler(CommandHandler("setrisk", set_risk))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_signal))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
