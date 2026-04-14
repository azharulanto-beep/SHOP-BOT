import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

bot = telebot.TeleBot(TOKEN)

# 🖼️ LOGO
LOGO = "https://i.postimg.cc/ZnTLxtW2/logo.jpg"

# ================= 10 SLOT PRODUCTS =================
products = {
    "1": {"DRIP CLINT": "", "7 DAYS 400\n10 DAYS\n30 DAYS 1500": "0", "bkash": "", "keys": [], "link": ""},
    "2": {"name": "Empty", "price": "0", "bkash": "", "keys": [], "link": ""},
    "3": {"name": "Empty", "price": "0", "bkash": "", "keys": [], "link": ""},
    "4": {"name": "Empty", "price": "0", "bkash": "", "keys": [], "link": ""},
    "5": {"name": "Empty", "price": "0", "bkash": "", "keys": [], "link": ""},
    "6": {"name": "Empty", "price": "0", "bkash": "", "keys": [], "link": ""},
    "7": {"name": "Empty", "price": "0", "bkash": "", "keys": [], "link": ""},
    "8": {"name": "Empty", "price": "0", "bkash": "", "keys": [], "link": ""},
    "9": {"name": "Empty", "price": "0", "bkash": "", "keys": [], "link": ""},
    "10": {"name": "Empty", "price": "0", "bkash": "", "keys": [], "link": ""}
}

pending = {}

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):
    markup = InlineKeyboardMarkup(row_width=1)

    for pid, p in products.items():
        if p["name"] != "Empty":
            markup.add(InlineKeyboardButton(
                f"{p['name']} - {p['price']} | Stock:{len(p['keys'])}",
                callback_data=f"buy_{pid}"
            ))

    bot.send_photo(
        msg.chat.id,
        LOGO,
        caption="🔥 WELCOME TO ANTO SHOP\nSelect product below:",
        reply_markup=markup
    )

# ================= BUY =================
@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(call):
    pid = call.data.split("_")[1]
    p = products[pid]

    pending[call.message.chat.id] = {"pid": pid}

    bot.send_message(
        call.message.chat.id,
        f"💰 PAYMENT PAGE\n\n"
        f"📦 Product: {p['name']}\n"
        f"💵 Price: {p['price']}\n"
        f"📱 bKash: {p['01918591988']}\n\n"
        "👉 Pay first\n👉 Send TRX\n👉 Send Screenshot"
    )

# ================= VERIFY =================
@bot.message_handler(content_types=['text', 'photo'])
def verify(msg):
    if msg.chat.id not in pending:
        return

    data = pending[msg.chat.id]
    pid = data["pid"]

    if msg.content_type == "text":
        data["trx"] = msg.text
        pending[msg.chat.id] = data
        bot.reply_to(msg, "📸 এখন Screenshot পাঠাও")
        return

    if msg.content_type == "photo":
        bot.send_photo(
            ADMIN_ID,
            msg.photo[-1].file_id,
            caption=(
                "🆕 ORDER\n\n"
                f"User: {msg.chat.id}\n"
                f"Product: {products[pid]['name']}\n"
                f"TRX: {data.get('trx')}"
            ),
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{msg.chat.id}_{pid}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{msg.chat.id}")
            )
        )

        bot.send_message(msg.chat.id, "⏳ Sent to admin")
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
        bot.send_message(ADMIN_ID, "❌ No stock!")
        return

    key = product["keys"].pop(0)

    bot.send_message(
        uid,
        f"✅ APPROVED\n\n🔑 KEY: {key}\n📥 LINK: {product['link']}"
    )

    bot.edit_message_caption("APPROVED", call.message.chat.id, call.message.message_id)

# ================= REJECT =================
@bot.callback_query_handler(func=lambda c: c.data.startswith("reject_"))
def reject(call):
    if call.from_user.id != ADMIN_ID:
        return

    uid = int(call.data.split("_")[1])
    bot.send_message(uid, "❌ Rejected")

    bot.edit_message_caption("REJECTED", call.message.chat.id, call.message.message_id)

# ================= OWNER PANEL =================
@bot.message_handler(commands=['owner'])
def owner(msg):
    if msg.chat.id != ADMIN_ID:
        return

    bot.send_message(
        msg.chat.id,
        "👑 OWNER PANEL\n\n"
        "/add slot|name|price|bkash|link\n"
        "/addkey slot|KEY\n"
        "/remove slot\n"
        "/show"
    )

# ================= ADD PRODUCT =================
@bot.message_handler(commands=['add'])
def add(msg):
    if msg.chat.id != ADMIN_ID:
        return

    try:
        _, data = msg.text.split(" ", 1)
        slot, name, price, bkash, link = data.split("|")

        products[slot] = {
            "name": name,
            "price": price,
            "bkash": bkash,
            "link": link,
            "keys": []
        }

        bot.reply_to(msg, f"✅ Added Slot {slot}")

    except:
        bot.reply_to(msg, "❌ /add slot|name|price|bkash|link")

# ================= ADD KEY =================
@bot.message_handler(commands=['addkey'])
def addkey(msg):
    if msg.chat.id != ADMIN_ID:
        return

    try:
        _, data = msg.text.split(" ", 1)
        slot, key = data.split("|")

        products[slot]["keys"].append(key)

        bot.reply_to(msg, "✅ Key Added")

    except:
        bot.reply_to(msg, "❌ /addkey slot|KEY")

# ================= REMOVE =================
@bot.message_handler(commands=['remove'])
def remove(msg):
    if msg.chat.id != ADMIN_ID:
        return

    try:
        _, slot = msg.text.split()
        products[slot] = {"name": "Empty", "price": "0", "bkash": "", "keys": [], "link": ""}
        bot.reply_to(msg, "🗑️ Removed")
    except:
        bot.reply_to(msg, "❌ /remove 1")

# ================= SHOW =================
@bot.message_handler(commands=['show'])
def show(msg):
    if msg.chat.id != ADMIN_ID:
        return

    text = "📦 PRODUCTS\n\n"
    for k, v in products.items():
        text += f"{k}. {v['name']} | Keys: {len(v['keys'])}\n"

    bot.send_message(msg.chat.id, text)

# ================= RUN =================
print("🔥 BOT RUNNING...")
bot.infinity_polling()
