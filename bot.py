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
            "desc": "✨ 10 Days Access\n✅ Root Required\n✅ All Features Unlocked",
            "stock": 10,
            "keys": ["REAPER-001", "REAPER-002"]
        },
        "2": {
            "name": "📱 Netflix Premium",
            "price": 299,
            "desc": "✨ 30 Days Access\n✅ 4K Quality\n✅ Personal Account",
            "stock": 15,
            "keys": ["NETFLIX-001", "NETFLIX-002"]
        },
        "3": {
            "name": "🎵 Spotify Premium",
            "price": 199,
            "desc": "✨ 12 Months Access\n✅ Ad-Free\n✅ Download Music",
            "stock": 20,
            "keys": ["SPOTIFY-001", "SPOTIFY-002"]
        },
        "4": {
            "name": "🛡️ VPN Premium",
            "price": 249,
            "desc": "✨ 1 Year Access\n✅ Unlimited Bandwidth\n✅ 50+ Countries",
            "stock": 25,
            "keys": ["VPN-001", "VPN-002"]
        }
    }
    save_db('products.json', products_db)

# ====================== MAIN MENU (2 COLUMNS) ======================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛍️ SHOP NOW", callback_data="shop"),
        InlineKeyboardButton("👤 MY PROFILE", callback_data="profile"),
        InlineKeyboardButton("💰 WALLET", callback_data="wallet"),
        InlineKeyboardButton("📦 MY ORDERS", callback_data="orders"),
        InlineKeyboardButton("🔑 CHECK KEY", callback_data="check_key"),
        InlineKeyboardButton("🔗 REFERRAL", callback_data="referral"),
        InlineKeyboardButton("🎲 LUCKY SPIN", callback_data="spin"),
        InlineKeyboardButton("📞 SUPPORT", url="https://t.me/PAPAJI_ANTO"),
        InlineKeyboardButton("📖 HOW TO USE", callback_data="howto"),
        InlineKeyboardButton("🏆 LEADERBOARD", callback_data="leaderboard")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    if user_id not in users_db:
        users_db[user_id] = {
            "name": message.from_user.first_name,
            "balance": 0,
            "orders": [],
            "joined": str(datetime.now())
        }
        save_db('users.json', users_db)
    
    welcome = f"""✨ **WELCOME TO ANTO SHOP** ✨

💝 Hello {message.from_user.first_name}!

✅ Instant Delivery
✅ 100% Secure
✅ 24/7 Support

📌 Select an option below:"""
    
    bot.send_photo(message.chat.id, LOGO_URL, caption=welcome, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== SHOP (2 COLUMNS) ======================
@bot.callback_query_handler(func=lambda call: call.data == "shop")
def shop(call):
    markup = InlineKeyboardMarkup(row_width=2)  # 2 columns
    for pid, product in products_db.items():
        stock_icon = "🟢" if product['stock'] > 0 else "🔴"
        markup.add(InlineKeyboardButton(
            f"{stock_icon} {product['name']}\n💰 ৳{product['price']}", 
            callback_data=f"buy_{pid}"
        ))
    markup.add(InlineKeyboardButton("🏠 BACK TO HOME", callback_data="home"))
    
    bot.edit_message_caption(
        "🛍️ **SELECT YOUR PRODUCT**\n\nTap on any product to buy:",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup, parse_mode="Markdown"
    )

# ====================== PRODUCT DETAILS ======================
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy(call):
    pid = call.data.replace("buy_", "")
    product = products_db.get(pid)
    
    if not product or product['stock'] <= 0:
        bot.answer_callback_query(call.id, "❌ Out of stock!")
        return
    
    text = f"""📦 **{product['name']}**

{product['desc']}

💰 **Price:** ৳{product['price']}
📊 **Stock:** {product['stock']} left

✅ Instant Delivery
✅ 24/7 Support
✅ Money Back Guarantee

Tap **BUY NOW** to purchase!"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛒 BUY NOW", callback_data=f"pay_{pid}"),
        InlineKeyboardButton("🔙 BACK", callback_data="shop"),
        InlineKeyboardButton("🏠 HOME", callback_data="home")
    )
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== PAYMENT SYSTEM ======================
pending = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def payment(call):
    pid = call.data.replace("pay_", "")
    product = products_db.get(pid)
    
    if not product or product['stock'] <= 0:
        bot.answer_callback_query(call.id, "❌ Out of stock!")
        return
    
    pending[str(call.message.chat.id)] = {"pid": pid, "product": product}
    
    text = f"""💳 **PAYMENT PAGE**

📦 **Product:** {product['name']}
💰 **Amount:** ৳{product['price']}
📱 **bKash Number:** `{BKASH_NUMBER}`

**After Payment:**
1️⃣ Send TRX ID
2️⃣ Send Screenshot

⚠️ Send TRX ID first, then screenshot!"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ SENT TRX", callback_data="send_trx"),
        InlineKeyboardButton("❌ CANCEL", callback_data="home")
    )
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "send_trx")
def send_trx(call):
    bot.send_message(call.message.chat.id, "📝 **Please send your bKash TRX ID:**")
    bot.register_next_step_handler(call.message, process_trx)

def process_trx(message):
    if message.text.startswith('/'):
        return
    pending[str(message.chat.id)]['trx'] = message.text
    bot.reply_to(message, "✅ TRX Saved!\n\n📸 Now send the payment screenshot:")
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
    
    admin_text = f"""🆕 **NEW ORDER!**

👤 **User ID:** `{message.chat.id}`
👤 **Name:** {message.from_user.first_name}
📦 **Product:** {product['name']}
💰 **Amount:** ৳{product['price']}
🔢 **TRX ID:** `{pending_data['trx']}`
⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_{message.chat.id}_{pending_data['pid']}"),
        InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{message.chat.id}")
    )
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(message.chat.id, "✅ **Order sent to admin!**\nPlease wait for approval ⏳", parse_mode="Markdown")
    
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
    
    user_text = f"""✅ **PAYMENT APPROVED!** 🎉

📦 **Product:** {product['name']}
🔑 **Your Key:** `{key}`

💝 Thank you for shopping with us!"""
    
    bot.send_message(uid, user_text, parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"✅ Order approved for user {uid}\n📦 Remaining stock: {product['stock']}")
    bot.answer_callback_query(call.id, "✅ Approved!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_order(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ You are not admin!")
        return
    
    uid = int(call.data.split("_")[1])
    bot.send_message(uid, "❌ **PAYMENT REJECTED!**\n\nPlease check your payment and try again.", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"❌ Order rejected for user {uid}")
    bot.answer_callback_query(call.id, "✅ Rejected!")

# ====================== CHECK KEY ======================
@bot.callback_query_handler(func=lambda call: call.data == "check_key")
def check_key(call):
    bot.send_message(call.message.chat.id, "🔑 **Please send your product key:**")
    bot.register_next_step_handler(call.message, process_key_check)

def process_key_check(message):
    key = message.text.strip().upper()
    found = False
    for pid, product in products_db.items():
        if key in product['keys']:
            found = True
            bot.reply_to(message, f"✅ **VALID KEY!**\n📦 {product['name']}\n💝 You can use this key.")
            break
    if not found:
        bot.reply_to(message, "❌ **INVALID KEY!**\nKey is wrong or already used.")

# ====================== MY PROFILE ======================
@bot.callback_query_handler(func=lambda call: call.data == "profile")
def profile(call):
    user = users_db.get(str(call.message.chat.id), {})
    text = f"""👤 **MY PROFILE**

🆔 **ID:** {call.message.chat.id}
👤 **Name:** {call.from_user.first_name}
💰 **Balance:** ৳{user.get('balance', 0)}
📦 **Orders:** {len(user.get('orders', []))}
📅 **Joined:** {user.get('joined', 'Unknown')}"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 BACK TO HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== MY ORDERS ======================
@bot.callback_query_handler(func=lambda call: call.data == "orders")
def orders(call):
    user = users_db.get(str(call.message.chat.id), {})
    orders_list = user.get('orders', [])
    
    if not orders_list:
        text = "📭 **No orders yet!**\n\nStart shopping now!"
    else:
        text = "📜 **YOUR ORDERS**\n\n"
        for i, order in enumerate(orders_list[-10:], 1):
            text += f"{i}. 📦 {order}\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 BACK TO HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== REFERRAL ======================
@bot.callback_query_handler(func=lambda call: call.data == "referral")
def referral(call):
    bot_username = bot.get_me().username
    text = f"""🔗 **REFERRAL PROGRAM**

💰 **Earn 10% commission** on every purchase!

👥 **Your Referrals:** 0
💵 **Earned:** ৳0

🔗 **Your Link:**
`https://t.me/{bot_username}?start=ref_{call.message.chat.id}`

Share this link with friends!"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 BACK TO HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== LUCKY SPIN ======================
@bot.callback_query_handler(func=lambda call: call.data == "spin")
def spin(call):
    prizes = ["💰 ৳50 Cash", "💰 ৳100 Cash", "🎁 Free Product", "🎫 10% Coupon", "😢 Try Again", "💰 ৳200 Cash"]
    prize = random.choice(prizes)
    
    text = f"🎲 **LUCKY SPIN** 🎲\n\nYou won: **{prize}**!\n\nContact admin to claim!"
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🎯 SPIN AGAIN", callback_data="spin"),
        InlineKeyboardButton("🏠 BACK TO HOME", callback_data="home")
    )
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== HOW TO USE ======================
@bot.callback_query_handler(func=lambda call: call.data == "howto")
def howto(call):
    text = """📖 **HOW TO USE**

1️⃣ **Buy Product:**
   • Tap SHOP NOW
   • Select your product
   • Tap BUY NOW

2️⃣ **Payment:**
   • Send money to bKash number
   • Send TRX ID in chat
   • Send payment screenshot

3️⃣ **Get Product:**
   • Wait for admin approval
   • Receive your key instantly

📞 **Need Help?** Contact: @PAPAJI_ANTO"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 BACK TO HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== WALLET ======================
@bot.callback_query_handler(func=lambda call: call.data == "wallet")
def wallet(call):
    user = users_db.get(str(call.message.chat.id), {})
    text = f"""💰 **MY WALLET**

💵 **Balance:** ৳{user.get('balance', 0)}
💸 **Total Spent:** ৳{user.get('total_spent', 0)}

**Add Money:**
• bKash: {BKASH_NUMBER}
• Send screenshot to admin"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 BACK TO HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== LEADERBOARD ======================
@bot.callback_query_handler(func=lambda call: call.data == "leaderboard")
def leaderboard(call):
    sorted_users = sorted(users_db.items(), key=lambda x: x[1].get('total_spent', 0), reverse=True)[:10]
    
    text = "🏆 **TOP 10 USERS** 🏆\n\n"
    for i, (uid, data) in enumerate(sorted_users, 1):
        text += f"{i}. {data.get('name', 'Unknown')} - ৳{data.get('total_spent', 0)}\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 BACK TO HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== HOME ======================
@bot.callback_query_handler(func=lambda call: call.data == "home")
def home(call):
    welcome = f"✨ **WELCOME BACK!** ✨\n\n💝 Hello {call.from_user.first_name}!\n\n📌 Select an option below:"
    bot.edit_message_caption(welcome, call.message.chat.id, call.message.message_id, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== ADMIN COMMANDS ======================
@bot.message_handler(commands=['addkey'])
def add_key(message):
    if message.chat.id != ADMIN_ID:
        return
    try:
        _, pid, key = message.text.split()
        if pid in products_db:
            products_db[pid]['keys'].append(key.upper())
            products_db[pid]['stock'] += 1
            save_db('products.json', products_db)
            bot.reply_to(message, f"✅ Key added to {products_db[pid]['name']}!")
    except:
        bot.reply_to(message, "❌ /addkey product_id KEY")

@bot.message_handler(commands=['addbalance'])
def add_balance(message):
    if message.chat.id != ADMIN_ID:
        return
    try:
        _, uid, amount = message.text.split()
        uid = str(uid)
        if uid not in users_db:
            users_db[uid] = {"name": "User", "balance": 0, "orders": []}
        users_db[uid]['balance'] += int(amount)
        save_db('users.json', users_db)
        bot.reply_to(message, f"✅ Added ৳{amount} to user {uid}")
    except:
        bot.reply_to(message, "❌ /addbalance user_id amount")

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id != ADMIN_ID:
        return
    text = f"📊 **BOT STATS**\n\n👥 Users: {len(users_db)}\n📦 Products: {len(products_db)}"
    bot.reply_to(message, text, parse_mode="Markdown")

# ====================== RUN ======================
if __name__ == "__main__":
    print("="*50)
    print("🔥 ANTO SHOP BOT STARTED!")
    print(f"🤖 Bot: @{bot.get_me().username}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("="*50)
    bot.infinity_polling(timeout=60)
