import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
TOKEN = os.environ.get("BOT_TOKEN")
PARTNER_LINK = "https://www.brokeraccountguide.com/"
SUPPORT_LINK = "https://t.me/MuhammadPrince7"
ADMIN_ID = 123456789  # <--- Replace with your numeric Telegram ID

# ===== START FUNCTION =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback=False):
    user = update.callback_query.from_user if from_callback else update.message.from_user
    first_name = user.first_name or "Trader"

    welcome_text = (
        f"**𝗛𝗲𝘆, {first_name}!**\n\n"
        "👋 **Welcome to Broker Account Guide Bot!**\n\n"
        "Unlock your trading benefits:\n"
        "📊 **Premium XAUUSD (Gold) Signals**\n"
        "🎁 **Exclusive Gifts & Giveaways**\n"
        "💎 **VIP Trading Access & Community**\n\n"
        "Please choose an option below:"
    )

    inline_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🆕 New Here", callback_data='new_here')],
        [InlineKeyboardButton("🔄 Old Here", callback_data='old_here')],
        [InlineKeyboardButton("🌐 Website User", callback_data='from_website')]
    ])

    # Show Mailing Button only to Admin
    reply_markup = None
    if user.id == ADMIN_ID:
        admin_kb = [[KeyboardButton("📢 Mailing")]]
        reply_markup = ReplyKeyboardMarkup(admin_kb, resize_keyboard=True)

    if from_callback:
        await update.callback_query.edit_message_text(text=welcome_text, reply_markup=inline_kb, parse_mode="Markdown")
    else:
        await update.message.reply_text(text=welcome_text, reply_markup=inline_kb, parse_mode="Markdown")
        if reply_markup:
            await update.message.reply_text("Admin Tools Enabled:", reply_markup=reply_markup)

# ===== MAILING SYSTEM =====
async def show_mailing_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("🔗 Add Link", callback_data="adm_link")],
        [InlineKeyboardButton("👁️ Preview", callback_data="adm_prev")],
        [InlineKeyboardButton("✅ Send Now", callback_data="adm_send")],
        [InlineKeyboardButton("❌ Cancel", callback_data="adm_stop")]
    ]
    await update.message.reply_text("Mailing Options:", reply_markup=InlineKeyboardMarkup(keyboard))

# ===== BUTTON HANDLER =====
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "start_again":
        await start(update, context, from_callback=True)
    
    # --- Admin Callbacks ---
    elif data == "adm_prev":
        text = context.user_data.get('m_text')
        link = context.user_data.get('m_url')
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(context.user_data['m_btn'], url=link)]]) if link else None
        await query.message.reply_text(f"--- PREVIEW ---\n\n{text}", reply_markup=kb)

    elif data == "adm_link":
        await query.message.reply_text("Send Link + Title in 2 lines:\nExample:\nJoin VIP\nhttps://t.me/link")
        context.user_data['state'] = 'link'

    elif data == "adm_send":
        # For now, it sends to you. You need a list/DB for all users.
        target_users = [ADMIN_ID] 
        text = context.user_data.get('m_text')
        link = context.user_data.get('m_url')
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(context.user_data['m_btn'], url=link)]]) if link else None
        
        for uid in target_users:
            try: await context.bot.send_message(chat_id=uid, text=text, reply_markup=kb)
            except: pass
        await query.message.reply_text("🚀 Broadcast Sent!")

    # --- Existing user buttons ---
    elif data == "new_here":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Join Now", url=PARTNER_LINK)], [InlineKeyboardButton("🔙 Back", callback_data="start_again")]])
        await query.edit_message_text("Register using the link below for VIP access.", reply_markup=kb)

# ===== MESSAGE HANDLER =====
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if text == "📢 Mailing" and user_id == ADMIN_ID:
        await update.message.reply_text("Please enter your message text:")
        context.user_data['state'] = 'text'
        return

    state = context.user_data.get('state')
    if user_id == ADMIN_ID and state == 'text':
        context.user_data['m_text'] = text
        context.user_data['state'] = None
        await show_mailing_menu(update, context)
    elif user_id == ADMIN_ID and state == 'link':
        lines = text.split('\n')
        if len(lines) >= 2:
            context.user_data['m_btn'], context.user_data['m_url'] = lines[0], lines[1]
            await update.message.reply_text("✅ Link added!")
        context.user_data['state'] = None
        await show_mailing_menu(update, context)
    else:
        await update.message.reply_text(f"✅ **Received!**\n\nDetail: `{text}`\n\nVerification in progress.")

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
    
