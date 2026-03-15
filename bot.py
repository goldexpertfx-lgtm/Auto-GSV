import telebot

# --- SETTINGS ---
API_TOKEN = '8284715892:AAE-rjrQovkKdI9HdxozsejhqKXfoy8BZRE'
ADMIN_ID = 5072932186  # Yahan apni real Telegram ID likhein (Numeric)

bot = telebot.TeleBot(API_TOKEN)

# 1. Start Command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome! Bot active hai.")

# 2. Mailing Option (Sirf Admin ke liye)
@bot.message_handler(commands=['mailing'])
def mailing_start(message):
    # Security Check: Kya message bhejne wala Admin hai?
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "✅ Admin Verified. Mailing ke liye message likhein:")
        bot.register_next_step_handler(msg, send_to_all_users)
    else:
        bot.reply_to(message, "❌ Access Denied! Ye option sirf Admin ke liye hai.")

def send_to_all_users(message):
    # Yahan aapki user list honi chahiye (Database ya List se)
    # Demo ke liye hum ek list use kar rahe hain
    user_list = [123456789, 987654321] # Sab users ki IDs yahan honi chahiye

    count = 0
    for user in user_list:
        try:
            bot.send_message(user, message.text)
            count += 1
        except Exception as e:
            print(f"User {user} ko message nahi gaya: {e}")

    bot.send_message(ADMIN_ID, f"📢 Broadcast finished! {count} users ko message mil gaya.")

print("Bot is running...")
bot.polling()
