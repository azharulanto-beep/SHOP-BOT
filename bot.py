import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import json
import random
import string
import time
from datetime import datetime, timedelta

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
            "desc": "Premium Gaming Mod",
            "keys": ["DRIP-001", "DRIP-002"],
            "stock": 2
        },
        "2": {
            "name": "🎮 BGMI ESP HACK",
            "price": 299,
            "durations": {
                "7days": {"name": "7 Days", "price": 299},
                "15days": {"name": "15 Days", "price": 499},
                "30days": {"name": "30 Days", "price": 899}
            },
            "desc": "ESP + Aimbot",
            "keys": ["BGMI-001"],
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
        InlineKeyboardButton("💰 MY WALLET", callback_data="wallet")
    )
    markup.add(
        InlineKeyboardButton("📦 MY ORDERS", callback_data="orders"),
        InlineKeyboardButton("🎲 LUCKY SPIN", callback_data="spin")
    )
    markup.add(
        InlineKeyboardButton("➕ ADD BALANCE", callback_data="add_balance"),
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

💰 Balance: ৳{balance}

Select an option below:"""
    
    bot.send_photo(message.chat.id, LOGO_URL, caption=welcome, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== SHOP ======================
@bot.callback_query_handler(func=lambda call: call.data == "shop")
def shop(call):
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, product in products_db.items():
        markup.add(InlineKeyboardButton(f"{product['name']}", callback_data=f"product_{pid}"))
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption("🛍️ SELECT PRODUCT:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

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
    
    text = f"""💳 PAYMENT

📦 {product['name']}
📅 {duration['name']}
💰 Amount: ৳{duration['price']}

💵 Your Balance: ৳{balance}"""
    
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
            key = "OUT OF STOCK"
        
        users_db[user_id]['orders'].append({
            "product": product['name'],
            "duration": duration['name'],
            "amount": amount,
            "key": key,
            "date": str(datetime.now())
        })
        save_db('users.json', users_db)
        
        new_balance = get_balance(call.message.chat.id)
        
        text = f"""✅ PURCHASE SUCCESSFUL! 🎉

📦 {product['name']}
📅 {duration['name']}
🔑 Key: `{key}`

💝 New Balance: ৳{new_balance}"""
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
        
        bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                                reply_markup=markup, parse_mode="Markdown")
        
        del pending_purchase[user_id]
    else:
        bot.answer_callback_query(call.id, f"❌ Insufficient balance!")

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

📦 {pending['product']['name']}
📅 {pending['duration']['name']}
💰 Amount: ৳{pending['amount']}
📱 bKash: `{BKASH_NUMBER}`
🔖 Ref: `{ref}`

Send TRX ID and screenshot"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ SEND TRX", callback_data="send_trx"))
    markup.add(InlineKeyboardButton("❌ CANCEL", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "send_trx")
def send_trx(call):
    bot.send_message(call.message.chat.id, "📝 Send TRX ID:")
    bot.register_next_step_handler(call.message, process_trx)

def process_trx(message):
    if message.text.startswith('/'):
        return
    bkash_pending[str(message.chat.id)]['trx'] = message.text
    bot.reply_to(message, "✅ TRX Saved!\n\n📸 Send screenshot:")
    bot.register_next_step_handler(message, process_screenshot)

def process_screenshot(message):
    if message.content_type != 'photo':
        bot.reply_to(message, "❌ Send screenshot!")
        bot.register_next_step_handler(message, process_screenshot)
        return
    
    pending_data = bkash_pending.get(str(message.chat.id))
    if not pending_data:
        return
    
    purchase = pending_data['pending']
    product = purchase['product']
    duration = purchase['duration']
    
    admin_text = f"""🆕 NEW ORDER

👤 User: {message.chat.id}
📦 {product['name']} - {duration['name']}
💰 ৳{purchase['amount']}
🔢 TRX: {pending_data['trx']}"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_{message.chat.id}"),
        InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{message.chat.id}")
    )
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text, reply_markup=markup)
    bot.send_message(message.chat.id, "✅ Sent to admin!")
    del bkash_pending[str(message.chat.id)]

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve_order(call):
    if call.from_user.id != ADMIN_ID:
        return
    
    uid = int(call.data.replace("approve_", ""))
    
    # Find pending order
    for user_id, pending in list(pending_purchase.items()):
        if int(user_id) == uid:
            product = pending['product']
            duration = pending['duration']
            
            if product['keys']:
                key = product['keys'].pop(0)
                product['stock'] -= 1
                save_db('products.json', products_db)
            else:
                key = "OUT OF STOCK"
            
            users_db[str(uid)]['orders'].append({
                "product": product['name'],
                "duration": duration['name'],
                "amount": pending['amount'],
                "key": key,
                "date": str(datetime.now())
            })
            save_db('users.json', users_db)
            
            bot.send_message(uid, f"✅ APPROVED!\n🔑 Key: `{key}`", parse_mode="Markdown")
            bot.send_message(ADMIN_ID, f"✅ Approved user {uid}")
            bot.answer_callback_query(call.id, "Approved!")
            del pending_purchase[user_id]
            break

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject(call):
    if call.from_user.id != ADMIN_ID:
        return
    
    uid = int(call.data.replace("reject_", ""))
    bot.send_message(uid, "❌ REJECTED!")
    bot.send_message(ADMIN_ID, f"❌ Rejected user {uid}")
    bot.answer_callback_query(call.id, "Rejected!")

# ====================== WALLET VIEW ======================
@bot.callback_query_handler(func=lambda call: call.data == "wallet")
def view_wallet(call):
    balance = get_balance(call.message.chat.id)
    text = f"💰 Balance: ৳{balance}"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# ====================== ORDERS ======================
@bot.callback_query_handler(func=lambda call: call.data == "orders")
def view_orders(call):
    user = users_db.get(str(call.message.chat.id), {})
    orders_list = user.get('orders', [])
    
    if not orders_list:
        text = "📭 No orders yet!"
    else:
        text = "📦 YOUR ORDERS:\n\n"
        for o in orders_list[-5:]:
            text += f"📦 {o['product']} ({o.get('duration', 'N/A')})\n💰 ৳{o['amount']}\n🔑 `{o['key']}`\n\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== ADD BALANCE ======================
@bot.callback_query_handler(func=lambda call: call.data == "add_balance")
def add_balance_menu(call):
    bot.send_message(call.message.chat.id, "Send: `500 8Y7X9K2M4N`", parse_mode="Markdown")
    bot.register_next_step_handler(call.message, process_add)

def process_add(message):
    try:
        amt, trx = message.text.split()
        admin_text = f"💰 BALANCE REQUEST\nUser: {message.chat.id}\nAmount: ৳{amt}\nTRX: {trx}"
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ APPROVE", callback_data=f"addbal_{message.chat.id}_{amt}"),
            InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{message.chat.id}")
        )
        bot.send_message(ADMIN_ID, admin_text, reply_markup=markup)
        bot.reply_to(message, "Request sent!")
    except:
        bot.reply_to(message, "Wrong format!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("addbal_"))
def approve_add(call):
    if call.from_user.id != ADMIN_ID:
        return
    _, uid, amt = call.data.split("_")
    add_balance(int(uid), int(amt))
    bot.send_message(int(uid), f"✅ ৳{amt} added!")
    bot.answer_callback_query(call.id, "Added!")

# ====================== LUCKY SPIN ======================
spin_cd = {}

@bot.callback_query_handler(func=lambda call: call.data == "spin")
def spin(call):
    uid = str(call.message.chat.id)
    if uid in spin_cd:
        last = datetime.fromisoformat(spin_cd[uid])
        if datetime.now() - last < timedelta(hours=24):
            bot.answer_callback_query(call.id, "Come back tomorrow!")
            return
    
    prizes = [5, 10, 20, 50, 0, 0, 5, 10]
    prize = random.choice(prizes)
    
    if prize > 0:
        add_balance(uid, prize)
        text = f"🎉 You won ৳{prize}!"
    else:
        text = "😢 Better luck next time!"
    
    spin_cd[uid] = str(datetime.now())
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# ====================== HOME ======================
@bot.callback_query_handler(func=lambda call: call.data == "home")
def home(call):
    balance = get_balance(call.message.chat.id)
    welcome = f"✨ Welcome back!\n💰 Balance: ৳{balance}"
    bot.edit_message_caption(welcome, call.message.chat.id, call.message.message_id, reply_markup=main_menu())

# ====================== ADMIN ======================
@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.chat.id != ADMIN_ID:
        return
    bot.reply_to(message, "/addbalance UID AMOUNT\n/addkey PID|KEY\n/products\n/users\n/stats")

@bot.message_handler(commands=['addkey'])
def addkey_cmd(message):
    if message.chat.id != ADMIN_ID:
        return
    try:
        _, pid, key = message.text.split("|")
        products_db[pid]['keys'].append(key.upper())
        products_db[pid]['stock'] += 1
        save_db('products.json', products_db)
        bot.reply_to(message, f"✅ Key added: {key}")
    except:
        bot.reply_to(message, "❌ /addkey PID|KEY")

@bot.message_handler(commands=['products'])
def products_cmd(message):
    if message.chat.id != ADMIN_ID:
        return
    text = "📦 PRODUCTS:\n"
    for pid, p in products_db.items():
        text += f"{pid}. {p['name']} | Stock: {p['stock']}\n"
    bot.reply_to(message, text)

@bot.message_handler(commands=['users'])
def users_cmd(message):
    if message.chat.id != ADMIN_ID:
        return
    text = "👥 USERS:\n"
    for uid, u in list(users_db.items())[:20]:
        text += f"{uid} | {u.get('name', 'Unknown')}\n"
    bot.reply_to(message, text)

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if message.chat.id != ADMIN_ID:
        return
    bot.reply_to(message, f"Users: {len(users_db)}\nProducts: {len(products_db)}")

# ====================== RUN ======================
if __name__ == "__main__":
    print("🔥 ANTO SHOP STARTED!")
    print(f"Bot: @{bot.get_me().username}")
    print(f"Admin: {ADMIN_ID}")
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
