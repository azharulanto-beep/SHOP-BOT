import telebot
import os

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "✅ ANTO SHOP BOT IS RUNNING!")

print("🔥 BOT STARTED!")
bot.infinity_polling() 
