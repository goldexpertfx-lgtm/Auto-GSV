import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
TOKEN = os.environ.get("BOT_TOKEN")
PARTNER_LINK = "https://www.brokeraccountguide.com/"
SUPPORT_LINK = "https://t.me/MuhammadPrince7"
ADMIN_ID = 5072932186  # <--- REPLACE THIS WITH YOUR NUMERIC TELEGRAM ID

# Temporary storage for mailing
pending_mail = {}

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

    # Inline buttons
    inline_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🆕 New Here", callback_data='new_here')],
        [InlineKeyboardButton("🔄 Old Here", callback_data='old_here')],
        [InlineKeyboardButton("🌐 Website User", callback_data='from_website')]
    ])

    # Show Admin Keyboard only to Admin
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

# ===== MAILING LOGIC =====
async def mailing_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("Please send the TEXT for your mailing:")
    return 1 # Setting a simple state logic

async def process_mailing_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    context.user_data['mail_text'] = update.message.text
    context.user_data['mail_link'] = None
    context.user_data['mail_link_text'] = None
    
    await show_mailing_menu(update)

async def show_mailing_menu(update):
    keyboard = [
        [InlineKeyboardButton("🔗 Add Link", callback_data="admin_add_link")],
        [InlineKeyboardButton("👁️ Preview", callback_data="admin_preview")],
        [InlineKeyboardButton("✅ Send Now", callback_data="admin_send")],
        [InlineKeyboardButton("❌ Cancel", callback_data="admin_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Mailing Options:", reply_markup=reply_markup)

# ===== BUTTON HANDLER (Updated) =====
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "start_again":
        await start(update, context, from_callback=True)
    
    # --- Admin Mailing Actions ---
    elif data == "admin_preview":
        text = context.user_data.get('mail_text')
        link = context.user_data.get('mail_link')
        markup = None
        if link:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton(context.user_data['mail_link_text'], url=link)]])
        await query.message.reply_text(f"--- PREVIEW ---\n\n{text}", reply_markup=markup)
        
    elif data == "admin_add_link":
        await query.message.reply_text("Send Link + Title in 2 lines:\nExample:\nJoin VIP\nhttps://t.me/link")
        context.user_data['awaiting_link'] = True

    elif data == "admin_send":
        # Note: You need a list of user IDs. For now, it sends to you as a test.
        target_users = [ADMIN_ID] 
        text = context.user_data.get('mail_text')
        link = context.user_data.get('mail_link')
        markup = None
        if link:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton(context.user_data['mail_link_text'], url=link)]])
        
        count = 0
        for uid in target_users:
            try:
                await context.bot.send_message(chat_id=uid, text=text, reply_markup=markup)
                count += 1
            except: pass
        await query.message.reply_text(f"✅ Sent to {count} users.")

    # --- Existing user buttons ---
    elif data == "new_here":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Join Now", url=PARTNER_LINK)],[InlineKeyboardButton("🔙 Back", callback_data="start_again")]])
        await query.edit_message_text(f"To get VIP access, please register below.", reply_markup=kb)
    
    elif data == "from_website":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Registered", callback_data="registered")],[InlineKeyboardButton("🔙 Back", callback_data="start_again")]])
        await query.edit_message_text("Please select your status:", reply_markup=kb)

# ===== MESSAGE HANDLER (Updated) =====
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # 1. Check if Admin clicked Mailing Button
    if text == "📢 Mailing" and user_id == ADMIN_ID:
        await update.message.reply_text("Enter message text:")
        context.user_data['is_mailing'] = True
        return

    # 2. If Admin is typing mailing details
    if user_id == ADMIN_ID and context.user_data.get('is_mailing'):
        context.user_data['mail_text'] = text
        context.user_data['is_mailing'] = False
        await show_mailing_menu(update)
        return

    # 3. If Admin is adding a link
    if user_id == ADMIN_ID and context.user_data.get('awaiting_link'):
        lines = text.split('\n')
        if len(lines) >= 2:
            context.user_data['mail_link_text'] = lines[0]
            context.user_data['mail_link'] = lines[1]
            await update.message.reply_text("✅ Link set!")
        context.user_data['awaiting_link'] = False
        await show_mailing_menu(update)
        return

    # Default message response
    await update.message.reply_text(f"✅ **Received!**\n\nDetail: `{text}`\n\nTeam will verify shortly.")

# ===== MAIN APPLICATION =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
    
