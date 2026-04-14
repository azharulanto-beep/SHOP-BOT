import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# ================= CONFIG =================
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

bot = telebot.TeleBot(TOKEN)

# 🖼️ LOGO (working direct image link)
LOGO = "https://i.postimg.cc/ZnTLxtW2/logo.jpg"

# ================= PRODUCTS =================
products = {
    "1": {
        "name": "VIP Key",
        "price": "100৳",
        "keys": ["KEY123", "KEY456", "KEY789"],
        "link": "https://example.com/download"
    },
    "2": {
        "name": "Premium Access",
        "price": "200৳",
        "keys": ["PREM111", "PREM222"],
        "link": "https://example.com/download2"
    }
}

# pending orders
pending = {}

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):
    markup = InlineKeyboardMarkup(row_width=1)

    for pid, p in products.items():
        markup.add(InlineKeyboardButton(
            f"{p['name']} - {p['price']} | Stock: {len(p['keys'])}",
            callback_data=f"buy_{pid}"
        ))

    markup.add(
        InlineKeyboardButton("📞 Owner", callback_data="owner"),
        InlineKeyboardButton("📢 Channels", callback_data="channels"),
        InlineKeyboardButton("❓ Help", callback_data="help")
    )

    bot.send_photo(
        msg.chat.id,
        LOGO,
        caption="🔥 WELCOME TO PREMIUM SHOP BOT\nSelect your product below:",
        reply_markup=markup
    )

# ================= BUY =================
@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(call):
    pid = call.data.split("_")[1]

    pending[call.message.chat.id] = {
        "pid": pid,
        "trx": None
    }

    bot.send_message(
        call.message.chat.id,
        "💰 PAYMENT INSTRUCTION\n\n"
        "👉 Send bKash payment\n"
        "👉 Then send TRX ID\n"
        "👉 Then send screenshot\n\n"
        "⚠️ TRX + Screenshot required!"
    )

# ================= PAYMENT VERIFY =================
@bot.message_handler(content_types=['text', 'photo'])
def verify(msg):
    if msg.chat.id not in pending:
        return

    data = pending[msg.chat.id]
    pid = data["pid"]

    # STEP 1: TRX ID
    if msg.content_type == "text":
        data["trx"] = msg.text
        pending[msg.chat.id] = data
        bot.reply_to(msg, "📸 এখন Payment Screenshot পাঠাও")
        return

    # STEP 2: SCREENSHOT -> SEND ADMIN
    if msg.content_type == "photo":
        trx = data.get("trx", "NOT PROVIDED")

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{msg.chat.id}_{pid}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{msg.chat.id}")
        )

        bot.send_photo(
            ADMIN_ID,
            msg.photo[-1].file_id,
            caption=(
                "🆕 NEW PAYMENT REQUEST\n\n"
                f"👤 User: {msg.chat.id}\n"
                f"🧾 TRX: {trx}\n"
                f"📦 Product ID: {pid}\n\n"
                "⚠️ Verify carefully!"
            ),
            reply_markup=markup
        )

        bot.send_message(msg.chat.id, "⏳ Payment sent to admin")
        del pending[msg.chat.id]

# ================= APPROVE =================
@bot.callback_query_handler(func=lambda c: c.data.startswith("approve_"))
def approve(call):
    if call.from_user.id != ADMIN_ID:
        return

    _, uid, pid = call.data.split("_")
    uid = int(uid)

    product = products[pid]

    if len(product["keys"]) == 0:
        bot.send_message(ADMIN_ID, "❌ No stock left!")
        return

    key = product["keys"].pop(0)

    bot.send_message(
        uid,
        "✅ PAYMENT APPROVED\n\n"
        f"🔑 YOUR KEY: {key}\n"
        f"📥 DOWNLOAD: {product['link']}\n\n"
        "🎉 Thanks for purchase!"
    )

    bot.edit_message_caption(
        "✅ APPROVED & DELIVERED",
        call.message.chat.id,
        call.message.message_id
    )

# ================= REJECT =================
@bot.callback_query_handler(func=lambda c: c.data.startswith("reject_"))
def reject(call):
    if call.from_user.id != ADMIN_ID:
        return

    uid = int(call.data.split("_")[1])

    bot.send_message(uid, "❌ Payment rejected. Try again.")

    bot.edit_message_caption(
        "❌ REJECTED",
        call.message.chat.id,
        call.message.message_id
    )

# ================= HELP =================
@bot.callback_query_handler(func=lambda c: c.data == "help")
def help_menu(call):
    bot.send_message(call.message.chat.id,
        "📌 HELP MENU\n\n"
        "/start - Open shop\n"
        "/stock - Check stock\n"
        "/addkey - Add keys (admin)\n"
    )

# ================= OWNER =================
@bot.callback_query_handler(func=lambda c: c.data == "owner")
def owner(call):
    bot.send_message(call.message.chat.id, "👤 Owner: @yourusername")

# ================= CHANNELS =================
@bot.callback_query_handler(func=lambda c: c.data == "channels")
def channels(call):
    bot.send_message(call.message.chat.id, "📢 @channel1\n@channel2")

# ================= STOCK =================
@bot.message_handler(commands=['stock'])
def stock(msg):
    if msg.chat.id != ADMIN_ID:
        return

    text = "📦 STOCK REPORT\n\n"
    for pid, p in products.items():
        text += f"{p['name']} → {len(p['keys'])} keys\n"

    bot.send_message(msg.chat.id, text)

# ================= ADD KEY =================
@bot.message_handler(commands=['addkey'])
def addkey(msg):
    if msg.chat.id != ADMIN_ID:
        return

    try:
        _, pid, key = msg.text.split()
        products[pid]["keys"].append(key)
        bot.reply_to(msg, "✅ Key Added")
    except:
        bot.reply_to(msg, "❌ Use: /addkey 1 KEY123")

# ================= RUN =================
print("🔥 Bot Running...")
bot.infinity_polling()
