import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)

products = {
    "1": {
        "name": "ANTO X CHEATS",
        "price": "1000৳",
        "delivery": "Here is your VIP link: https://example.com"
    }
}

pending = {}

@bot.message_handler(commands=['start'])
def start(msg):
    markup = InlineKeyboardMarkup()
    for pid, p in products.items():
        markup.add(InlineKeyboardButton(f"{p['name']} - {p['price']}", callback_data=f"buy_{pid}"))
    
    bot.send_message(msg.chat.id, "🔥 Welcome! Select Product:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy(call):
    pid = call.data.split("_")[1]
    pending[call.message.chat.id] = pid
    
    bot.send_message(call.message.chat.id,
        "💰 Send money to bKash: 01918591988\nSend TRX ID after payment."
    )

@bot.message_handler(func=lambda m: m.chat.id in pending)
def handle_trx(msg):
    pid = pending[msg.chat.id]
    trx = msg.text

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{msg.chat.id}_{pid}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{msg.chat.id}")
    )

    bot.send_message(ADMIN_ID,
        f"New Payment\nUser: {msg.chat.id}\nTRX: {trx}",
        reply_markup=markup
    )

    bot.reply_to(msg, "⏳ Wait for admin approval.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve(call):
    if call.message.chat.id != ADMIN_ID:
        return

    _, user_id, pid = call.data.split("_")
    user_id = int(user_id)

    bot.send_message(user_id, "✅ Payment Approved! Here is your product.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject(call):
    if call.message.chat.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])
    bot.send_message(user_id, "❌ Payment Rejected.")

print("Bot running...")
bot.infinity_polling()
