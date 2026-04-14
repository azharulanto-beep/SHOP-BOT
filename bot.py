import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# ================= CONFIG =================
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

bot = telebot.TeleBot(TOKEN)

# 🖼️ LOGO (your file_id)
LOGO = "AgACAgUAAxkBAAEC7zxp3n2Zl-IgVzpJzsyLsHOpQzV8pwACGw5rG76O8VYFRrDhfmA49QEAAwIAA3MAAzsE"

# ================= PRODUCTS =================
products = {
    "1": {
        "name": "VIP Key",
        "price": "100৳",
        "keys": ["KEY123", "KEY456", "KEY789"],
        "link": "https://mediafire.com/file/example"
    },
    "2": {
        "name": "Premium Access",
        "price": "200৳",
        "keys": ["PREM111", "PREM222"],
        "link": "https://mediafire.com/file/example2"
    }
}

# pending = user_id -> {"pid": "", "trx": ""}
pending = {}

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):
    markup = InlineKeyboardMarkup(row_width=2)

    for pid, p in products.items():
        markup.add(InlineKeyboardButton(
            f"{p['name']} - {p['price']} | Stock:{len(p['keys'])}",
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
        caption="🔥 WELCOME TO PREMIUM SHOP\n\nSelect your product below:",
        reply_markup=markup
    )

# ================= BUY =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy(call):
    pid = call.data.split("_")[1]

    pending[call.message.chat.id] = {
        "pid": pid,
        "step": "trx"
    }

    bot.send_message(
        call.message.chat.id,
        "💰 PAYMENT INSTRUCTION\n\n"
        "👉 Send bKash Payment\n"
        "👉 Then send TRX ID\n"
        "👉 Then send PAYMENT SCREENSHOT\n\n"
        "⚠️ Both TRX + Screenshot required for approval!"
    )

# ================= PAYMENT VERIFY (TRX + SCREENSHOT) =================
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

        bot.reply_to(msg, "📸 এখন আপনার Payment Screenshot পাঠান")
        return

    # STEP 2: SCREENSHOT -> SEND TO ADMIN
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
                "🆕 PAYMENT REQUEST\n\n"
                f"👤 User: {msg.chat.id}\n"
                f"🧾 TRX: {trx}\n"
                f"📦 Product ID: {pid}\n\n"
                "⚠️ Verify carefully before approve"
            ),
            reply_markup=markup
        )

        bot.send_message(msg.chat.id, "⏳ Payment under review...")
        del pending[msg.chat.id]

# ================= APPROVE =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve(call):
    if call.from_user.id != ADMIN_ID:
        return

    _, uid, pid = call.data.split("_")
    uid = int(uid)

    product = products[pid]

    if len(product["keys"]) == 0:
        bot.send_message(ADMIN_ID, "❌ No keys left!")
        return

    key = product["keys"].pop(0)

    bot.send_message(
        uid,
        "✅ PAYMENT APPROVED\n\n"
        f"🔑 KEY: {key}\n"
        f"📥 LINK: {product['link']}\n\n"
        "🎉 Thank you for purchase!"
    )

    bot.edit_message_caption(
        "✅ APPROVED & DELIVERED",
        ADMIN_ID,
        call.message.message_id
    )

# ================= REJECT =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject(call):
    if call.from_user.id != ADMIN_ID:
        return

    uid = int(call.data.split("_")[1])
    bot.send_message(uid, "❌ Your payment was rejected. Please try again.")

    bot.edit_message_caption(
        "❌ REJECTED",
        ADMIN_ID,
        call.message.message_id
    )

# ================= HELP =================
@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_menu(call):
    bot.send_message(call.message.chat.id,
        "📌 HELP MENU\n\n"
        "/start - Open shop\n"
        "/stock - Check stock (admin)\n"
        "/addkey - Add key (admin)\n"
        "/broadcast - Send message (admin)"
    )

# ================= OWNER =================
@bot.callback_query_handler(func=lambda call: call.data == "owner")
def owner(call):
    bot.send_message(call.message.chat.id, "👤 Owner: @yourusername")

# ================= CHANNELS =================
@bot.callback_query_handler(func=lambda call: call.data == "channels")
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

# ================= BROADCAST =================
@bot.message_handler(commands=['broadcast'])
def broadcast(msg):
    if msg.chat.id != ADMIN_ID:
        return

    text = msg.text.replace("/broadcast", "").strip()

    for uid in list(pending.keys()):
        try:
            bot.send_message(uid, f"📢 {text}")
        except:
            pass

    bot.reply_to(msg, "✅ Broadcast sent")

print("🔥 Bot Running...")
bot.infinity_polling()
