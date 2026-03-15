import telebot
from telebot import types

# --- SETTINGS ---
API_TOKEN = '8284715892:AAE-rjrQovkKdI9HdxozsejhqKXfoy8BZRE'
ADMIN_ID = 5072932186  # Replace with your numeric Telegram ID

bot = telebot.TeleBot(API_TOKEN)

# Temporary storage for mailing data
pending_mail = {}

# 1. Start Command
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.from_user.id == ADMIN_ID:
        markup.add(types.KeyboardButton('📢 Mailing'))
        bot.send_message(message.chat.id, "Welcome Admin! Access the mailing tool below.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Welcome! The bot is active.", reply_markup=types.ReplyKeyboardRemove())

# 2. Mailing Button Initiation
@bot.message_handler(func=lambda message: message.text == '📢 Mailing')
def mailing_init(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "Please enter the text for your broadcast:")
        bot.register_next_step_handler(msg, process_mailing_text)
    else:
        bot.reply_to(message, "❌ Access Denied.")

def process_mailing_text(message):
    if message.text == 'Cancel': return
    
    # Store the text temporarily
    pending_mail[ADMIN_ID] = {"text": message.text, "link": None, "link_text": None}
    show_mailing_menu(message.chat.id)

def show_mailing_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🔗 Add Link", callback_data="add_link"))
    markup.row(types.InlineKeyboardButton("👁️ Preview", callback_data="preview_mail"))
    markup.row(types.InlineKeyboardButton("✅ Send to All", callback_data="send_now"))
    markup.row(types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_mail"))
    
    bot.send_message(chat_id, "Mailing Options:", reply_markup=markup)

# 3. Callback Handlers for Menu
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "preview_mail":
        data = pending_mail.get(ADMIN_ID)
        markup = types.InlineKeyboardMarkup()
        if data["link"]:
            markup.add(types.InlineKeyboardButton(data["link_text"], url=data["link"]))
        
        bot.send_message(call.message.chat.id, f"--- PREVIEW ---\n\n{data['text']}", reply_markup=markup)
        show_mailing_menu(call.message.chat.id)

    elif call.data == "add_link":
        msg = bot.send_message(call.message.chat.id, "Send link and title in 2 lines:\nExample:\nJoin VIP\nhttps://t.me/yourlink")
        bot.register_next_step_handler(msg, process_link)

    elif call.data == "send_now":
        data = pending_mail.get(ADMIN_ID)
        # Add your list of user IDs here
        user_list = [ADMIN_ID] # In production, pull this from a database
        
        count = 0
        markup = types.InlineKeyboardMarkup()
        if data["link"]:
            markup.add(types.InlineKeyboardButton(data["link_text"], url=data["link"]))

        for user in user_list:
            try:
                bot.send_message(user, data["text"], reply_markup=markup)
                count += 1
            except:
                pass
        
        bot.send_message(ADMIN_ID, f"🚀 Broadcast Finished! Sent to {count} users.")

def process_link(message):
    lines = message.text.split('\n')
    if len(lines) >= 2:
        pending_mail[ADMIN_ID]["link_text"] = lines[0]
        pending_mail[ADMIN_ID]["link"] = lines[1]
        bot.send_message(message.chat.id, "✅ Link Added!")
    else:
        bot.send_message(message.chat.id, "❌ Invalid format. Link not added.")
    
    show_mailing_menu(message.chat.id)

print("Bot started...")
bot.polling()
    
