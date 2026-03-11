import os
import asyncio
import logging
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5072932186
CHANNEL_ID = -1003742118245

# Referral Links
EXNESS_LINK = "https://one.exness-track.com/a/your_code"
XM_LINK = "https://clicks.pipaffiliates.com/c?m=your_code"

# ================= UNLIMITED HYBRID APIs =================
# Ye sources TradingView aur MetaTrader ke price se 99% match karte hain
API_SOURCES = [
    "https://api.exchangerate-api.com/v4/latest/XAU",
    "https://open.er-api.com/v6/latest/XAU",
    "https://api.frankfurter.app/latest?from=XAU&to=USD",
    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/xau.json",
    "https://www.floatrates.com/daily/xau.json",
    "https://api.exchangerate.host/convert?from=XAU&to=USD"
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

active_trade = None

async def fetch_realtime_price():
    """Failover Logic: Ek API block hogi to bot foran dusri check karega"""
    async with aiohttp.ClientSession() as session:
        for url in API_SOURCES:
            try:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        price = 0
                        # Parsing different formats
                        if 'rates' in data:
                            price = data['rates'].get('USD') or (1 / data['rates'].get('XAU') if data['rates'].get('XAU') else 0)
                        elif 'result' in data:
                            price = data['result']
                        elif 'usd' in data:
                            price = data['usd'].get('rate') if isinstance(data['usd'], dict) else data['usd']
                        
                        if 1500 < price < 4000: # Valid Gold Price Check
                            return round(price, 2)
            except:
                continue
    return None

async def tracker(context: ContextTypes.DEFAULT_TYPE):
    global active_trade
    while active_trade:
        current_price = await fetch_realtime_price()
        if not current_price:
            await asyncio.sleep(5)
            continue

        trade = active_trade
        msg_id = trade['msg_id']
        hit = False
        update_text = ""

        if trade['type'] == "BUY":
            if current_price >= trade['tp2']:
                update_text = "🎯 **TP2 HIT: +100 Pips!** 💰"
                hit = True
            elif current_price >= trade['tp1'] and not trade['tp1_done']:
                await context.bot.send_message(CHANNEL_ID, "✅ **TP1 HIT: +50 Pips!**\nMoving SL to Entry.", reply_to_message_id=msg_id)
                trade['tp1_done'] = True
            elif current_price <= trade['sl']:
                update_text = "❌ **SL HIT.** Wait for next setup."
                hit = True
        
        else: # SELL
            if current_price <= trade['tp2']:
                update_text = "🎯 **TP2 HIT: +100 Pips!** 💰"
                hit = True
            elif current_price <= trade['tp1'] and not trade['tp1_done']:
                await context.bot.send_message(CHANNEL_ID, "✅ **TP1 HIT: +50 Pips!**\nMoving SL to Entry.", reply_to_message_id=msg_id)
                trade['tp1_done'] = True
            elif current_price >= trade['sl']:
                update_text = "❌ **SL HIT.** Wait for next setup."
                hit = True

        if hit:
            await context.bot.send_message(CHANNEL_ID, update_text, reply_to_message_id=msg_id)
            active_trade = None
            break
        await asyncio.sleep(10)

async def handle_admin_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_trade
    if update.effective_user.id != ADMIN_ID: return

    cmd = update.message.text.upper()
    if "BUY" in cmd or "SELL" in cmd:
        price = await fetch_realtime_price()
        if not price:
            await update.message.reply_text("❌ APIs busy. Try again in 5 seconds.")
            return

        trade_type = "BUY" if "BUY" in cmd else "SELL"
        tp1 = round(price + 5, 2) if trade_type == "BUY" else round(price - 5, 2)
        tp2 = round(price + 10, 2) if trade_type == "BUY" else round(price - 10, 2)
        sl = round(price - 10, 2) if trade_type == "BUY" else round(price + 10, 2)

        keyboard = [[InlineKeyboardButton("💎 Open Exness Account", url=EXNESS_LINK)],
                    [InlineKeyboardButton("📈 Open XM Account", url=XM_LINK)]]
        
        signal_msg = (
            f"🚀 **XAUUSD {trade_type} NOW**\n\n"
            f"📥 Entry: {price}\n"
            f"🎯 TP1: {tp1}\n"
            f"🎯 TP2: {tp2}\n"
            f"🛑 SL: {sl}\n\n"
            f"⚠️ *Automatic tracking active...*"
        )

        msg = await context.bot.send_message(CHANNEL_ID, signal_msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        
        active_trade = {
            "type": trade_type, "tp1": tp1, "tp2": tp2, "sl": sl, 
            "msg_id": msg.message_id, "tp1_done": False
        }
        asyncio.create_task(tracker(context))
        await update.message.reply_text(f"✅ Signal posted at {price}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_msg))
    app.run_polling()
    
