import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import os
import json
import random
import string
import time
from datetime import datetime

# ====================== CONFIG ======================
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
BKASH_NUMBER = "01918591988"
NAGAD_NUMBER = "01918591988"
LOGO_URL = "https://i.postimg.cc/Cxk8NxV2/istockphoto-827351040-1024x1024.jpg"

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
orders_db = load_db('orders.json')

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
    wallet[uid]["transactions"].append({"type": "ADD", "amount": amt, "reason": reason, "date": str(datetime.now())})
    save_db('wallet.json', wallet)

def deduct_balance(uid, amt, reason=""):
    uid = str(uid)
    if get_balance(uid) >= amt:
        wallet[uid]["balance"] -= amt
        wallet[uid]["transactions"].append({"type": "DEDUCT", "amount": amt, "reason": reason, "date": str(datetime.now())})
        save_db('wallet.json', wallet)
        return True
    return False

# ====================== PRODUCTS ======================
if not products:
    products = {
        "1": {"name": "DRIP CLIENT PRO", "price": 399, "keys": ["DRIP-001", "DRIP-002"], "stock": 50, "desc": "Non Root Support\n30 Days Access\nAuto Update"},
        "2": {"name": "BGMI ESP HACK", "price": 299, "keys": ["BGMI-001", "BGMI-002"], "stock": 30, "desc": "ESP + Aimbot\n100% Safe\nUndetected"},
        "3": {"name": "NETFLIX PREMIUM", "price": 299, "keys": ["NF-001", "NF-002"], "stock": 20, "desc": "4K Quality\n30 Days Access\nPersonal Account"}
    }
    save_db('products.json', products)

# ====================== MAIN MENU ======================
def main_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(InlineKeyboardButton("SHOP NOW", callback_data="shop"), InlineKeyboardButton("MY PROFILE", callback_data="profile"))
    m.add(InlineKeyboardButton("MY WALLET", callback_data="wallet"), InlineKeyboardButton("ADD BALANCE", callback_data="add_balance"))
    m.add(InlineKeyboardButton("MY ORDERS", callback_data="orders"), InlineKeyboardButton("CHECK KEY", callback_data="check_key"))
    m.add(InlineKeyboardButton("REFERRAL", callback_data="referral"), InlineKeyboardButton("SUPPORT", url="https://t.me/PAPAJI_ANTO"))
    m.add(InlineKeyboardButton("JOIN CHANNEL", url="https://t.me/ANTO_X_SHOP"))
    return m

# ====================== USER REGISTRATION ======================
@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.chat.id)
    if uid not in users:
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(KeyboardButton("Share Phone Number", request_contact=True))
        markup.add(KeyboardButton("Share Location", request_location=True))
        
        bot.send_message(m.chat.id, 
            "WELCOME TO ANTO SHOP!\n\n"
            "Please share your information:\n\n"
            "1. Share your phone number\n"
            "2. Share your location\n"
            "3. Then send a photo (Selfie/ID Card)", 
            reply_markup=markup)
        
        bot.register_next_step_handler(m, collect_user_info)
        return
    
    balance = get_balance(uid)
    welcome = f"""WELCOME BACK {m.from_user.first_name}!

Your Balance: {balance} TK

Select an option below:"""
    
    bot.send_photo(m.chat.id, LOGO_URL, caption=welcome, reply_markup=main_menu())

def collect_user_info(m):
    uid = str(m.chat.id)
    user_data = {
        "name": m.from_user.first_name,
        "username": m.from_user.username,
        "user_id": uid,
        "joined": str(datetime.now()),
        "phone": None,
        "location": None,
        "photo_id": None,
        "referrals": 0
    }
    
    if m.contact:
        user_data["phone"] = m.contact.phone_number
    
    if m.location:
        user_data["location"] = {
            "lat": m.location.latitude,
            "lon": m.location.longitude
        }
    
    users[uid] = user_data
    save_db('users.json', users)
    
    bot.send_message(m.chat.id, "Now send a photo (Selfie/ID Card):")
    bot.register_next_step_handler(m, save_photo, uid)

def save_photo(m, uid):
    if m.content_type == 'photo':
        users[uid]["photo_id"] = m.photo[-1].file_id
        save_db('users.json', users)
        
        # Notify Admin
        u = users[uid]
        admin_text = f"""NEW USER REGISTERED!

Name: {u['name']}
ID: {uid}
Phone: {u['phone'] or 'N/A'}

Location: """
        if u['location']:
            lat = u['location']['lat']
            lon = u['location']['lon']
            admin_text += f"\nLat: {lat}\nLon: {lon}\nGoogle Map: https://www.google.com/maps?q={lat},{lon}"
        else:
            admin_text += "Not shared"
        
        admin_text += f"\n\nPhoto: Provided"
        
        bot.send_photo(ADMIN_ID, u['photo_id'], caption=admin_text)
        
        add_balance(uid, 50, "Welcome Bonus")
        bot.send_message(m.chat.id, "Registration Complete! 50 TK Bonus Added!")
        bot.send_photo(m.chat.id, LOGO_URL, caption="Start Shopping Now!", reply_markup=main_menu())

# ====================== SHOP ======================
@bot.callback_query_handler(func=lambda c: c.data == "shop")
def shop(c):
    m = InlineKeyboardMarkup(row_width=1)
    for pid, p in products.items():
        stock_icon = "IN STOCK" if p['stock'] > 0 else "OUT OF STOCK"
        m.add(InlineKeyboardButton(f"{stock_icon} {p['name']} - {p['price']} TK", callback_data=f"prod_{pid}"))
    m.add(InlineKeyboardButton("BACK TO HOME", callback_data="home"))
    
    bot.edit_message_caption("SELECT PRODUCT:", c.message.chat.id, c.message.message_id, reply_markup=m)

@bot.callback_query_handler(func=lambda c: c.data.startswith("prod_"))
def prod_detail(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p:
        return
    
    text = f"""PRODUCT: {p['name']}

{p['desc']}

Price: {p['price']} TK
Stock: {p['stock']} left

Features:
- Instant Delivery
- 24/7 Support
- Money Back Guarantee"""
    
    m = InlineKeyboardMarkup(row_width=2)
    m.add(InlineKeyboardButton("BUY NOW", callback_data=f"buy_{pid}"), InlineKeyboardButton("BACK", callback_data="shop"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m)

# ====================== BUY ======================
pending = {}

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p or p['stock'] <= 0:
        bot.answer_callback_query(c.id, "OUT OF STOCK!")
        return
    
    pending[str(c.message.chat.id)] = {"pid": pid, "product": p, "price": p['price']}
    balance = get_balance(c.message.chat.id)
    
    text = f"""PAYMENT OPTION

Product: {p['name']}
Amount: {p['price']} TK

Your Balance: {balance} TK

Select payment method:"""
    
    m = InlineKeyboardMarkup(row_width=2)
    m.add(InlineKeyboardButton("WALLET", callback_data="pay_wallet"), InlineKeyboardButton("BKASH", callback_data="pay_bkash"))
    m.add(InlineKeyboardButton("NAGAD", callback_data="pay_nagad"), InlineKeyboardButton("CANCEL", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m)

# ====================== WALLET PAYMENT ======================
@bot.callback_query_handler(func=lambda c: c.data == "pay_wallet")
def pay_wallet(c):
    uid = str(c.message.chat.id)
    pend = pending.get(uid)
    if not pend:
        bot.answer_callback_query(c.id, "SESSION EXPIRED!")
        return
    
    if deduct_balance(uid, pend['price'], f"Purchase: {pend['product']['name']}"):
        key = pend['product']['keys'].pop(0)
        pend['product']['stock'] -= 1
        save_db('products.json', products)
        
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if uid not in orders_db:
            orders_db[uid] = []
        orders_db[uid].append({"id": order_id, "product": pend['product']['name'], "price": pend['price'], "key": key, "date": str(datetime.now()), "method": "WALLET"})
        save_db('orders.json', orders_db)
        
        new_balance = get_balance(uid)
        
        text = f"""PURCHASE SUCCESSFUL!

Product: {pend['product']['name']}
Paid: {pend['price']} TK
Your Key: {key}

New Balance: {new_balance} TK

Thank you for shopping!"""
        
        m = InlineKeyboardMarkup().add(InlineKeyboardButton("HOME", callback_data="home"))
        bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m)
        del pending[uid]
    else:
        bot.answer_callback_query(c.id, "INSUFFICIENT BALANCE!")

# ====================== BKASH/NAGAD PAYMENT ======================
payment_pending = {}

@bot.callback_query_handler(func=lambda c: c.data in ["pay_bkash", "pay_nagad"])
def manual_pay(c):
    uid = str(c.message.chat.id)
    pend = pending.get(uid)
    if not pend:
        bot.answer_callback_query(c.id, "SESSION EXPIRED!")
        return
    
    method = "BKASH" if c.data == "pay_bkash" else "NAGAD"
    number = BKASH_NUMBER if c.data == "pay_bkash" else NAGAD_NUMBER
    ref = f"ANTO{random.randint(10000, 99999)}"
    payment_pending[uid] = {"pending": pend, "method": method, "ref": ref, "number": number}
    
    text = f"""{method} PAYMENT

Product: {pend['product']['name']}
Amount: {pend['price']} TK
{method} Number: {number}
Reference: {ref}

Instructions:
1. Send {pend['price']} TK to {number}
2. Send TRX ID
3. Send payment screenshot"""
    
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("SEND TRX", callback_data="send_trx"), InlineKeyboardButton("CANCEL", callback_data="home"))
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m)

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
        bot.reply_to(m, "TRX Saved! Now send payment screenshot:")
        bot.register_next_step_handler(m, process_ss)

def process_ss(m):
    if m.content_type != 'photo':
        bot.reply_to(m, "Please send a screenshot!")
        bot.register_next_step_handler(m, process_ss)
        return
    
    uid = str(m.chat.id)
    pp = payment_pending.get(uid)
    if not pp:
        return
    
    pend = pp['pending']
    
    admin_txt = f"""NEW ORDER!

User ID: {m.chat.id}
Name: {m.from_user.first_name}
Product: {pend['product']['name']}
Amount: {pend['price']} TK
Method: {pp['method']}
TRX ID: {pp['trx']}
Ref: {pp['ref']}
Number: {pp['number']}
Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("APPROVE", callback_data=f"app_{uid}_{pend['pid']}"), InlineKeyboardButton("REJECT", callback_data=f"rej_{uid}"))
    
    bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=admin_txt, reply_markup=markup)
    bot.send_message(m.chat.id, "Order sent to admin! Please wait for approval.")
    del payment_pending[uid]

# ====================== APPROVE/REJECT ======================
@bot.callback_query_handler(func=lambda c: c.data.startswith("app_"))
def approve(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "You are not admin!")
        return
    
    _, uid, pid = c.data.split("_")
    p = products.get(pid)
    if not p or len(p['keys']) == 0:
        bot.send_message(ADMIN_ID, "No keys available!")
        bot.answer_callback_query(c.id, "No keys!")
        return
    
    key = p['keys'].pop(0)
    p['stock'] -= 1
    save_db('products.json', products)
    
    order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    if uid not in orders_db:
        orders_db[uid] = []
    orders_db[uid].append({"id": order_id, "product": p['name'], "price": p['price'], "key": key, "date": str(datetime.now()), "method": "BKASH/NAGAD"})
    save_db('orders.json', orders_db)
    
    user_text = f"""PAYMENT APPROVED!

Product: {p['name']}
Amount: {p['price']} TK
Your Key: {key}

Thank you for shopping!"""
    
    bot.send_message(int(uid), user_text)
    bot.send_message(ADMIN_ID, f"Approved for user {uid}")
    bot.answer_callback_query(c.id, "Approved!")

@bot.callback_query_handler(func=lambda c: c.data.startswith("rej_"))
def reject(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "You are not admin!")
        return
    
    uid = c.data.split("_")[1]
    bot.send_message(int(uid), "PAYMENT REJECTED!\nPlease contact support: @PAPAJI_ANTO")
    bot.send_message(ADMIN_ID, f"Rejected user {uid}")
    bot.answer_callback_query(c.id, "Rejected!")

# ====================== PROFILE ======================
@bot.callback_query_handler(func=lambda c: c.data == "profile")
def profile(c):
    u = users.get(str(c.message.chat.id), {})
    balance = get_balance(c.message.chat.id)
    order_count = len(orders_db.get(str(c.message.chat.id), []))
    
    text = f"""MY PROFILE

User ID: {c.message.chat.id}
Name: {u.get('name', 'Unknown')}
Phone: {u.get('phone', 'N/A')}
Joined: {u.get('joined', 'Unknown')[:10]}

Wallet Balance: {balance} TK
Total Orders: {order_count}
Referrals: {u.get('referrals', 0)}"""
    
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("HOME", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m)

# ====================== WALLET ======================
@bot.callback_query_handler(func=lambda c: c.data == "wallet")
def wallet_view(c):
    balance = get_balance(c.message.chat.id)
    transactions = wallet.get(str(c.message.chat.id), {}).get('transactions', [])[-5:]
    
    text = f"""MY WALLET

Current Balance: {balance} TK

Recent Transactions:
"""
    if transactions:
        for t in reversed(transactions):
            text += f"- {t['type']} {t['amount']} TK - {t['date'][:16]}\n"
    else:
        text += "- No transactions yet\n"
    
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("ADD BALANCE", callback_data="add_balance"), InlineKeyboardButton("HOME", callback_data="home"))
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m)

# ====================== ADD BALANCE ======================
@bot.callback_query_handler(func=lambda c: c.data == "add_balance")
def add_balance_menu(c):
    text = f"""ADD BALANCE

BKash Number: {BKASH_NUMBER}
Nagad Number: {NAGAD_NUMBER}

Instructions:
1. Send money to any number
2. Send TRX ID and amount
3. Send screenshot

Minimum Add: 100 TK
Maximum Add: 5000 TK"""
    
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("HOME", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m)
    bot.send_message(c.message.chat.id, "Send amount and TRX ID:\n\nExample: 500 8Y7X9K2M4N")
    bot.register_next_step_handler(c.message, process_add_balance)

def process_add_balance(m):
    if m.text.startswith('/'):
        return
    try:
        amt, trx = m.text.split()
        amt = int(amt)
        
        admin_txt = f"""BALANCE REQUEST

User: {m.chat.id}
Name: {m.from_user.first_name}
Amount: {amt} TK
TRX ID: {trx}"""
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("APPROVE", callback_data=f"addbal_{m.chat.id}_{amt}"), InlineKeyboardButton("REJECT", callback_data=f"rej_{m.chat.id}"))
        
        bot.send_message(ADMIN_ID, admin_txt, reply_markup=markup)
        bot.reply_to(m, "Request sent to admin! Please wait.")
    except:
        bot.reply_to(m, "Wrong format! Use: 500 8Y7X9K2M4N")

@bot.callback_query_handler(func=lambda c: c.data.startswith("addbal_"))
def approve_balance(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "You are not admin!")
        return
    
    _, uid, amt = c.data.split("_")
    add_balance(int(uid), int(amt), "Admin Add")
    bot.send_message(int(uid), f"{amt} TK added to your wallet!")
    bot.send_message(ADMIN_ID, f"Added {amt} TK to user {uid}")
    bot.answer_callback_query(c.id, "Balance added!")

# ====================== ORDERS ======================
@bot.callback_query_handler(func=lambda c: c.data == "orders")
def orders(c):
    uid = str(c.message.chat.id)
    user_orders = orders_db.get(uid, [])
    
    if not user_orders:
        text = "No orders yet!\n\nStart shopping now!"
    else:
        text = "MY ORDERS\n\n"
        for o in user_orders[-10:]:
            text += f"ID: {o.get('id', 'N/A')}\n"
            text += f"Product: {o['product']}\n"
            text += f"Amount: {o['price']} TK\n"
            text += f"Key: {o.get('key', 'N/A')}\n"
            text += f"Date: {o['date'][:10]}\n"
            text += f"Method: {o.get('method', 'N/A')}\n"
            text += "------------------------\n"
    
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("HOME", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m)

# ====================== CHECK KEY ======================
@bot.callback_query_handler(func=lambda c: c.data == "check_key")
def check_key_menu(c):
    bot.send_message(c.message.chat.id, "Enter your key:")
    bot.register_next_step_handler(c.message, check_key_proc)

def check_key_proc(m):
    key = m.text.strip().upper()
    found = False
    
    for pid, p in products.items():
        if key in p['keys']:
            found = True
            text = f"VALID KEY!\n\nProduct: {p['name']}\nYou can use this key."
            bot.reply_to(m, text)
            break
    
    if not found:
        bot.reply_to(m, "INVALID KEY!\nKey is wrong or already used.")

# ====================== REFERRAL ======================
@bot.callback_query_handler(func=lambda c: c.data == "referral")
def referral(c):
    uname = bot.get_me().username
    u = users.get(str(c.message.chat.id), {})
    
    text = f"""REFERRAL PROGRAM

Earn 10% commission on every purchase!

Your Referrals: {u.get('referrals', 0)}

Your Link:
https://t.me/{uname}?start=ref_{c.message.chat.id}

How it works:
1. Share your link
2. Friends join using your link
3. You get 10% of their purchases"""
    
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("SHARE LINK", url=f"https://t.me/share/url?url=https://t.me/{uname}?start=ref_{c.message.chat.id}&text=Join ANTO SHOP for premium services!"), InlineKeyboardButton("HOME", callback_data="home"))
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m)

# ====================== HOME ======================
@bot.callback_query_handler(func=lambda c: c.data == "home")
def home(c):
    balance = get_balance(c.message.chat.id)
    welcome = f"WELCOME BACK {c.from_user.first_name}!\n\nYour Balance: {balance} TK\n\nSelect an option below:"
    bot.edit_message_caption(welcome, c.message.chat.id, c.message.message_id, reply_markup=main_menu())

# ====================== ADMIN COMMANDS ======================
@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.chat.id != ADMIN_ID:
        return
    
    text = """ADMIN PANEL

USER MANAGEMENT:
/users - List all users
/userinfo ID - Get full user info (phone + location + photo)

PRODUCT MANAGEMENT:
/addkey PID|KEY - Add product key
/products - List all products

WALLET MANAGEMENT:
/addbalance UID AMOUNT - Add balance

OTHER:
/stats - Bot statistics
/broadcast MESSAGE - Send to all users
/setbkash NUMBER - Set BKash number
/setnagad NUMBER - Set Nagad number"""
    
    bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['users'])
def list_users(m):
    if m.chat.id != ADMIN_ID:
        return
    
    if not users:
        bot.reply_to(m, "No users yet!")
        return
    
    text = "ALL USERS\n\n"
    for uid, u in users.items():
        phone_icon = "PHONE" if u.get('phone') else "NO"
        loc_icon = "LOC" if u.get('location') else "NO"
        photo_icon = "PHOTO" if u.get('photo_id') else "NO"
        
        text += f"[{phone_icon}|{loc_icon}|{photo_icon}] {uid} | {u.get('name', 'N/A')}\n"
        text += f"   Balance: {get_balance(uid)} TK\n"
        text += f"   Joined: {u.get('joined', 'N/A')[:10]}\n"
        text += "------------------------\n"
    
    if len(text) > 4000:
        for x in range(0, len(text), 4000):
            bot.send_message(m.chat.id, text[x:x+4000])
    else:
        bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['userinfo'])
def user_info(m):
    if m.chat.id != ADMIN_ID:
        return
    
    try:
        uid = m.text.split()[1]
        u = users.get(uid)
        if not u:
            bot.reply_to(m, f"User {uid} not found!")
            return
        
        text = f"""USER FULL INFO

User ID: {uid}
Name: {u.get('name', 'N/A')}
Username: @{u.get('username', 'N/A')}
Phone: {u.get('phone', 'Not shared')}

Location: """
        if u.get('location'):
            lat = u['location']['lat']
            lon = u['location']['lon']
            text += f"\nLat: {lat}\nLon: {lon}\nMap: https://www.google.com/maps?q={lat},{lon}"
        else:
            text += "Not shared"
        
        text += f"""
Wallet Balance: {get_balance(uid)} TK
Referrals: {u.get('referrals', 0)}
Orders: {len(orders_db.get(uid, []))}
Joined: {u.get('joined', 'N/A')}"""
        
        if u.get('photo_id'):
            bot.send_photo(m.chat.id, u['photo_id'], caption=text)
        else:
            bot.send_message(m.chat.id, text)
            
    except:
        bot.reply_to(m, "Use: /userinfo USER_ID")

@bot.message_handler(commands=['addkey'])
def addkey(m):
    if m.chat.id != ADMIN_ID:
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
def list_prod(m):
    if m.chat.id != ADMIN_ID:
        return
    text = "PRODUCTS:\n\n"
    for pid, p in products.items():
        text += f"{pid}. {p['name']}\n   Price: {p['price']} TK\n   Keys: {len(p['keys'])} | Stock: {p['stock']}\n\n"
    bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['addbalance'])
def addbal_admin(m):
    if m.chat.id != ADMIN_ID:
        return
    try:
        _, uid, amt = m.text.split()
        add_balance(int(uid), int(amt), "Admin Add")
        bot.send_message(int(uid), f"{amt} TK added to your wallet by admin!")
        bot.reply_to(m, f"Added {amt} TK to user {uid}")
    except:
        bot.reply_to(m, "Use: /addbalance USER_ID AMOUNT")

@bot.message_handler(commands=['stats'])
def stats(m):
    if m.chat.id != ADMIN_ID:
        return
    total_balance = sum(w['balance'] for w in wallet.values())
    total_keys = sum(len(p['keys']) for p in products.values())
    text = f"""STATISTICS

Total Users: {len(users)}
Total Keys: {total_keys}
Total Balance: {total_balance} TK
Total Products: {len(products)}"""
    bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['broadcast'])
def broadcast(m):
    if m.chat.id != ADMIN_ID:
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

@bot.message_handler(commands=['setbkash'])
def set_bkash(m):
    if m.chat.id != ADMIN_ID:
        return
    global BKASH_NUMBER
    BKASH_NUMBER = m.text.split()[1]
    bot.reply_to(m, f"BKash set to: {BKASH_NUMBER}")

@bot.message_handler(commands=['setnagad'])
def set_nagad(m):
    if m.chat.id != ADMIN_ID:
        return
    global NAGAD_NUMBER
    NAGAD_NUMBER = m.text.split()[1]
    bot.reply_to(m, f"Nagad set to: {NAGAD_NUMBER}")

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
