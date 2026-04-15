import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import json
import random
import string
from datetime import datetime, timedelta

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
BKASH_NUMBER = "01918591988"
LOGO_URL = "https://i.postimg.cc/Cxk8NxV2/istockphoto-827351040-1024x1024.jpg"

bot = telebot.TeleBot(TOKEN)

# ====================== ডাটাবেজ ======================
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

# ====================== প্রোডাক্ট ======================
if not products_db:
    products_db = {
        "1": {
            "name": "🔥 DRIP CLINT",
            "price": 400,
            "keys": ["DRIP-001", "DRIP-002", "DRIP-003"],
            "stock": 3,
            "desc": "Premium Gaming Mod"
        },
        "2": {
            "name": "🎮 BGMI ESP HACK",
            "price": 299,
            "keys": ["BGMI-001", "BGMI-002"],
            "stock": 2,
            "desc": "ESP + Aimbot"
        },
        "3": {
            "name": "📱 NETFLIX PREMIUM",
            "price": 299,
            "keys": ["NETFLIX-001"],
            "stock": 1,
            "desc": "4K Quality"
        }
    }
    save_db('products.json', products_db)

# ====================== ওয়ালেট ======================
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

# ====================== মেনু ======================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛍️ SHOP NOW", callback_data="shop"),
        InlineKeyboardButton("💰 MY WALLET", callback_data="wallet")
    )
    markup.add(
        InlineKeyboardButton("📦 MY ORDERS", callback_data="orders"),
        InlineKeyboardButton("🎲 LUCKY SPIN", callback_data="spin")
    )
    markup.add(
        InlineKeyboardButton("📞 SUPPORT", url="https://t.me/PAPAJI_ANTO")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    if user_id not in users_db:
        users_db[user_id] = {
            "name": message.from_user.first_name,
            "joined": str(datetime.now()),
            "orders": []
        }
        save_db('users.json', users_db)
    
    balance = get_balance(message.chat.id)
    
    welcome = f"""✨ WELCOME TO ANTO SHOP ✨

Hello {message.from_user.first_name}!

💰 Your Balance: ৳{balance}

Select an option below:"""
    
    bot.send_photo(message.chat.id, LOGO_URL, caption=welcome, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== শপ ======================
@bot.callback_query_handler(func=lambda call: call.data == "shop")
def shop(call):
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, product in products_db.items():
        stock_icon = "🟢" if product['stock'] > 0 else "🔴"
        markup.add(InlineKeyboardButton(f"{stock_icon} {product['name']} - ৳{product['price']}", callback_data=f"buy_{pid}"))
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption("🛍️ SELECT PRODUCT:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== কেনা ======================
pending_purchase = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_product(call):
    pid = call.data.replace("buy_", "")
    product = products_db.get(pid)
    
    if not product or product['stock'] <= 0:
        bot.answer_callback_query(call.id, "❌ Out of stock!")
        return
    
    pending_purchase[str(call.message.chat.id)] = {
        "pid": pid,
        "product": product,
        "amount": product['price']
    }
    
    balance = get_balance(call.message.chat.id)
    
    text = f"""💳 PAYMENT

📦 {product['name']}
💰 Price: ৳{product['price']}

💵 Your Balance: ৳{balance}

Click PAY to purchase:"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("💳 PAY WITH WALLET", callback_data="pay_wallet"),
        InlineKeyboardButton("❌ CANCEL", callback_data="home")
    )
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "pay_wallet")
def wallet_payment(call):
    user_id = str(call.message.chat.id)
    pending = pending_purchase.get(user_id)
    
    if not pending:
        bot.answer_callback_query(call.id, "Session expired!")
        return
    
    product = pending['product']
    amount = pending['amount']
    balance = get_balance(call.message.chat.id)
    
    if balance >= amount:
        deduct_balance(call.message.chat.id, amount)
        
        if product['keys']:
            key = product['keys'].pop(0)
            product['stock'] -= 1
            save_db('products.json', products_db)
        else:
            key = "OUT OF STOCK"
        
        users_db[user_id]['orders'].append({
            "product": product['name'],
            "amount": amount,
            "key": key,
            "date": str(datetime.now())
        })
        save_db('users.json', users_db)
        
        new_balance = get_balance(call.message.chat.id)
        
        text = f"""✅ PURCHASE SUCCESSFUL! 🎉

📦 {product['name']}
💰 Paid: ৳{amount}
🔑 Key: `{key}`

💝 New Balance: ৳{new_balance}"""
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
        
        bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        
        del pending_purchase[user_id]
    else:
        bot.answer_callback_query(call.id, f"❌ Insufficient balance! Need ৳{amount - balance} more.")

# ====================== ওয়ালেট ======================
@bot.callback_query_handler(func=lambda call: call.data == "wallet")
def view_wallet(call):
    balance = get_balance(call.message.chat.id)
    
    text = f"""💰 MY WALLET

💵 Balance: ৳{balance}

To add balance, contact admin: @PAPAJI_ANTO"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== অর্ডার ======================
@bot.callback_query_handler(func=lambda call: call.data == "orders")
def view_orders(call):
    user = users_db.get(str(call.message.chat.id), {})
    orders_list = user.get('orders', [])
    
    if not orders_list:
        text = "📭 NO ORDERS YET!"
    else:
        text = "📦 YOUR ORDERS:\n\n"
        for order in orders_list[-10:]:
            text += f"📦 {order['product']}\n"
            text += f"💰 ৳{order['amount']} | {order['date'][:10]}\n"
            text += f"🔑 Key: `{order.get('key', 'N/A')}`\n\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== লাকি স্পিন ======================
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
    
    prizes = [5, 10, 20, 50, 100, 0, 0, 5, 10]
    prize = random.choice(prizes)
    
    if prize > 0:
        add_balance(user_id, prize)
        result_text = f"🎉 CONGRATULATIONS! 🎉\n\nYou won ৳{prize}!\n💰 Added to your wallet!"
    else:
        result_text = "😢 BETTER LUCK NEXT TIME!\n\nYou won nothing.\nTry again tomorrow!"
    
    spin_cooldown[user_id] = str(datetime.now())
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(result_text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== হোম ======================
@bot.callback_query_handler(func=lambda call: call.data == "home")
def home(call):
    balance = get_balance(call.message.chat.id)
    welcome = f"✨ Welcome back {call.from_user.first_name}!\n\n💰 Balance: ৳{balance}\n\nSelect an option:"
    bot.edit_message_caption(welcome, call.message.chat.id, call.message.message_id, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== অ্যাডমিন প্যানেল ======================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        return
    
    text = """👑 ADMIN PANEL

COMMANDS:
/addbalance USER_ID AMOUNT
/addkey PRODUCT_ID|KEY
/products
/users
/stats
/broadcast MESSAGE"""
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

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

@bot.message_handler(commands=['products'])
def list_products(message):
    if message.chat.id != ADMIN_ID:
        return
    
    text = "📦 PRODUCTS:\n\n"
    for pid, p in products_db.items():
        text += f"🆔 {pid} | {p['name']}\n"
        text += f"   💰 ৳{p['price']} | 🔑 {len(p['keys'])} | 📦 {p['stock']}\n\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['users'])
def list_users(message):
    if message.chat.id != ADMIN_ID:
        return
    
    text = "👥 USERS:\n\n"
    for uid, user in list(users_db.items())[:20]:
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
    
    text = f"""📊 STATISTICS

👥 Users: {total_users}
📦 Orders: {total_orders}
🔑 Keys: {total_keys}
📦 Products: {len(products_db)}"""
    
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
        except:
            pass
    
    bot.reply_to(message, f"✅ Sent to {count} users")

# ====================== রান ======================
if __name__ == "__main__":
    print("="*40)
    print("🔥 ANTO SHOP BOT STARTED!")
    print(f"🤖 Bot: @{bot.get_me().username}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("="*40)
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
