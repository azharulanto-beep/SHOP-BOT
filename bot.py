import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import json
import random
import string
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
BKASH_NUMBER = "01918591988"
LOGO_URL = "https://i.postimg.cc/Cxk8NxV2/istockphoto-827351040-1024x1024.jpg"

bot = telebot.TeleBot(TOKEN)

# ====================== DATABASE ======================
def load_db(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_db(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

users_db = load_db('users.json')
products_db = load_db('products.json')

# ====================== PRODUCTS ======================
if not products_db:
    products_db = {
        "1": {
            "name": "🎮 Reaper X Pro (Root)",
            "price": 349,
            "desc": "10 Days Access\nRoot Required\nAll Features Unlocked",
            "stock": 10,
            "keys": ["REAPER-001", "REAPER-002"]
        },
        "2": {
            "name": "📱 Netflix Premium",
            "price": 299,
            "desc": "30 Days Access\n4K Quality\nPersonal Account",
            "stock": 15,
            "keys": ["NETFLIX-001", "NETFLIX-002"]
        }
    }
    save_db('products.json', products_db)

# ====================== MAIN MENU (Buttons arranged) ======================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    # TOP ROW
    markup.add(
        InlineKeyboardButton("🛍️ SHOP NOW", callback_data="shop"),
        InlineKeyboardButton("👤 MY PROFILE", callback_data="profile")
    )
    # MIDDLE ROW
    markup.add(
        InlineKeyboardButton("💰 WALLET", callback_data="wallet"),
        InlineKeyboardButton("📦 MY ORDERS", callback_data="orders")
    )
    # BOTTOM ROW
    markup.add(
        InlineKeyboardButton("🔗 REFERRAL", callback_data="referral"),
        InlineKeyboardButton("🔑 CHECK KEY", callback_data="check_key")
    )
    # LAST ROW
    markup.add(
        InlineKeyboardButton("🎲 LUCKY SPIN", callback_data="spin"),
        InlineKeyboardButton("📞 SUPPORT", url="https://t.me/PAPAJI_ANTO")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    if user_id not in users_db:
        users_db[user_id] = {"name": message.from_user.first_name, "balance": 0, "orders": []}
        save_db('users.json', users_db)
    
    welcome = f"""✨ WELCOME TO ANTO SHOP ✨

💝 Hello {message.from_user.first_name}!

✅ Instant Delivery
✅ 100% Secure
✅ 24/7 Support

Select an option below:"""
    
    bot.send_photo(message.chat.id, LOGO_URL, caption=welcome, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== SHOP ======================
@bot.callback_query_handler(func=lambda call: call.data == "shop")
def shop(call):
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, product in products_db.items():
        stock_icon = "🟢" if product['stock'] > 0 else "🔴"
        markup.add(InlineKeyboardButton(f"{stock_icon} {product['name']} - ৳{product['price']}", callback_data=f"buy_{pid}"))
    markup.add(InlineKeyboardButton("🏠 BACK TO HOME", callback_data="home"))
    
    bot.edit_message_caption("🛍️ SELECT PRODUCT:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy(call):
    pid = call.data.replace("buy_", "")
    product = products_db.get(pid)
    
    if not product or product['stock'] <= 0:
        bot.answer_callback_query(call.id, "❌ Out of stock!")
        return
    
    pending[str(call.message.chat.id)] = {"pid": pid, "product": product}
    
    text = f"""💳 PAYMENT PAGE

📦 Product: {product['name']}
💰 Price: ৳{product['price']}
📱 bKash: `{BKASH_NUMBER}`

After payment:
1️⃣ Send TRX ID
2️⃣ Send Screenshot"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ SEND TRX", callback_data="send_trx"),
        InlineKeyboardButton("❌ CANCEL", callback_data="home")
    )
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== PAYMENT SYSTEM ======================
pending = {}

@bot.callback_query_handler(func=lambda call: call.data == "send_trx")
def send_trx(call):
    bot.send_message(call.message.chat.id, "📝 Send your bKash TRX ID:")
    bot.register_next_step_handler(call.message, process_trx)

def process_trx(message):
    if message.text.startswith('/'):
        return
    pending[str(message.chat.id)]['trx'] = message.text
    bot.reply_to(message, "✅ TRX Saved!\n\n📸 Now send payment screenshot:")
    bot.register_next_step_handler(message, process_screenshot)

def process_screenshot(message):
    if message.content_type != 'photo':
        bot.reply_to(message, "❌ Please send a screenshot!")
        bot.register_next_step_handler(message, process_screenshot)
        return
    
    pending_data = pending.get(str(message.chat.id))
    if not pending_data:
        return
    
    product = pending_data['product']
    
    admin_text = f"""🆕 NEW ORDER!

👤 User ID: `{message.chat.id}`
📦 Product: {product['name']}
💰 Amount: ৳{product['price']}
🔢 TRX ID: `{pending_data['trx']}`"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_{message.chat.id}_{pending_data['pid']}"),
        InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{message.chat.id}")
    )
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(message.chat.id, "✅ Order sent to admin! Please wait for approval ⏳", parse_mode="Markdown")
    
    del pending[str(message.chat.id)]

# ====================== APPROVE SYSTEM ======================
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve_order(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ You are not admin!")
        return
    
    _, uid, pid = call.data.split("_")
    uid = int(uid)
    product = products_db.get(pid)
    
    if not product or len(product['keys']) == 0:
        bot.send_message(ADMIN_ID, "❌ No keys available!")
        bot.answer_callback_query(call.id, "No keys!")
        return
    
    key = product['keys'].pop(0)
    product['stock'] -= 1
    save_db('products.json', products_db)
    
    user_text = f"""✅ PAYMENT APPROVED! 🎉

📦 Product: {product['name']}
🔑 Your Key: `{key}`

Thank you for your purchase! 💝"""
    
    bot.send_message(uid, user_text, parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"✅ Order approved! Remaining stock: {product['stock']}")
    bot.answer_callback_query(call.id, "✅ Approved!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_order(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ You are not admin!")
        return
    
    uid = int(call.data.split("_")[1])
    bot.send_message(uid, "❌ PAYMENT REJECTED!\nPlease try again with correct information.", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"❌ Order rejected for user {uid}")
    bot.answer_callback_query(call.id, "✅ Rejected!")

# ====================== CHECK KEY ======================
@bot.callback_query_handler(func=lambda call: call.data == "check_key")
def check_key(call):
    bot.send_message(call.message.chat.id, "🔑 Enter your key:")
    bot.register_next_step_handler(call.message, process_key_check)

def process_key_check(message):
    key = message.text.strip().upper()
    found = False
    for pid, product in products_db.items():
        if key in product['keys']:
            found = True
            bot.reply_to(message, f"✅ VALID KEY!\n📦 {product['name']}\n💝 You can use this key.")
            break
    if not found:
        bot.reply_to(message, "❌ INVALID KEY! Key is wrong or already used.")

# ====================== PROFILE ======================
@bot.callback_query_handler(func=lambda call: call.data == "profile")
def profile(call):
    user = users_db.get(str(call.message.chat.id), {})
    text = f"""👤 MY PROFILE

🆔 ID: {call.message.chat.id}
💰 Balance: ৳{user.get('balance', 0)}
📦 Total Orders: {len(user.get('orders', []))}"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== WALLET ======================
@bot.callback_query_handler(func=lambda call: call.data == "wallet")
def wallet(call):
    user = users_db.get(str(call.message.chat.id), {})
    text = f"""💰 MY WALLET

Balance: ৳{user.get('balance', 0)}
Total Spent: ৳{user.get('total_spent', 0)}

To add money, send to bKash: {BKASH_NUMBER}"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== ORDERS ======================
@bot.callback_query_handler(func=lambda call: call.data == "orders")
def orders(call):
    user = users_db.get(str(call.message.chat.id), {})
    orders_list = user.get('orders', [])
    
    if not orders_list:
        text = "📭 No orders yet!"
    else:
        text = "📦 MY ORDERS\n\n"
        for i, order in enumerate(orders_list[-5:], 1):
            text += f"{i}. {order}\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== REFERRAL ======================
@bot.callback_query_handler(func=lambda call: call.data == "referral")
def referral(call):
    bot_username = bot.get_me().username
    text = f"""🔗 REFERRAL PROGRAM

Earn 10% commission!

Your referral link:
`https://t.me/{bot_username}?start=ref_{call.message.chat.id}`

Share this link with friends!"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📤 SHARE", url=f"https://t.me/share/url?url=https://t.me/{bot_username}?start=ref_{call.message.chat.id}"),
        InlineKeyboardButton("🏠 HOME", callback_data="home")
    )
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== LUCKY SPIN ======================
@bot.callback_query_handler(func=lambda call: call.data == "spin")
def spin(call):
    prizes = ["৳50", "৳100", "৳200", "Try Again", "৳500"]
    prize = random.choice(prizes)
    
    text = f"🎲 LUCKY SPIN 🎲\n\nYou won: {prize}!\n\nContact admin to claim!"
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🎯 SPIN AGAIN", callback_data="spin"),
        InlineKeyboardButton("🏠 HOME", callback_data="home")
    )
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== HOME ======================
@bot.callback_query_handler(func=lambda call: call.data == "home")
def home(call):
    welcome = f"✨ Welcome back {call.from_user.first_name}!\n\nSelect an option below:"
    bot.edit_message_caption(welcome, call.message.chat.id, call.message.message_id, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== ADMIN PANEL ======================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ You are not admin!")
        return
    
    text = """👑 ADMIN PANEL

📦 PRODUCTS:
`/products` - List all products
`/addkey ID|KEY` - Add key

🔑 KEYS:
`/keys` - View all keys

👥 USERS:
`/users` - List users
`/addbalance ID|AMOUNT` - Add balance

📢 OTHER:
`/broadcast MSG` - Send to all
`/stats` - Statistics"""
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['products'])
def list_products(message):
    if message.chat.id != ADMIN_ID:
        return
    text = "📦 PRODUCTS:\n\n"
    for pid, p in products_db.items():
        text += f"{pid}. {p['name']} | ৳{p['price']} | Stock: {p['stock']}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['keys'])
def list_keys(message):
    if message.chat.id != ADMIN_ID:
        return
    text = "🔑 ALL KEYS:\n\n"
    for pid, p in products_db.items():
        text += f"📦 {p['name']}:\n"
        for k in p['keys']:
            text += f"   • {k}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['addkey'])
def add_key(message):
    if message.chat.id != ADMIN_ID:
        return
    try:
        _, pid, key = message.text.split("|")
        if pid in products_db:
            products_db[pid]['keys'].append(key.upper())
            products_db[pid]['stock'] += 1
            save_db('products.json', products_db)
            bot.reply_to(message, f"✅ Key added: {key}")
        else:
            bot.reply_to(message, "❌ Wrong product ID!")
    except:
        bot.reply_to(message, "❌ /addkey ID|KEY")

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id != ADMIN_ID:
        return
    text = f"📊 STATS\n\nUsers: {len(users_db)}\nProducts: {len(products_db)}"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.chat.id != ADMIN_ID:
        return
    msg = message.text.replace("/broadcast ", "")
    count = 0
    for uid in users_db.keys():
        try:
            bot.send_message(int(uid), f"📢 ANNOUNCEMENT\n\n{msg}")
            count += 1
        except:
            pass
    bot.reply_to(message, f"✅ Sent to {count} users")

# ====================== RUN ======================
if __name__ == "__main__":
    print("🔥 ANTO SHOP BOT STARTED!")
    print(f"🤖 Bot: @{bot.get_me().username}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("="*40)
    bot.infinity_polling(timeout=60)
