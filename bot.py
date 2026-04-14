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
    "1": {"name": "DRIP CLINT", "price": "400", "bkash": "01918591988", "keys": [], "link": ""},
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
        if p.get("name") != "Empty":  # ✅ get() ব্যবহার করুন
            markup.add(InlineKeyboardButton(
                f"{p['name']} - {p['price']} | Stock:{len(p['keys'])}",
                callback_data=f"buy_{pid}"
            ))

    bot.send_photo(
        msg.chat.id,
        LOGO,
        caption="🔥 WELCOME TO ANTO SHOP",
        reply_markup=markup
    )

# ================= BUY =================
@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(call):
    pid = call.data.split("_")[1]
    p = products.get(pid)  # ✅ get() ব্যবহার করুন
    
    if not p or p.get("name") == "Empty":
        bot.answer_callback_query(call.id, "Product not available!")
        return

    pending[call.message.chat.id] = {"pid": pid}

    bot.send_message(
        call.message.chat.id,
        f"💰 PAYMENT PAGE\n\n"
        f"📦 Product: {p.get('name')}\n"
        f"💵 Price: {p.get('price')}\n"
        f"📱 bKash: {p.get('01918591988')}\n\n"
        f"👉 Pay first\n👉 Send TRX\n👉 Send Screenshot"
    )

# ================= VERIFY =================
@bot.message_handler(content_types=['text', 'photo'])
def verify(msg):
    if msg.chat.id not in pending:
        return

    data = pending[msg.chat.id]
    pid = data["pid"]
    p = products.get(pid)

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
                f"🆕 ORDER\n\n"
                f"User: {msg.chat.id}\n"
                f"Product: {p.get('name') if p else 'Unknown'}\n"
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
        bot.answer_callback_query(call.id, "You are not admin!")
        return

    _, uid, pid = call.data.split("_")
    uid = int(uid)
    
    product = products.get(pid)
    
    if not product or len(product.get("keys", [])) == 0:
        bot.send_message(ADMIN_ID, "❌ No stock!")
        bot.answer_callback_query(call.id, "No stock!")
        return

    key = product["keys"].pop(0)

    bot.send_message(
        uid,
        f"✅ APPROVED\n\n🔑 KEY: {key}\n📥 LINK: {product.get('link', 'No link')}"
    )
    
    bot.send_message(ADMIN_ID, f"✅ Approved for user {uid}")

# ================= REJECT =================
@bot.callback_query_handler(func=lambda c: c.data.startswith("reject_"))
def reject(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "You are not admin!")
        return

    uid = int(call.data.split("_")[1])
    bot.send_message(uid, "❌ Payment Rejected")
    bot.send_message(ADMIN_ID, f"❌ Rejected user {uid}")

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

        bot.reply_to(msg, f"✅ Added Slot {slot}: {name}")

    except Exception as e:
        bot.reply_to(msg, f"❌ /add slot|name|price|bkash|link\nError: {e}")

# ================= ADD KEY =================
@bot.message_handler(commands=['addkey'])
def addkey(msg):
    if msg.chat.id != ADMIN_ID:
        return

    try:
        _, data = msg.text.split(" ", 1)
        slot, key = data.split("|")
        
        if slot not in products:
            bot.reply_to(msg, "❌ Slot doesn't exist!")
            return

        products[slot]["keys"].append(key)
        bot.reply_to(msg, f"✅ Key added to Slot {slot} (Total: {len(products[slot]['keys'])} keys)")

    except Exception as e:
        bot.reply_to(msg, f"❌ /addkey slot|KEY\nError: {e}")

# ================= REMOVE =================
@bot.message_handler(commands=['remove'])
def remove(msg):
    if msg.chat.id != ADMIN_ID:
        return

    try:
        _, slot = msg.text.split()
        if slot in products:
            products[slot] = {"name": "Empty", "price": "0", "bkash": "", "keys": [], "link": ""}
            bot.reply_to(msg, f"🗑️ Slot {slot} removed/emptied")
        else:
            bot.reply_to(msg, "❌ Slot not found")
    except:
        bot.reply_to(msg, "❌ /remove 1")

# ================= SHOW =================
@bot.message_handler(commands=['show'])
def show(msg):
    if msg.chat.id != ADMIN_ID:
        return

    text = "📦 PRODUCTS\n\n"
    for k, v in products.items():
        text += f"{k}. {v.get('name')} | Price: {v.get('price')} | Keys: {len(v.get('keys', []))}\n"

    bot.send_message(msg.chat.id, text)

# ================= RUN =================
if __name__ == "__main__":
    print("🔥 BOT RUNNING...")
    print(f"Bot Token: {'OK' if TOKEN else 'MISSING!'}")
    print(f"Admin ID: {ADMIN_ID if ADMIN_ID != 0 else 'MISSING!'}")
    
    if not TOKEN or ADMIN_ID == 0:
        print("❌ ERROR: Please set BOT_TOKEN and ADMIN_ID in environment variables!")
    else:
        bot.infinity_polling()
