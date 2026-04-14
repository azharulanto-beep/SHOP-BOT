import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

bot = telebot.TeleBot(TOKEN)

# 🔑 Product + Key Stock System
products = {
    "1": {
        "name": "VIP Key",
        "price": "100৳",
        "keys": ["KEY123", "KEY456", "KEY789"],
        "link": "https://www.mediafire.com/file/example"
    },
    "2": {
        "name": "Premium Access",
        "price": "200৳",
        "keys": ["PREM111", "PREM222"],
        "link": "https://www.mediafire.com/file/example2"
    }
}

pending = {}

# 🚀 Start UI
@bot.message_handler(commands=['start'])
def start(msg):
    markup = InlineKeyboardMarkup(row_width=2)

    for pid, p in products.items():
        markup.add(InlineKeyboardButton(f"{p['name']} - {p['price']}", callback_data=f"buy_{pid}"))

    markup.add(
        InlineKeyboardButton("📞 Owner", callback_data="owner"),
        InlineKeyboardButton("📢 Channels", callback_data="channels")
    )

    bot.send_message(msg.chat.id, "🔥 Welcome to Premium Shop!\nSelect Product:", reply_markup=markup)

# 🛒 Buy System
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy(call):
    pid = call.data.split("_")[1]
    pending[call.message.chat.id] = pid

    bot.send_message(call.message.chat.id,
        "💰 Send payment to bKash: 01XXXXXXXXX\n\nSend TRX ID after payment."
    )

# 📩 TRX Handle
@bot.message_handler(func=lambda m: m.chat.id in pending)
def trx(msg):
    pid = pending[msg.chat.id]
    trx = msg.text

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{msg.chat.id}_{pid}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{msg.chat.id}")
    )

    bot.send_message(ADMIN_ID,
        f"🆕 Payment Request\nUser: {msg.chat.id}\nTRX: {trx}",
        reply_markup=markup
    )

    bot.reply_to(msg, "⏳ Waiting for admin approval...")

# ✅ Approve → Auto Key Send
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve(call):
    if call.message.chat.id != ADMIN_ID:
        return

    _, user_id, pid = call.data.split("_")
    user_id = int(user_id)

    product = products[pid]

    if len(product["keys"]) == 0:
        bot.send_message(call.message.chat.id, "❌ No keys left!")
        return

    key = product["keys"].pop(0)  # 🔑 auto take key

    bot.send_message(user_id,
        f"✅ Payment Approved!\n\n🔑 Your Key: {key}\n📥 Download: {product['link']}"
    )

    bot.edit_message_text("✅ Delivered", call.message.chat.id, call.message.message_id)

# ❌ Reject
@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject(call):
    if call.message.chat.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])
    bot.send_message(user_id, "❌ Payment Rejected.")

# 📞 Owner
@bot.callback_query_handler(func=lambda call: call.data == "owner")
def owner(call):
    bot.send_message(call.message.chat.id, "👤 Contact Owner: @yourusername")

# 📢 Channels
@bot.callback_query_handler(func=lambda call: call.data == "channels")
def channels(call):
    bot.send_message(call.message.chat.id, "📢 Join Channels:\n@channel1\n@channel2")

# 📘 Help
@bot.message_handler(commands=['help'])
def help_cmd(msg):
    bot.reply_to(msg, "Use /start to buy products.\nContact admin if problem.")

# 👑 Admin Panel (Add Keys)
@bot.message_handler(commands=['admin'])
def admin(msg):
    if msg.chat.id == ADMIN_ID:
        bot.send_message(msg.chat.id, "👑 Admin Panel\nSend:\n/addkey product_id KEY")

# ➕ Add Key Command
@bot.message_handler(commands=['addkey'])
def addkey(msg):
    if msg.chat.id != ADMIN_ID:
        return

    try:
        _, pid, key = msg.text.split()
        products[pid]["keys"].append(key)
        bot.reply_to(msg, "✅ Key Added")
    except:
        bot.reply_to(msg, "❌ Format: /addkey 1 KEY123")

print("🔥 Bot Running...")
bot.infinity_polling()
