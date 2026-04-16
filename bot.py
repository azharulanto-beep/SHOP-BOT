import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import json
import random
import string
import time
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ANTO@2026")
BKASH_NUMBER = os.environ.get("BKASH_NUMBER", "01918591988")
NAGAD_NUMBER = os.environ.get("NAGAD_NUMBER", "01918591988")
LOGO_URL = os.environ.get("LOGO_URL", "https://i.postimg.cc/qvt6CQjk/logo.jpg")

bot = telebot.TeleBot(TOKEN)

# ====================== DATABASE ======================
def load_db(f):
    try:
        with open(f, 'r') as file:
            return json.load(file)
    except:
        return {}

def save_db(f, d):
    with open(f, 'w') as file:
        json.dump(d, file, indent=4)

users = load_db('users.json')
products = load_db('products.json')
wallet = load_db('wallet.json')
orders = load_db('orders.json')
settings = load_db('settings.json')

# ====================== DEFAULT SETTINGS ======================
if not settings:
    settings = {
        "bot_name": "🛍️ ANTO SHOP",
        "logo_url": LOGO_URL,
        "support_url": "https://t.me/PAPAJI_ANTO",
        "channel_url": "https://t.me/ANTO_X_SHOP",
        "currency": "৳",
        "welcome_bonus": 50,
        "referral_percent": 10,
        "bkash": BKASH_NUMBER,
        "nagad": NAGAD_NUMBER
    }
    save_db('settings.json', settings)

# ====================== WALLET FUNCTIONS ======================
def get_balance(uid):
    uid = str(uid)
    if uid not in wallet:
        wallet[uid] = {"balance": 0, "transactions": []}
        save_db('wallet.json', wallet)
    return wallet[uid]["balance"]

def add_balance(uid, amt, reason=""):
    uid = str(uid)
    if uid not in wallet:
        wallet[uid] = {"balance": 0, "transactions": []}
    wallet[uid]["balance"] += amt
    wallet[uid]["transactions"].append({"type": "➕ ADD", "amount": amt, "reason": reason, "date": str(datetime.now())})
    save_db('wallet.json', wallet)

def deduct_balance(uid, amt, reason=""):
    uid = str(uid)
    if get_balance(uid) >= amt:
        wallet[uid]["balance"] -= amt
        wallet[uid]["transactions"].append({"type": "➖ DEDUCT", "amount": amt, "reason": reason, "date": str(datetime.now())})
        save_db('wallet.json', wallet)
        return True
    return False

# ====================== PRODUCTS ======================
if not products:
    products = {
        "1": {
            "name": "🔥 DRIP CLIENT PRO",
            "price": 399,
            "desc": "Non Root Support\n30 Days Access\nAuto Update",
            "keys": ["DRIP-001", "DRIP-002", "DRIP-003"],
            "stock": 50,
            "sold": 0
        },
        "2": {
            "name": "🎮 BGMI ESP HACK",
            "price": 299,
            "desc": "ESP + Aimbot\n100% Safe\nUndetected",
            "keys": ["BGMI-001", "BGMI-002", "BGMI-003"],
            "stock": 30,
            "sold": 0
        },
        "3": {
            "name": "📱 NETFLIX PREMIUM",
            "price": 299,
            "desc": "4K Ultra HD\n30 Days Access\nPersonal Account",
            "keys": ["NF-001", "NF-002", "NF-003"],
            "stock": 20,
            "sold": 0
        }
    }
    save_db('products.json', products)

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
        InlineKeyboardButton("🔗 REFERRAL", callback_data="referral")
    )
    markup.add(
        InlineKeyboardButton("📞 SUPPORT", url=settings.get("support_url")),
        InlineKeyboardButton("📢 JOIN CHANNEL", url=settings.get("channel_url"))
    )
    return markup

@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.chat.id)
    
    if uid not in users:
        users[uid] = {
            "name": m.from_user.first_name,
            "joined": str(datetime.now()),
            "referrals": 0,
            "referred_by": None
        }
        save_db('users.json', users)
        add_balance(uid, settings.get("welcome_bonus", 50), "Welcome Bonus")
    
    # Check referral
    if len(m.text.split()) > 1:
        ref_code = m.text.split()[1]
        if ref_code.startswith("ref_"):
            referrer = ref_code.replace("ref_", "")
            if referrer != str(uid) and users.get(referrer):
                users[uid]["referred_by"] = referrer
                users[referrer]["referrals"] += 1
                add_balance(referrer, settings.get("welcome_bonus", 50), "Referral Bonus")
                save_db('users.json', users)
                bot.send_message(int(referrer), f"New Referral!\n{ m.from_user.first_name} joined!")
    
    balance = get_balance(uid)
    logo = settings.get("logo_url")
    bot_name = settings.get("bot_name")
    
    welcome = f"""{bot_name}

Hello {m.from_user.first_name}!

Balance: {settings.get('currency')}{balance}

Owner: PAPAJI ANTO"""
    
    try:
        bot.send_photo(m.chat.id, logo, caption=welcome, reply_markup=main_menu())
    except:
        bot.send_message(m.chat.id, welcome, reply_markup=main_menu())

# ====================== SHOP ======================
@bot.callback_query_handler(func=lambda c: c.data == "shop")
def shop(c):
    if not products:
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("HOME", callback_data="home"))
        bot.edit_message_text("No products!", c.message.chat.id, c.message.message_id, reply_markup=markup)
        return
    
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, p in products.items():
        stock_icon = "✅" if p.get('stock', 0) > 0 else "❌"
        markup.add(InlineKeyboardButton(f"{stock_icon} {p['name']} - {settings.get('currency')}{p['price']}", callback_data=f"prod_{pid}"))
    markup.add(InlineKeyboardButton("HOME", callback_data="home"))
    
    bot.edit_message_text("SELECT PRODUCT:", c.message.chat.id, c.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("prod_"))
def prod_detail(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p:
        return
    
    text = f"""{p['name']}

{p.get('desc')}

Price: {settings.get('currency')}{p['price']}
Stock: {p.get('stock', 0)} left
Sold: {p.get('sold', 0)}

Instant Delivery
24/7 Support"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("BUY NOW", callback_data=f"buy_{pid}"), InlineKeyboardButton("BACK", callback_data="shop"))
    markup.add(InlineKeyboardButton("HOME", callback_data="home"))
    
    bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=markup)

# ====================== BUY SYSTEM ======================
pending_purchase = {}

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p or p.get('stock', 0) <= 0:
        bot.answer_callback_query(c.id, "OUT OF STOCK!")
        return
    
    pending_purchase[str(c.message.chat.id)] = {"pid": pid, "product": p, "price": p['price']}
    balance = get_balance(c.message.chat.id)
    
    text = f"""PAYMENT OPTION

Product: {p['name']}
Amount: {settings.get('currency')}{p['price']}

Your Balance: {settings.get('currency')}{balance}

Choose payment method:"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("WALLET", callback_data="pay_wallet"),
        InlineKeyboardButton("BKASH", callback_data="pay_bkash"),
        InlineKeyboardButton("NAGAD", callback_data="pay_nagad"),
        InlineKeyboardButton("CANCEL", callback_data="home")
    )
    
    bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=markup)

# ====================== WALLET PAYMENT ======================
@bot.callback_query_handler(func=lambda c: c.data == "pay_wallet")
def pay_wallet(c):
    uid = str(c.message.chat.id)
    pend = pending_purchase.get(uid)
    if not pend:
        bot.answer_callback_query(c.id, "Session expired!")
        return
    
    if deduct_balance(uid, pend['price'], f"Purchase: {pend['product']['name']}"):
        key = pend['product']['keys'].pop(0) if pend['product'].get('keys') else "OUT_OF_STOCK"
        pend['product']['stock'] -= 1
        pend['product']['sold'] = pend['product'].get('sold', 0) + 1
        save_db('products.json', products)
        
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        if uid not in orders:
            orders[uid] = []
        orders[uid].append({
            "id": order_id,
            "product": pend['product']['name'],
            "price": pend['price'],
            "key": key,
            "date": str(datetime.now()),
            "method": "WALLET"
        })
        save_db('orders.json', orders)
        
        new_balance = get_balance(uid)
        
        text = f"""PURCHASE SUCCESSFUL!

Product: {pend['product']['name']}
Paid: {settings.get('currency')}{pend['price']}
Key: {key}
Order ID: {order_id}

New Balance: {settings.get('currency')}{new_balance}

Thank you!"""
        
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("HOME", callback_data="home"))
        bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=markup)
        del pending_purchase[uid]
    else:
        bot.answer_callback_query(c.id, f"Insufficient balance! Need {settings.get('currency')}{pend['price'] - get_balance(uid)} more!")

# ====================== BKASH/NAGAD PAYMENT ======================
payment_pending = {}

@bot.callback_query_handler(func=lambda c: c.data in ["pay_bkash", "pay_nagad"])
def manual_pay(c):
    uid = str(c.message.chat.id)
    pend = pending_purchase.get(uid)
    if not pend:
        bot.answer_callback_query(c.id, "Session expired!")
        return
    
    method = "BKASH" if c.data == "pay_bkash" else "NAGAD"
    number = settings.get("bkash") if c.data == "pay_bkash" else settings.get("nagad")
    ref = f"ANTO{random.randint(10000, 99999)}"
    payment_pending[uid] = {"pending": pend, "method": method, "ref": ref, "number": number}
    
    text = f"""{method} PAYMENT

Product: {pend['product']['name']}
Amount: {settings.get('currency')}{pend['price']}

{method} Number: {number}
Reference: {ref}

Instructions:
1. Send {settings.get('currency')}{pend['price']} to {number}
2. Send TRX ID
3. Send payment screenshot"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("SEND TRX", callback_data="send_trx"))
    markup.add(InlineKeyboardButton("CANCEL", callback_data="home"))
    
    bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "send_trx")
def send_trx(c):
    bot.send_message(c.message.chat.id, "Send your TRX ID:")
    bot.register_next_step_handler(c.message, process_trx)

def process_trx(m):
    if m.text.startswith('/'):
        return
    uid = str(m.chat.id)
    if uid in payment_pending:
        payment_pending[uid]['trx'] = m.text
        bot.reply_to(m, "TRX Saved!\nNow send payment screenshot:")
        bot.register_next_step_handler(m, process_screenshot)

def process_screenshot(m):
    if m.content_type != 'photo':
        bot.reply_to(m, "Please send a screenshot!")
        bot.register_next_step_handler(m, process_screenshot)
        return
    
    uid = str(m.chat.id)
    pp = payment_pending.get(uid)
    if not pp:
        return
    
    pend = pp['pending']
    
    admin_text = f"""NEW ORDER!

User: {m.chat.id}
Name: {m.from_user.first_name}
Product: {pend['product']['name']}
Amount: {settings.get('currency')}{pend['price']}
Method: {pp['method']}
TRX: {pp['trx']}
Ref: {pp['ref']}
Number: {pp['number']}
Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("APPROVE", callback_data=f"approve_{uid}_{pend['pid']}"),
        InlineKeyboardButton("REJECT", callback_data=f"reject_{uid}")
    )
    
    bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=admin_text, reply_markup=markup)
    bot.send_message(m.chat.id, "Order sent to admin! Please wait.")
    del payment_pending[uid]

# ====================== APPROVE/REJECT ======================
@bot.callback_query_handler(func=lambda c: c.data.startswith("approve_"))
def approve(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "You are not admin!")
        return
    
    _, uid, pid = c.data.split("_")
    p = products.get(pid)
    if not p or len(p.get('keys', [])) == 0:
        bot.send_message(ADMIN_ID, "No keys available!")
        bot.answer_callback_query(c.id, "No keys!")
        return
    
    key = p['keys'].pop(0)
    p['stock'] -= 1
    p['sold'] = p.get('sold', 0) + 1
    save_db('products.json', products)
    
    order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    if uid not in orders:
        orders[uid] = []
    orders[uid].append({
        "id": order_id,
        "product": p['name'],
        "price": p['price'],
        "key": key,
        "date": str(datetime.now()),
        "method": "BKASH/NAGAD"
    })
    save_db('orders.json', orders)
    
    user_text = f"""PAYMENT APPROVED!

Product: {p['name']}
Amount: {settings.get('currency')}{p['price']}
Key: {key}
Order ID: {order_id}

Thank you!"""
    
    bot.send_message(int(uid), user_text)
    bot.send_message(ADMIN_ID, f"Approved for user {uid}")
    bot.answer_callback_query(c.id, "Approved!")

@bot.callback_query_handler(func=lambda c: c.data.startswith("reject_"))
def reject(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "You are not admin!")
        return
    
    uid = c.data.split("_")[1]
    bot.send_message(int(uid), "PAYMENT REJECTED!\nContact support: @PAPAJI_ANTO")
    bot.send_message(ADMIN_ID, f"Rejected user {uid}")
    bot.answer_callback_query(c.id, "Rejected!")

# ====================== PROFILE ======================
@bot.callback_query_handler(func=lambda c: c.data == "profile")
def profile(c):
    u = users.get(str(c.message.chat.id), {})
    balance = get_balance(c.message.chat.id)
    order_count = len(orders.get(str(c.message.chat.id), []))
    
    text = f"""MY PROFILE

ID: {c.message.chat.id}
Name: {u.get('name', 'Unknown')}
Joined: {u.get('joined', 'Unknown')[:10]}

Balance: {settings.get('currency')}{balance}
Orders: {order_count}
Referrals: {u.get('referrals', 0)}"""
    
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("HOME", callback_data="home"))
    bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=markup)

# ====================== WALLET VIEW ======================
@bot.callback_query_handler(func=lambda c: c.data == "wallet")
def wallet_view(c):
    balance = get_balance(c.message.chat.id)
    transactions = wallet.get(str(c.message.chat.id), {}).get('transactions', [])[-5:]
    
    text = f"""MY WALLET

Current Balance: {settings.get('currency')}{balance}

Recent Transactions:
"""
    if transactions:
        for t in reversed(transactions):
            text += f"- {t['type']} {settings.get('currency')}{t['amount']} - {t['date'][:16]}\n"
    else:
        text += "- No transactions yet\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("ADD BALANCE", callback_data="add_balance"), InlineKeyboardButton("HOME", callback_data="home"))
    
    bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=markup)

# ====================== ORDERS ======================
@bot.callback_query_handler(func=lambda c: c.data == "orders")
def orders_view(c):
    uid = str(c.message.chat.id)
    user_orders = orders.get(uid, [])
    
    if not user_orders:
        text = "NO ORDERS YET!\nStart shopping now!"
    else:
        text = "MY ORDERS\n\n"
        for o in user_orders[-10:]:
            text += f"Order: {o.get('id', 'N/A')}\n"
            text += f"Product: {o['product']}\n"
            text += f"Amount: {settings.get('currency')}{o['price']}\n"
            text += f"Key: {o.get('key', 'N/A')}\n"
            text += f"Date: {o['date'][:10]}\n"
            text += f"Method: {o.get('method', 'N/A')}\n"
            text += "------------------\n\n"
    
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("HOME", callback_data="home"))
    bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=markup)

# ====================== REFERRAL ======================
@bot.callback_query_handler(func=lambda c: c.data == "referral")
def referral(c):
    uname = bot.get_me().username
    u = users.get(str(c.message.chat.id), {})
    
    text = f"""REFERRAL PROGRAM

Earn {settings.get('referral_percent')}% commission!

Your Referrals: {u.get('referrals', 0)}

Your Link:
https://t.me/{uname}?start=ref_{c.message.chat.id}

How it works:
1. Share your link
2. Friends join using your link
3. You get {settings.get('referral_percent')}% of their purchases"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("SHARE LINK", url=f"https://t.me/share/url?url=https://t.me/{uname}?start=ref_{c.message.chat.id}"),
        InlineKeyboardButton("HOME", callback_data="home")
    )
    
    bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=markup)

# ====================== ADD BALANCE ======================
@bot.callback_query_handler(func=lambda c: c.data == "add_balance")
def add_balance_menu(c):
    text = f"""ADD BALANCE

BKash: {settings.get('bkash')}
Nagad: {settings.get('nagad')}

Instructions:
1. Send money to any number
2. Send TRX ID + Amount
3. Send screenshot

Minimum: {settings.get('currency')}100
Maximum: {settings.get('currency')}5000"""
    
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("HOME", callback_data="home"))
    bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=markup)
    bot.send_message(c.message.chat.id, "Send amount and TRX ID:\n\nExample: 500 8Y7X9K2M4N")
    bot.register_next_step_handler(c.message, process_add_balance)

def process_add_balance(m):
    try:
        amt, trx = m.text.split()
        amt = int(amt)
        
        admin_text = f"""BALANCE REQUEST

User: {m.chat.id}
Name: {m.from_user.first_name}
Amount: {settings.get('currency')}{amt}
TRX: {trx}"""
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("APPROVE", callback_data=f"addbal_{m.chat.id}_{amt}"),
            InlineKeyboardButton("REJECT", callback_data=f"reject_{m.chat.id}")
        )
        
        bot.send_message(ADMIN_ID, admin_text, reply_markup=markup)
        bot.reply_to(m, "Request sent to admin! Please wait.")
    except:
        bot.reply_to(m, "Wrong format! Use: 500 8Y7X9K2M4N")

@bot.callback_query_handler(func=lambda c: c.data.startswith("addbal_"))
def approve_balance(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "You are not admin!")
        return
    
    _, _, uid, amt = c.data.split("_")
    add_balance(int(uid), int(amt), "Admin Add")
    bot.send_message(int(uid), f"{settings.get('currency')}{amt} added to your wallet!")
    bot.send_message(ADMIN_ID, f"Added {settings.get('currency')}{amt} to user {uid}")
    bot.answer_callback_query(c.id, "Balance added!")

# ====================== HOME ======================
@bot.callback_query_handler(func=lambda c: c.data == "home")
def home(c):
    balance = get_balance(c.message.chat.id)
    bot_name = settings.get("bot_name")
    
    welcome = f"""{bot_name}

Welcome back {c.from_user.first_name}!

Balance: {settings.get('currency')}{balance}

Owner: PAPAJI ANTO"""
    
    try:
        logo = settings.get("logo_url")
        bot.send_photo(c.message.chat.id, logo, caption=welcome, reply_markup=main_menu())
    except:
        bot.send_message(c.message.chat.id, welcome, reply_markup=main_menu())

# ====================== ADMIN PANEL ======================
admin_session = {}

@bot.message_handler(commands=['admin'])
def admin_login(m):
    bot.send_message(m.chat.id, "ENTER ADMIN PASSWORD:")
    bot.register_next_step_handler(m, verify_admin)

def verify_admin(m):
    if m.text == ADMIN_PASSWORD:
        admin_session[str(m.chat.id)] = True
        show_admin_panel(m.chat.id)
    else:
        bot.send_message(m.chat.id, "WRONG PASSWORD!")

def show_admin_panel(chat_id):
    text = """ADMIN PANEL

STATISTICS:
/stats - View bot statistics

PRODUCT MANAGEMENT:
/addproduct NAME|PRICE|DESC - Add product
/addkey PID|KEY - Add product key
/products - List all products
/delproduct PID - Delete product

WALLET MANAGEMENT:
/addbalance UID AMOUNT - Add balance
/users - List all users

SETTINGS:
/setlogo URL - Change bot logo
/setname NAME - Change bot name
/setcurrency SYMBOL - Change currency
/setbkash NUMBER - Change BKash number
/setnagad NUMBER - Change Nagad number

OTHER:
/broadcast MSG - Send to all users"""
    
    bot.send_message(chat_id, text)

@bot.message_handler(commands=['stats'])
def stats(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "Access denied! Use /admin first.")
        return
    
    total_users = len(users)
    total_orders = sum(len(o) for o in orders.values())
    total_keys = sum(len(p.get('keys', [])) for p in products.values())
    total_balance = sum(w.get('balance', 0) for w in wallet.values())
    
    text = f"""BOT STATISTICS

Total Users: {total_users}
Total Orders: {total_orders}
Total Keys: {total_keys}
Total Balance: {settings.get('currency')}{total_balance}
Total Products: {len(products)}"""
    
    bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['addproduct'])
def add_product(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "Access denied! Use /admin first.")
        return
    
    try:
        _, data = m.text.split(" ", 1)
        name, price, desc = data.split("|")
        new_id = str(len(products) + 1)
        
        products[new_id] = {
            "name": name,
            "price": int(price),
            "desc": desc,
            "keys": [],
            "stock": 0,
            "sold": 0
        }
        save_db('products.json', products)
        bot.reply_to(m, f"Product added! ID: {new_id}\n{name} - {settings.get('currency')}{price}")
    except:
        bot.reply_to(m, "Use: /addproduct NAME|PRICE|DESC")

@bot.message_handler(commands=['addkey'])
def add_key(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "Access denied! Use /admin first.")
        return
    
    try:
        _, pid, key = m.text.split("|")
        if pid in products:
            products[pid]['keys'].append(key.upper())
            products[pid]['stock'] += 1
            save_db('products.json', products)
            bot.reply_to(m, f"Key added: {key}")
        else:
            bot.reply_to(m, "Product not found!")
    except:
        bot.reply_to(m, "Use: /addkey PID|KEY")

@bot.message_handler(commands=['products'])
def list_products(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "Access denied! Use /admin first.")
        return
    
    text = "PRODUCTS:\n\n"
    for pid, p in products.items():
        text += f"{pid}. {p['name']}\n   Price: {settings.get('currency')}{p['price']} | Keys: {len(p.get('keys', []))} | Stock: {p.get('stock', 0)}\n\n"
    bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['delproduct'])
def del_product(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "Access denied! Use /admin first.")
        return
    
    try:
        pid = m.text.split()[1]
        if pid in products:
            del products[pid]
            save_db('products.json', products)
            bot.reply_to(m, f"Product {pid} deleted!")
        else:
            bot.reply_to(m, "Product not found!")
    except:
        bot.reply_to(m, "Use: /delproduct PID")

@bot.message_handler(commands=['users'])
def list_users(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "Access denied! Use /admin first.")
        return
    
    text = "USERS:\n\n"
    for uid, u in list(users.items())[:30]:
        balance = get_balance(uid)
        text += f"{uid} | {u.get('name', 'Unknown')}\n   Balance: {settings.get('currency')}{balance}\n\n"
    bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['addbalance'])
def add_balance_admin(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "Access denied! Use /admin first.")
        return
    
    try:
        _, uid, amt = m.text.split()
        add_balance(int(uid), int(amt), "Admin Add")
        bot.send_message(int(uid), f"{settings.get('currency')}{amt} added to your wallet!")
        bot.reply_to(m, f"Added {settings.get('currency')}{amt} to user {uid}")
    except:
        bot.reply_to(m, "Use: /addbalance UID AMOUNT")

@bot.message_handler(commands=['setlogo'])
def set_logo(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "Access denied! Use /admin first.")
        return
    
    try:
        logo_url = m.text.split()[1]
        settings['logo_url'] = logo_url
        save_db('settings.json', settings)
        bot.reply_to(m, f"Logo updated!\n{logo_url}")
    except:
        bot.reply_to(m, "Use: /setlogo URL")

@bot.message_handler(commands=['setname'])
def set_name(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "Access denied! Use /admin first.")
        return
    
    name = m.text.replace("/setname ", "")
    settings['bot_name'] = name
    save_db('settings.json', settings)
    bot.reply_to(m, f"Bot name updated!\n{name}")

@bot.message_handler(commands=['setcurrency'])
def set_currency(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "Access denied! Use /admin first.")
        return
    
    currency = m.text.split()[1]
    settings['currency'] = currency
    save_db('settings.json', settings)
    bot.reply_to(m, f"Currency updated! {currency}")

@bot.message_handler(commands=['setbkash'])
def set_bkash(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "Access denied! Use /admin first.")
        return
    
    bkash = m.text.split()[1]
    settings['bkash'] = bkash
    save_db('settings.json', settings)
    bot.reply_to(m, f"BKash number updated! {bkash}")

@bot.message_handler(commands=['setnagad'])
def set_nagad(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "Access denied! Use /admin first.")
        return
    
    nagad = m.text.split()[1]
    settings['nagad'] = nagad
    save_db('settings.json', settings)
    bot.reply_to(m, f"Nagad number updated! {nagad}")

@bot.message_handler(commands=['broadcast'])
def broadcast(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "Access denied! Use /admin first.")
        return
    
    msg = m.text.replace("/broadcast ", "")
    count = 0
    for uid in users:
        try:
            bot.send_message(int(uid), f"ANNOUNCEMENT\n\n{msg}")
            count += 1
            time.sleep(0.05)
        except:
            pass
    bot.reply_to(m, f"Sent to {count} users")

# ====================== RUN ======================
if __name__ == "__main__":
    print("=" * 50)
    print("ANTO SHOP BOT STARTED!")
    print(f"Bot: @{bot.get_me().username}")
    print(f"Admin ID: {ADMIN_ID}")
    print("=" * 50)
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
