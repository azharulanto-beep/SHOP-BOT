import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os, json, random, time
from datetime import datetime, timedelta

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
BKASH_NUMBER = "01918591988"
LOGO_URL = "https://i.postimg.cc/Cxk8NxV2/istockphoto-827351040-1024x1024.jpg"

bot = telebot.TeleBot(TOKEN)

# ====================== DATABASE ======================
def load_db(f):
    try:
        with open(f, 'r') as file:
            return json.load(file)
    except:
        return {}

def save_db(f, data):
    with open(f, 'w') as file:
        json.dump(data, file, indent=4)

users_db = load_db('users.json')
products_db = load_db('products.json')
wallet_db = load_db('wallet.json')

# ====================== PRODUCTS ======================
if not products_db:
    products_db = {
        "1": {"name": "🔥 DRIP CLINT", "price": 400, "keys": ["DRIP-001", "DRIP-002"], "stock": 2},
        "2": {"name": "🎮 BGMI ESP", "price": 299, "keys": ["BGMI-001"], "stock": 1}
    }
    save_db('products.json', products_db)

# ====================== WALLET ======================
def get_balance(uid):
    uid = str(uid)
    if uid not in wallet_db:
        wallet_db[uid] = {"balance": 0}
        save_db('wallet.json', wallet_db)
    return wallet_db[uid]["balance"]

def add_balance(uid, amount):
    uid = str(uid)
    if uid not in wallet_db:
        wallet_db[uid] = {"balance": 0}
    wallet_db[uid]["balance"] += amount
    save_db('wallet.json', wallet_db)

def deduct_balance(uid, amount):
    uid = str(uid)
    if get_balance(uid) >= amount:
        wallet_db[uid]["balance"] -= amount
        save_db('wallet.json', wallet_db)
        return True
    return False

# ====================== MENU ======================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛍️ SHOP", callback_data="shop"),
        InlineKeyboardButton("💰 WALLET", callback_data="wallet"),
        InlineKeyboardButton("🎲 SPIN", callback_data="spin"),
        InlineKeyboardButton("📞 SUPPORT", url="https://t.me/PAPAJI_ANTO")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.chat.id)
    if uid not in users_db:
        users_db[uid] = {"name": m.from_user.first_name, "orders": []}
        save_db('users.json', users_db)
    
    bal = get_balance(m.chat.id)
    bot.send_photo(m.chat.id, LOGO_URL, 
                   caption=f"✨ ANTO SHOP\nHello {m.from_user.first_name}!\n💰 Balance: ৳{bal}", 
                   reply_markup=main_menu())

# ====================== SHOP ======================
@bot.callback_query_handler(func=lambda c: c.data == "shop")
def shop(c):
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, p in products_db.items():
        markup.add(InlineKeyboardButton(f"{p['name']} - ৳{p['price']}", callback_data=f"buy_{pid}"))
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    bot.edit_message_caption("🛍️ SELECT PRODUCT:", c.message.chat.id, c.message.message_id, reply_markup=markup)

# ====================== BUY ======================
pending = {}

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(c):
    pid = c.data.split("_")[1]
    p = products_db.get(pid)
    if not p or p['stock'] <= 0:
        bot.answer_callback_query(c.id, "Out of stock!")
        return
    
    pending[str(c.message.chat.id)] = {"pid": pid, "product": p, "amount": p['price']}
    bal = get_balance(c.message.chat.id)
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💳 PAY", callback_data="pay_wallet"),
        InlineKeyboardButton("❌ CANCEL", callback_data="home")
    )
    bot.edit_message_caption(f"💳 PAYMENT\n{p['name']} - ৳{p['price']}\n💰 Balance: ৳{bal}", 
                            c.message.chat.id, c.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "pay_wallet")
def pay_wallet(c):
    uid = str(c.message.chat.id)
    pend = pending.get(uid)
    if not pend:
        return
    if deduct_balance(uid, pend['amount']):
        key = pend['product']['keys'].pop(0)
        pend['product']['stock'] -= 1
        save_db('products.json', products_db)
        
        users_db[uid]['orders'].append({
            "product": pend['product']['name'],
            "amount": pend['amount'],
            "key": key,
            "date": str(datetime.now())
        })
        save_db('users.json', users_db)
        
        bot.edit_message_caption(f"✅ PURCHASE SUCCESSFUL!\n🔑 Key: `{key}`", 
                                c.message.chat.id, c.message.message_id, 
                                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home")),
                                parse_mode="Markdown")
        del pending[uid]
    else:
        bot.answer_callback_query(c.id, "Insufficient balance!")

# ====================== WALLET ======================
@bot.callback_query_handler(func=lambda c: c.data == "wallet")
def wallet(c):
    bal = get_balance(c.message.chat.id)
    bot.edit_message_caption(f"💰 BALANCE: ৳{bal}", c.message.chat.id, c.message.message_id,
                            reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home")))

# ====================== SPIN ======================
spin_cd = {}

@bot.callback_query_handler(func=lambda c: c.data == "spin")
def spin(c):
    uid = str(c.message.chat.id)
    if uid in spin_cd:
        last = datetime.fromisoformat(spin_cd[uid])
        if datetime.now() - last < timedelta(hours=24):
            bot.answer_callback_query(c.id, "Come back tomorrow!")
            return
    
    prize = random.choice([5, 10, 20, 50, 0, 5, 10])
    if prize > 0:
        add_balance(uid, prize)
        text = f"🎉 You won ৳{prize}!"
    else:
        text = "😢 Better luck next time!"
    
    spin_cd[uid] = str(datetime.now())
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id,
                            reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home")))

# ====================== HOME ======================
@bot.callback_query_handler(func=lambda c: c.data == "home")
def home(c):
    bal = get_balance(c.message.chat.id)
    bot.edit_message_caption(f"✨ Welcome back!\n💰 Balance: ৳{bal}", 
                            c.message.chat.id, c.message.message_id, reply_markup=main_menu())

# ====================== ADMIN ======================
@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.chat.id != ADMIN_ID:
        return
    bot.reply_to(m, "/addbalance UID AMOUNT\n/addkey PID|KEY\n/products\n/users\n/stats")

@bot.message_handler(commands=['addkey'])
def addkey_cmd(m):
    if m.chat.id != ADMIN_ID:
        return
    try:
        _, pid, key = m.text.split("|")
        products_db[pid]['keys'].append(key.upper())
        products_db[pid]['stock'] += 1
        save_db('products.json', products_db)
        bot.reply_to(m, f"✅ Key added: {key}")
    except:
        bot.reply_to(m, "❌ /addkey PID|KEY")

@bot.message_handler(commands=['addbalance'])
def addbal_cmd(m):
    if m.chat.id != ADMIN_ID:
        return
    try:
        _, uid, amt = m.text.split()
        add_balance(int(uid), int(amt))
        bot.send_message(int(uid), f"💰 ৳{amt} added by admin!")
        bot.reply_to(m, f"✅ Added ৳{amt} to {uid}")
    except:
        bot.reply_to(m, "❌ /addbalance UID AMOUNT")

@bot.message_handler(commands=['products'])
def products_cmd(m):
    if m.chat.id != ADMIN_ID:
        return
    text = "📦 PRODUCTS:\n"
    for pid, p in products_db.items():
        text += f"{pid}. {p['name']} | Stock: {p['stock']}\n"
    bot.reply_to(m, text)

@bot.message_handler(commands=['users'])
def users_cmd(m):
    if m.chat.id != ADMIN_ID:
        return
    text = "👥 USERS:\n"
    for uid, u in list(users_db.items())[:20]:
        text += f"{uid} | {u.get('name', 'Unknown')}\n"
    bot.reply_to(m, text)

@bot.message_handler(commands=['stats'])
def stats_cmd(m):
    if m.chat.id != ADMIN_ID:
        return
    bot.reply_to(m, f"Users: {len(users_db)}\nProducts: {len(products_db)}")

# ====================== RUN ======================
if __name__ == "__main__":
    print("🔥 ANTO SHOP BOT STARTED!")
    print(f"Bot: @{bot.get_me().username}")
    print(f"Admin: {ADMIN_ID}")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)
