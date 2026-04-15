from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import json
import random
import string
import time
import threading
from datetime import datetime, timedelta

# ====================== FLASK FOR RENDER ======================
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ ANTO SHOP BOT IS RUNNING!"

# ====================== BOT CODE ======================
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
BKASH_NUMBER = "01918591988"
LOGO_URL = "https://i.postimg.cc/Cxk8NxV2/istockphoto-827351040-1024x1024.jpg"
CHANNEL_LINK = "https://t.me/+G9DiZ6NznoQ2Yzc1"

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
wallet_db = load_db('wallet.json')

# ====================== PRODUCTS ======================
if not products_db:
    products_db = {
        "1": {
            "name": "🔥 DRIP CLINT",
            "price": 400,
            "durations": {
                "7days": {"name": "7 Days", "price": 400},
                "10days": {"name": "10 Days", "price": 550},
                "30days": {"name": "30 Days", "price": 1500}
            },
            "desc": "Premium Gaming Mod\n✓ All Features Unlocked\n✓ Anti-Ban Protected",
            "keys": ["DRIP-001", "DRIP-002", "DRIP-003"],
            "stock": 3
        },
        "2": {
            "name": "🎮 BGMI ESP HACK",
            "price": 299,
            "durations": {
                "7days": {"name": "7 Days", "price": 299},
                "15days": {"name": "15 Days", "price": 499},
                "30days": {"name": "30 Days", "price": 899}
            },
            "desc": "ESP + Aimbot + Wallhack\n✓ 100% Undetected",
            "keys": ["BGMI-001", "BGMI-002"],
            "stock": 2
        },
        "3": {
            "name": "📱 NETFLIX PREMIUM",
            "price": 299,
            "durations": {
                "30days": {"name": "30 Days", "price": 299},
                "90days": {"name": "90 Days", "price": 699},
                "365days": {"name": "365 Days", "price": 1999}
            },
            "desc": "4K Quality\n✓ Personal Account\n✓ All Devices",
            "keys": ["NETFLIX-001"],
            "stock": 1
        }
    }
    save_db('products.json', products_db)

# ====================== WALLET FUNCTIONS ======================
def get_balance(user_id):
    user_id = str(user_id)
    if user_id not in wallet_db:
        wallet_db[user_id] = {"balance": 0, "transactions": []}
        save_db('wallet.json', wallet_db)
    return wallet_db[user_id]["balance"]

def add_balance(user_id, amount):
    user_id = str(user_id)
    if user_id not in wallet_db:
        wallet_db[user_id] = {"balance": 0, "transactions": []}
    wallet_db[user_id]["balance"] += amount
    wallet_db[user_id]["transactions"].append({
        "type": "add",
        "amount": amount,
        "date": str(datetime.now())
    })
    save_db('wallet.json', wallet_db)

def deduct_balance(user_id, amount):
    user_id = str(user_id)
    if user_id not in wallet_db:
        return False
    if wallet_db[user_id]["balance"] >= amount:
        wallet_db[user_id]["balance"] -= amount
        wallet_db[user_id]["transactions"].append({
            "type": "deduct",
            "amount": amount,
            "date": str(datetime.now())
        })
        save_db('wallet.json', wallet_db)
        return True
    return False

# ====================== MAIN MENU ======================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛍️ SHOP NOW", callback_data="shop"),
        InlineKeyboardButton("👤 MY PROFILE", callback_data="profile")
    )
    markup.add(
        InlineKeyboardButton("💰 MY WALLET", callback_data="wallet"),
        InlineKeyboardButton("➕ ADD BALANCE", callback_data="add_balance")
    )
    markup.add(
        InlineKeyboardButton("📦 MY ORDERS", callback_data="orders"),
        InlineKeyboardButton("🔑 CHECK KEY", callback_data="check_key")
    )
    markup.add(
        InlineKeyboardButton("🔗 REFERRAL", callback_data="referral"),
        InlineKeyboardButton("🎲 LUCKY SPIN", callback_data="spin")
    )
    markup.add(
        InlineKeyboardButton("📢 JOIN CHANNEL", url=CHANNEL_LINK),
        InlineKeyboardButton("📞 SUPPORT", url="https://t.me/PAPAJI_ANTO")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    if user_id not in users_db:
        users_db[user_id] = {
            "name": message.from_user.first_name,
            "username": message.from_user.username,
            "joined": str(datetime.now()),
            "referrals": 0,
            "orders": []
        }
        save_db('users.json', users_db)
    
    # Check referral
    if len(message.text.split()) > 1:
        ref_code = message.text.split()[1]
        if ref_code.startswith("ref_"):
            referrer = ref_code.replace("ref_", "")
            if referrer != str(user_id) and users_db.get(referrer):
                users_db[str(user_id)]["referred_by"] = referrer
                users_db[referrer]["referrals"] += 1
                save_db('users.json', users_db)
                bot.send_message(int(referrer), f"🎉 New referral! {message.from_user.first_name} joined using your link!")
    
    balance = get_balance(message.chat.id)
    
    welcome = f"""✨ WELCOME TO ANTO SHOP ✨

💝 Hello {message.from_user.first_name}!

✅ Premium Services
✅ Instant Delivery
✅ 24/7 Support

💰 Your Balance: ৳{balance}

Select an option below:"""
    
    bot.send_photo(message.chat.id, LOGO_URL, caption=welcome, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== SHOP ======================
@bot.callback_query_handler(func=lambda call: call.data == "shop")
def shop(call):
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, product in products_db.items():
        markup.add(InlineKeyboardButton(f"{product['name']} - From ৳{product['price']}", callback_data=f"product_{pid}"))
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption("🛍️ SELECT PRODUCT CATEGORY:\n\nChoose a product:", 
                            call.message.chat.id, call.message.message_id, 
                            reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def show_durations(call):
    pid = call.data.replace("product_", "")
    product = products_db.get(pid)
    
    if not product:
        bot.answer_callback_query(call.id, "Product not found!")
        return
    
    markup = InlineKeyboardMarkup(row_width=2)
    for dur_id, dur in product['durations'].items():
        markup.add(InlineKeyboardButton(f"📅 {dur['name']} - ৳{dur['price']}", callback_data=f"duration_{pid}_{dur_id}"))
    markup.add(InlineKeyboardButton("🔙 BACK", callback_data="shop"))
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    text = f"""📦 **{product['name']}**

{product['desc']}

💰 Base Price: ৳{product['price']}

Select duration:"""
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, 
                            reply_markup=markup, parse_mode="Markdown")

# ====================== PURCHASE ======================
pending_purchase = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith("duration_"))
def purchase(call):
    _, pid, dur_id = call.data.split("_")
    product = products_db.get(pid)
    duration = product['durations'].get(dur_id)
    
    if not product or not duration:
        bot.answer_callback_query(call.id, "Invalid selection!")
        return
    
    pending_purchase[str(call.message.chat.id)] = {
        "pid": pid,
        "dur_id": dur_id,
        "product": product,
        "duration": duration,
        "amount": duration['price']
    }
    
    balance = get_balance(call.message.chat.id)
    
    text = f"""💳 PAYMENT OPTION

📦 Product: {product['name']}
📅 Duration: {duration['name']}
💰 Amount: ৳{duration['price']}

💵 Your Wallet Balance: ৳{balance}

Choose payment method:"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💳 PAY WITH WALLET", callback_data="pay_wallet"),
        InlineKeyboardButton("📱 PAY WITH BKASH", callback_data="pay_bkash")
    )
    markup.add(InlineKeyboardButton("❌ CANCEL", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, 
                            reply_markup=markup, parse_mode="Markdown")

# ====================== WALLET PAYMENT ======================
@bot.callback_query_handler(func=lambda call: call.data == "pay_wallet")
def wallet_payment(call):
    user_id = str(call.message.chat.id)
    pending = pending_purchase.get(user_id)
    
    if not pending:
        bot.answer_callback_query(call.id, "Session expired!")
        return
    
    product = pending['product']
    duration = pending['duration']
    amount = pending['amount']
    
    if deduct_balance(call.message.chat.id, amount):
        if product['keys']:
            key = product['keys'].pop(0)
            product['stock'] -= 1
            save_db('products.json', products_db)
        else:
            key = "OUT OF STOCK - Contact Admin"
        
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        users_db[user_id]['orders'].append({
            "id": order_id,
            "product": product['name'],
            "duration": duration['name'],
            "amount": amount,
            "key": key,
            "date": str(datetime.now()),
            "method": "wallet"
        })
        save_db('users.json', users_db)
        
        new_balance = get_balance(call.message.chat.id)
        
        text = f"""✅ PURCHASE SUCCESSFUL! 🎉

📦 Product: {product['name']}
📅 Duration: {duration['name']}
💰 Paid: ৳{amount}
🔑 Your Key: `{key}`

💝 New Balance: ৳{new_balance}"""
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
        
        bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                                reply_markup=markup, parse_mode="Markdown")
        
        del pending_purchase[user_id]
    else:
        bot.answer_callback_query(call.id, f"❌ Insufficient balance! Need ৳{amount - get_balance(call.message.chat.id)} more.")

# ====================== BKASH PAYMENT ======================
bkash_pending = {}

@bot.callback_query_handler(func=lambda call: call.data == "pay_bkash")
def bkash_payment(call):
    pending = pending_purchase.get(str(call.message.chat.id))
    if not pending:
        bot.answer_callback_query(call.id, "Session expired!")
        return
    
    ref = f"ANTO{random.randint(10000, 99999)}"
    bkash_pending[str(call.message.chat.id)] = {
        "pending": pending,
        "ref": ref
    }
    
    text = f"""💳 BKASH PAYMENT

📦 Product: {pending['product']['name']}
📅 Duration: {pending['duration']['name']}
💰 Amount: ৳{pending['amount']}
📱 bKash Number: `{BKASH_NUMBER}`
🔖 Reference: `{ref}`

Instructions:
1. Send ৳{pending['amount']} to {BKASH_NUMBER}
2. Send TRX ID here
3. Send payment screenshot"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ SEND TRX", callback_data="send_trx"))
    markup.add(InlineKeyboardButton("❌ CANCEL", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "send_trx")
def send_trx(call):
    bot.send_message(call.message.chat.id, "📝 Send your bKash TRX ID:")
    bot.register_next_step_handler(call.message, process_trx)

def process_trx(message):
    if message.text.startswith('/'):
        return
    bkash_pending[str(message.chat.id)]['trx'] = message.text
    bot.reply_to(message, "✅ TRX Saved!\n\n📸 Now send payment screenshot:")
    bot.register_next_step_handler(message, process_screenshot)

def process_screenshot(message):
    if message.content_type != 'photo':
        bot.reply_to(message, "❌ Please send a screenshot!")
        bot.register_next_step_handler(message, process_screenshot)
        return
    
    pending_data = bkash_pending.get(str(message.chat.id))
    if not pending_data:
        return
    
    purchase = pending_data['pending']
    product = purchase['product']
    duration = purchase['duration']
    
    admin_text = f"""🆕 NEW ORDER - BKASH

👤 User: `{message.chat.id}`
👤 Name: {message.from_user.first_name}
📦 Product: {product['name']}
📅 Duration: {duration['name']}
💰 Amount: ৳{purchase['amount']}
🔢 TRX ID: `{pending_data['trx']}`
🔖 Ref: `{pending_data['ref']}`"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_bkash_{message.chat.id}"),
        InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{message.chat.id}")
    )
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(message.chat.id, "✅ Order sent to admin! Please wait for approval ⏳")
    del bkash_pending[str(message.chat.id)]

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_bkash_"))
def approve_bkash(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ You are not admin!")
        return
    
    uid = int(call.data.replace("approve_bkash_", ""))
    pending_data = bkash_pending.get(str(uid))
    
    if not pending_data:
        bot.send_message(ADMIN_ID, "❌ Session expired!")
        return
    
    purchase = pending_data['pending']
    product = purchase['product']
    duration = purchase['duration']
    
    if product['keys']:
        key = product['keys'].pop(0)
        product['stock'] -= 1
        save_db('products.json', products_db)
    else:
        key = "OUT OF STOCK - Contact Admin"
    
    order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    users_db[str(uid)]['orders'].append({
        "id": order_id,
        "product": product['name'],
        "duration": duration['name'],
        "amount": purchase['amount'],
        "key": key,
        "date": str(datetime.now()),
        "method": "bkash"
    })
    save_db('users.json', users_db)
    
    user_text = f"""✅ PAYMENT APPROVED! 🎉

📦 Product: {product['name']}
📅 Duration: {duration['name']}
💰 Paid: ৳{purchase['amount']}
🔑 Your Key: `{key}`

💝 Thank you for shopping with ANTO SHOP!"""
    
    bot.send_message(uid, user_text, parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"✅ Order approved for user {uid}")
    bot.answer_callback_query(call.id, "✅ Approved!")
    
    del bkash_pending[str(uid)]

# ====================== ADD BALANCE ======================
@bot.callback_query_handler(func=lambda call: call.data == "add_balance")
def add_balance_menu(call):
    text = f"""💰 ADD BALANCE

📱 bKash Number: `{BKASH_NUMBER}`

Instructions:
1. Send money to {BKASH_NUMBER}
2. Send TRX ID and amount
3. Send screenshot

Example: `500 8Y7X9K2M4N`"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")
    bot.send_message(call.message.chat.id, "📝 Send amount and TRX ID:\n\nExample: `500 8Y7X9K2M4N`")
    bot.register_next_step_handler(call.message, process_balance_add)

def process_balance_add(message):
    if message.text.startswith('/'):
        return
    
    try:
        parts = message.text.split()
        amount = int(parts[0])
        trx = parts[1]
        
        admin_text = f"""💰 BALANCE ADD REQUEST

👤 User: `{message.chat.id}`
👤 Name: {message.from_user.first_name}
💰 Amount: ৳{amount}
🔢 TRX ID: `{trx}`"""
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_balance_{message.chat.id}_{amount}"),
            InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{message.chat.id}")
        )
        
        bot.send_message(ADMIN_ID, admin_text, reply_markup=markup, parse_mode="Markdown")
        bot.send_message(message.chat.id, "✅ Request sent to admin! Please wait.")
    except:
        bot.send_message(message.chat.id, "❌ Wrong format! Use: `500 8Y7X9K2M4N`", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_balance_"))
def approve_balance(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ You are not admin!")
        return
    
    _, _, uid, amount = call.data.split("_")
    uid = int(uid)
    amount = int(amount)
    
    add_balance(uid, amount)
    bot.send_message(uid, f"✅ ৳{amount} added to your wallet!")
    bot.send_message(ADMIN_ID, f"✅ Added ৳{amount} to user {uid}")
    bot.answer_callback_query(call.id, "✅ Balance added!")

# ====================== WALLET VIEW ======================
@bot.callback_query_handler(func=lambda call: call.data == "wallet")
def view_wallet(call):
    balance = get_balance(call.message.chat.id)
    transactions = wallet_db.get(str(call.message.chat.id), {}).get('transactions', [])[-5:]
    
    text = f"""💰 MY WALLET

💵 Current Balance: ৳{balance}

📜 Recent Transactions:
"""
    if transactions:
        for t in reversed(transactions):
            sign = "+" if t['type'] == 'add' else "-"
            text += f"• {sign} ৳{t['amount']} - {t['date'][:16]}\n"
    else:
        text += "• No transactions yet\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ====================== PROFILE ======================
@bot.callback_query_handler(func=lambda call: call.data == "profile")
def profile(call):
    user = users_db.get(str(call.message.chat.id), {})
    balance = get_balance(call.message.chat.id)
    
    text = f"""👤 MY PROFILE

🆔 ID: `{call.message.chat.id}`
👤 Name: {user.get('name', 'Unknown')}
📅 Joined: {user.get('joined', 'Unknown')[:10]}

💰 Wallet Balance: ৳{balance}
📦 Total Orders: {len(user.get('orders', []))}
👥 Referrals: {user.get('referrals', 0)}"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ====================== ORDERS ======================
@bot.callback_query_handler(func=lambda call: call.data == "orders")
def orders(call):
    user = users_db.get(str(call.message.chat.id), {})
    orders_list = user.get('orders', [])
    
    if not orders_list:
        text = "📭 NO ORDERS YET!\n\nStart shopping now!"
    else:
        text = "📦 YOUR ORDERS\n\n"
        for order in orders_list[-10:]:
            text += f"🆔 {order.get('id', 'N/A')}\n"
            text += f"📦 {order['product']} ({order.get('duration', 'N/A')})\n"
            text += f"💰 ৳{order['amount']} | {order['date'][:10]}\n"
            text += f"🔑 Key: `{order.get('key', 'N/A')}`\n\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ====================== CHECK KEY ======================
@bot.callback_query_handler(func=lambda call: call.data == "check_key")
def check_key_menu(call):
    bot.send_message(call.message.chat.id, "🔑 Enter your product key:")
    bot.register_next_step_handler(call.message, process_key_check)

def process_key_check(message):
    key = message.text.strip().upper()
    found = False
    
    for pid, product in products_db.items():
        if key in product['keys']:
            found = True
            bot.reply_to(message, f"✅ VALID KEY!\n📦 {product['name']}\n💝 You can use this key.", parse_mode="Markdown")
            break
    
    if not found:
        bot.reply_to(message, "❌ INVALID KEY!\nKey is wrong or already used.", parse_mode="Markdown")

# ====================== REFERRAL ======================
@bot.callback_query_handler(func=lambda call: call.data == "referral")
def referral(call):
    bot_username = bot.get_me().username
    text = f"""🔗 REFERRAL PROGRAM

💰 Earn 10% commission on every purchase your referrals make!

👥 Your Referrals: {users_db.get(str(call.message.chat.id), {}).get('referrals', 0)}

🔗 Your Link:
`https://t.me/{bot_username}?start=ref_{call.message.chat.id}`

Share this link with friends!"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📤 SHARE LINK", url=f"https://t.me/share/url?url=https://t.me/{bot_username}?start=ref_{call.message.chat.id}&text=Join ANTO SHOP for premium services!"),
        InlineKeyboardButton("🏠 HOME", callback_data="home")
    )
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ====================== LUCKY SPIN ======================
spin_cooldown = {}

@bot.callback_query_handler(func=lambda call: call.data == "spin")
def lucky_spin(call):
    user_id = str(call.message.chat.id)
    
    if user_id in spin_cooldown:
        last_spin = datetime.fromisoformat(spin_cooldown[user_id])
        if datetime.now() - last_spin < timedelta(hours=24):
            remaining = timedelta(hours=24) - (datetime.now() - last_spin)
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            bot.answer_callback_query(call.id, f"Come back in {hours}h {minutes}m!")
            return
    
    prizes = [5, 10, 20, 50, 100, 0, 0, 5, 10, 0, 20, 50]
    prize = random.choice(prizes)
    
    if prize > 0:
        add_balance(user_id, prize)
        result_text = f"🎉 CONGRATULATIONS! 🎉\n\nYou won ৳{prize}!\n💰 Added to your wallet!"
    else:
        result_text = "😢 BETTER LUCK NEXT TIME!\n\nYou won nothing.\nTry again tomorrow!"
    
    spin_cooldown[user_id] = str(datetime.now())
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(result_text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ====================== REJECT ======================
@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_order(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ You are not admin!")
        return
    
    uid = int(call.data.replace("reject_", ""))
    bot.send_message(uid, "❌ REJECTED!\nPlease contact support.", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"❌ Rejected user {uid}")
    bot.answer_callback_query(call.id, "✅ Rejected!")

# ====================== HOME ======================
@bot.callback_query_handler(func=lambda call: call.data == "home")
def home(call):
    balance = get_balance(call.message.chat.id)
    welcome = f"✨ Welcome back {call.from_user.first_name}! ✨\n\n💰 Balance: ৳{balance}\n\nSelect an option below:"
    bot.edit_message_caption(welcome, call.message.chat.id, call.message.message_id,
                            reply_markup=main_menu(), parse_mode="Markdown")

# ====================== ADMIN PANEL ======================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ You are not admin!")
        return
    
    text = """👑 ADMIN PANEL - FULL CONTROL

📦 PRODUCT MANAGEMENT:
`/products` - List all products
`/addkey PID|KEY` - Add single key
`/addkeys PID|KEY1,KEY2` - Add multiple keys
`/removekey KEY` - Remove key

💰 WALLET MANAGEMENT:
`/addbalance UID AMOUNT` - Add balance

👥 USER MANAGEMENT:
`/users` - List all users
`/broadcast MSG` - Send to all
`/stats` - Bot statistics"""
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['products'])
def list_products(message):
    if message.chat.id != ADMIN_ID:
        return
    
    text = "📦 ALL PRODUCTS:\n\n"
    for pid, p in products_db.items():
        text += f"🆔 {pid} | {p['name']}\n"
        text += f"   💰 Base: ৳{p['price']}\n"
        text += f"   🔑 Keys: {len(p['keys'])} | 📦 Stock: {p['stock']}\n\n"
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
            bot.reply_to(message, "❌ Product not found!")
    except:
        bot.reply_to(message, "❌ /addkey PID|KEY")

@bot.message_handler(commands=['addkeys'])
def add_keys(message):
    if message.chat.id != ADMIN_ID:
        return
    
    try:
        _, pid, keys_str = message.text.split("|")
        keys = [k.strip().upper() for k in keys_str.split(",")]
        
        if pid in products_db:
            for key in keys:
                products_db[pid]['keys'].append(key)
                products_db[pid]['stock'] += 1
            save_db('products.json', products_db)
            bot.reply_to(message, f"✅ Added {len(keys)} keys!")
        else:
            bot.reply_to(message, "❌ Product not found!")
    except:
        bot.reply_to(message, "❌ /addkeys PID|KEY1,KEY2,KEY3")

@bot.message_handler(commands=['removekey'])
def remove_key(message):
    if message.chat.id != ADMIN_ID:
        return
    
    try:
        key = message.text.split()[1].upper()
        removed = False
        for pid, product in products_db.items():
            if key in product['keys']:
                product['keys'].remove(key)
                product['stock'] -= 1
                removed = True
                save_db('products.json', products_db)
                break
        if removed:
            bot.reply_to(message, f"✅ Key removed: {key}")
        else:
            bot.reply_to(message, "❌ Key not found!")
    except:
        bot.reply_to(message, "❌ /removekey KEY")

@bot.message_handler(commands=['addbalance'])
def add_balance_admin(message):
    if message.chat.id != ADMIN_ID:
        return
    
    try:
        _, uid, amount = message.text.split()
        uid = int(uid)
        amount = int(amount)
        
        add_balance(uid, amount)
        bot.send_message(uid, f"💰 ৳{amount} added to your wallet by admin!")
        bot.reply_to(message, f"✅ Added ৳{amount} to user {uid}")
    except:
        bot.reply_to(message, "❌ /addbalance USER_ID AMOUNT")

@bot.message_handler(commands=['users'])
def list_users(message):
    if message.chat.id != ADMIN_ID:
        return
    
    text = "👥 USERS:\n\n"
    for uid, user in list(users_db.items())[:30]:
        balance = get_balance(uid)
        text += f"🆔 {uid} | {user.get('name', 'Unknown')}\n"
        text += f"   💰 ৳{balance} | 📦 {len(user.get('orders', []))}\n\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id != ADMIN_ID:
        return
    
    total_users = len(users_db)
    total_orders = sum(len(u.get('orders', [])) for u in users_db.values())
    total_keys = sum(len(p['keys']) for p in products_db.values())
    total_balance = sum(w.get('balance', 0) for w in wallet_db.values())
    
    text = f"""📊 BOT STATISTICS

👥 Total Users: {total_users}
📦 Total Orders: {total_orders}
🔑 Total Keys: {total_keys}
💰 Total Wallet Balance: ৳{total_balance}
📦 Total Products: {len(products_db)}"""
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.chat.id != ADMIN_ID:
        return
    
    msg = message.text.replace("/broadcast ", "")
    count = 0
    
    for uid in users_db.keys():
        try:
            bot.send_message(int(uid), f"📢 ANNOUNCEMENT\n\n{msg}", parse_mode="Markdown")
            count += 1
            time.sleep(0.05)
        except:
            pass
    
    bot.reply_to(message, f"✅ Broadcast sent to {count} users!")

# ====================== RUN BOTH ======================
def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("="*50)
    print("🔥 ANTO SHOP ULTIMATE BOT STARTED!")
    print(f"🤖 Bot: @{bot.get_me().username}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("="*50)
    
    # Start bot in background
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask for Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
