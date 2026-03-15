import telebot
from telebot import types

# --- SETTINGS ---
API_TOKEN = '8284715892:AAE-rjrQovkKdI9HdxozsejhqKXfoy8BZRE'
ADMIN_ID = 5072932186  # Apni ID check kar ke likhein

bot = telebot.TeleBot(API_TOKEN)

# 1. Start Command with Admin Keyboard
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Check agar user admin hai to usay button dikhao
    if message.from_user.id == ADMIN_ID:
        btn1 = types.KeyboardButton('📢 Mailing')
        markup.add(btn1)
        bot.send_message(message.chat.id, "Welcome Admin! Mailing option niche keyboard mein hai.", reply_markup=markup)
    else:
        # Aam user ke liye normal message (koi button nahi)
        bot.send_message(message.chat.id, "Welcome! Bot active hai.", reply_markup=types.ReplyKeyboardRemove())

# 2. Button Press Handler
@bot.message_handler(func=lambda message: message.text == '📢 Mailing')
def mailing_button_pressed(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "✅ Mailing Mode Active. Apna message likhein:")
        bot.register_next_step_handler(msg, send_to_all_users)
    else:
        bot.reply_to(message, "❌ Access Denied!")

def send_to_all_users(message):
    # Filhal ye demo list hai, yahan user IDs honi chahiye
    user_list = [ADMIN_ID] 
    
    count = 0
    for user in user_list:
        try:
            bot.send_message(user, message.text)
            count += 1
        except:
            pass
    
    bot.send_message(ADMIN_ID, f"📢 Broadcast finished! {count} users ko bhej diya gaya.")

print("Bot is running...")
bot.polling()
