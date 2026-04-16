import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import os
import json
import random
import string
import time
from datetime import datetime

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
pending_reg = load_db('pending_reg.json')
products = load_db('products.json')
wallet = load_db('wallet.json')
orders_db = load_db('orders.json')

# ====================== WALLET ======================
def get_balance(uid):
    uid = str(uid)
    if uid not in wallet:
        wallet[uid] = {"balance": 0}
        save_db('wallet.json', wallet)
    return wallet[uid]["balance"]

def add_balance(uid, amt):
    uid = str(uid)
    if uid not in wallet:
        wallet[uid] = {"balance": 0}
    wallet[uid]["balance"] += amt
    save_db('wallet.json', wallet)

# ====================== PRODUCTS ======================
if not products:
    products = {
        "1": {"name": "DRIP CLIENT PRO", "price": 399, "keys": ["DRIP-001"], "stock": 50},
        "2": {"name": "BGMI ESP HACK", "price": 299, "keys": ["BGMI-001"], "stock": 30},
        "3": {"name": "NETFLIX PREMIUM", "price": 299, "keys": ["NF-001"], "stock": 20}
    }
    save_db('products.json', products)

# ====================== MAIN MENU ======================
def main_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(InlineKeyboardButton("SHOP", callback_data="shop"), InlineKeyboardButton("PROFILE", callback_data="profile"))
    m.add(InlineKeyboardButton("WALLET", callback_data="wallet"), InlineKeyboardButton("ORDERS", callback_data="orders"))
    m.add(InlineKeyboardButton("SUPPORT", url="https://t.me/PAPAJI_ANTO"))
    return m

def show_main_menu(m):
    balance = get_balance(m.chat.id)
    welcome = f"WELCOME {m.from_user.first_name}!\n\nBalance: {balance} TK"
    bot.send_photo(m.chat.id, LOGO_URL, caption=welcome, reply_markup=main_menu())

# ====================== FORCED REGISTRATION (Phone + Location + Photo) ======================
@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.chat.id)
    
    # Check if already registered
    if uid in users and users[uid].get("fully_registered", False):
        show_main_menu(m)
        return
    
    # Start registration
    if uid not in pending_reg:
        pending_reg[uid] = {"step": "phone", "data": {}}
        save_db('pending_reg.json', pending_reg)
    
    send_next_step(m)

def send_next_step(m):
    uid = str(m.chat.id)
    step = pending_reg[uid]["step"]
    
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    
    if step == "phone":
        markup.add(KeyboardButton("SHARE PHONE NUMBER", request_contact=True))
        bot.send_message(m.chat.id, 
            "🔐 MANDATORY REGISTRATION\n\n"
            "STEP 1/3: SHARE YOUR PHONE NUMBER\n\n"
            "Click the button below. This is MANDATORY!",
            reply_markup=markup)
        bot.register_next_step_handler(m, process_phone)
    
    elif step == "location":
        markup.add(KeyboardButton("SHARE LOCATION", request_location=True))
        bot.send_message(m.chat.id,
            "STEP 2/3: SHARE YOUR LOCATION\n\n"
            "Click the button below. This is MANDATORY!",
            reply_markup=markup)
        bot.register_next_step_handler(m, process_location)
    
    elif step == "photo":
        # Create keyboard with Gallery and Camera options
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(KeyboardButton("📸 TAKE PHOTO", request_poll=True))  # Opens camera
        markup.add(KeyboardButton("🖼️ CHOOSE FROM GALLERY", request_poll=False))  # Opens gallery
        markup.add(KeyboardButton("📷 SEND PHOTO", request_poll=False))
        
        bot.send_message(m.chat.id,
            "STEP 3/3: SEND A PHOTO\n\n"
            "Options:\n"
            "• Click 'TAKE PHOTO' to use camera\n"
            "• Click 'CHOOSE FROM GALLERY' to select existing photo\n"
            "• Or just send any photo\n\n"
            "This is MANDATORY!",
            reply_markup=markup)
        bot.register_next_step_handler(m, process_photo)

def process_phone(m):
    uid = str(m.chat.id)
    
    if m.contact:
        pending_reg[uid]["data"]["phone"] = m.contact.phone_number
        pending_reg[uid]["step"] = "location"
        save_db('pending_reg.json', pending_reg)
        send_next_step(m)
    else:
        bot.send_message(m.chat.id, "❌ You MUST share your phone number! Press the button below.", reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(KeyboardButton("SHARE PHONE NUMBER", request_contact=True)))
        bot.register_next_step_handler(m, process_phone)

def process_location(m):
    uid = str(m.chat.id)
    
    if m.location:
        pending_reg[uid]["data"]["location"] = {
            "lat": m.location.latitude,
            "lon": m.location.longitude
        }
        pending_reg[uid]["step"] = "photo"
        save_db('pending_reg.json', pending_reg)
        send_next_step(m)
    else:
        bot.send_message(m.chat.id, "❌ You MUST share your location! Press the button below.", reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(KeyboardButton("SHARE LOCATION", request_location=True)))
        bot.register_next_step_handler(m, process_location)

def process_photo(m):
    uid = str(m.chat.id)
    
    # Handle button clicks for camera/gallery
    if m.text == "📸 TAKE PHOTO":
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(KeyboardButton("📸 TAKE PHOTO", request_poll=True))
        markup.add(KeyboardButton("🖼️ CHOOSE FROM GALLERY"))
        bot.send_message(m.chat.id, "Open camera and take a photo:", reply_markup=markup)
        bot.register_next_step_handler(m, process_photo)
        return
    
    elif m.text == "🖼️ CHOOSE FROM GALLERY":
        bot.send_message(m.chat.id, "Please send a photo from your gallery:")
        bot.register_next_step_handler(m, process_photo)
        return
    
    # Check if photo received
    if m.content_type == 'photo':
        # Save user data
        user_data = pending_reg[uid]["data"]
        users[uid] = {
            "name": m.from_user.first_name,
            "username": m.from_user.username,
            "user_id": uid,
            "phone": user_data.get("phone"),
            "location": user_data.get("location"),
            "photo_id": m.photo[-1].file_id,
            "joined": str(datetime.now()),
            "fully_registered": True
        }
        save_db('users.json', users)
        
        # Add welcome bonus
        add_balance(uid, 50)
        
        # Notify admin
        u = users[uid]
        loc_text = f"Location: {u['location']['lat']}, {u['location']['lon']}" if u.get('location') else "Location: Not shared"
        
        admin_text = f"""NEW USER REGISTERED!

Name: {u['name']}
ID: {uid}
Phone: {u.get('phone', 'N/A')}
{loc_text}"""
        
        bot.send_photo(ADMIN_ID, u['photo_id'], caption=admin_text)
        
        # Clean up and show menu
        del pending_reg[uid]
        save_db('pending_reg.json', pending_reg)
        
        bot.send_message(m.chat.id, "✅ Registration Complete! 50 TK Bonus Added!")
        show_main_menu(m)
    else:
        bot.send_message(m.chat.id, "❌ You MUST send a photo! Please send a photo from camera or gallery.")
        bot.register_next_step_handler(m, process_photo)

# ====================== SHOP ======================
@bot.callback_query_handler(func=lambda c: c.data == "shop")
def shop(c):
    m = InlineKeyboardMarkup(row_width=1)
    for pid, p in products.items():
        m.add(InlineKeyboardButton(f"{p['name']} - {p['price']} TK", callback_data=f"buy_{pid}"))
    m.add(InlineKeyboardButton("BACK", callback_data="home"))
    bot.edit_message_caption("SELECT PRODUCT:", c.message.chat.id, c.message.message_id, reply_markup=m)

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p or p['stock'] <= 0:
        bot.answer_callback_query(c.id, "OUT OF STOCK!")
        return
    
    balance = get_balance(c.message.chat.id)
    
    if balance >= p['price']:
        # Deduct balance
        wallet[str(c.message.chat.id)]["balance"] -= p['price']
        save_db('wallet.json', wallet)
        
        # Get key
        key = p['keys'].pop(0)
        p['stock'] -= 1
        save_db('products.json', products)
        
        # Save order
        if str(c.message.chat.id) not in orders_db:
            orders_db[str(c.message.chat.id)] = []
        orders_db[str(c.message.chat.id)].append({
            "product": p['name'],
            "price": p['price'],
            "key": key,
            "date": str(datetime.now())
        })
        save_db('orders.json', orders_db)
        
        bot.edit_message_caption(f"✅ PURCHASE SUCCESSFUL!\n\nProduct: {p['name']}\nKey: {key}", 
                                c.message.chat.id, c.message.message_id,
                                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("HOME", callback_data="home")))
    else:
        bot.answer_callback_query(c.id, "INSUFFICIENT BALANCE!")

# ====================== PROFILE ======================
@bot.callback_query_handler(func=lambda c: c.data == "profile")
def profile(c):
    u = users.get(str(c.message.chat.id), {})
    balance = get_balance(c.message.chat.id)
    
    text = f"""MY PROFILE

ID: {c.message.chat.id}
Name: {u.get('name', 'Unknown')}
Phone: {u.get('phone', 'N/A')}
Balance: {balance} TK
Joined: {u.get('joined', 'N/A')[:10]}"""
    
    if u.get('location'):
        text += f"\nLocation: {u['location']['lat']}, {u['location']['lon']}"
    
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("HOME", callback_data="home"))
    
    if u.get('photo_id'):
        bot.send_photo(c.message.chat.id, u['photo_id'], caption=text, reply_markup=m)
    else:
        bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m)

# ====================== WALLET ======================
@bot.callback_query_handler(func=lambda c: c.data == "wallet")
def wallet_view(c):
    balance = get_balance(c.message.chat.id)
    text = f"MY WALLET\n\nBalance: {balance} TK"
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("ADD BALANCE", callback_data="add_balance"), InlineKeyboardButton("HOME", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m)

@bot.callback_query_handler(func=lambda c: c.data == "add_balance")
def add_balance_menu(c):
    text = f"ADD BALANCE\n\nBKash: {BKASH_NUMBER}\nNagad: {NAGAD_NUMBER}\n\nSend amount + TRX ID to admin"
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("HOME", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m)

# ====================== ORDERS ======================
@bot.callback_query_handler(func=lambda c: c.data == "orders")
def orders(c):
    uid = str(c.message.chat.id)
    user_orders = orders_db.get(uid, [])
    
    if not user_orders:
        text = "No orders yet!"
    else:
        text = "MY ORDERS\n\n"
        for o in user_orders[-5:]:
            text += f"Product: {o['product']}\nPrice: {o['price']} TK\nKey: {o['key']}\nDate: {o['date'][:10]}\n\n"
    
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("HOME", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m)

# ====================== HOME ======================
@bot.callback_query_handler(func=lambda c: c.data == "home")
def home(c):
    balance = get_balance(c.message.chat.id)
    welcome = f"WELCOME BACK {c.from_user.first_name}!\n\nBalance: {balance} TK"
    bot.edit_message_caption(welcome, c.message.chat.id, c.message.message_id, reply_markup=main_menu())

# ====================== ADMIN COMMANDS ======================
@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.chat.id != ADMIN_ID:
        return
    text = """ADMIN PANEL

/users - List all users
/userinfo ID - Get full user info
/addkey PID|KEY - Add product key
/products - List products
/addbalance UID AMOUNT - Add balance
/stats - Statistics
/broadcast MSG - Send to all"""
    bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['users'])
def list_users(m):
    if m.chat.id != ADMIN_ID:
        return
    
    if not users:
        bot.reply_to(m, "No users!")
        return
    
    text = "ALL USERS\n\n"
    for uid, u in users.items():
        if u.get("fully_registered"):
            phone_icon = "📞" if u.get('phone') else "❌"
            loc_icon = "📍" if u.get('location') else "❌"
            photo_icon = "📸" if u.get('photo_id') else "❌"
            text += f"{phone_icon}{loc_icon}{photo_icon} {uid} | {u.get('name', 'N/A')}\n"
            text += f"   Balance: {get_balance(uid)} TK\n"
            text += "------------------------\n"
    
    bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['userinfo'])
def user_info(m):
    if m.chat.id != ADMIN_ID:
        return
    
    try:
        uid = m.text.split()[1]
        u = users.get(uid)
        if not u or not u.get("fully_registered"):
            bot.reply_to(m, "User not found!")
            return
        
        text = f"USER INFO\n\nName: {u['name']}\nID: {uid}\nPhone: {u.get('phone', 'N/A')}\n"
        
        if u.get('location'):
            lat = u['location']['lat']
            lon = u['location']['lon']
            text += f"Location: {lat}, {lon}\nMap: https://www.google.com/maps?q={lat},{lon}\n"
        
        text += f"Balance: {get_balance(uid)} TK\nOrders: {len(orders_db.get(uid, []))}\nJoined: {u.get('joined', 'N/A')}"
        
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
        products[pid]['keys'].append(key.upper())
        products[pid]['stock'] += 1
        save_db('products.json', products)
        bot.reply_to(m, f"Key added: {key}")
    except:
        bot.reply_to(m, "Use: /addkey PID|KEY")

@bot.message_handler(commands=['products'])
def list_prod(m):
    if m.chat.id != ADMIN_ID:
        return
    text = "PRODUCTS:\n"
    for pid, p in products.items():
        text += f"{pid}. {p['name']} - {p['price']} TK | Stock: {p['stock']}\n"
    bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['addbalance'])
def add_balance_admin(m):
    if m.chat.id != ADMIN_ID:
        return
    try:
        _, uid, amt = m.text.split()
        add_balance(int(uid), int(amt))
        bot.send_message(int(uid), f"{amt} TK added to your wallet!")
        bot.reply_to(m, f"Added {amt} TK to {uid}")
    except:
        bot.reply_to(m, "Use: /addbalance UID AMOUNT")

@bot.message_handler(commands=['stats'])
def stats(m):
    if m.chat.id != ADMIN_ID:
        return
    total_balance = sum(w['balance'] for w in wallet.values())
    total_keys = sum(len(p['keys']) for p in products.values())
    text = f"STATS\n\nUsers: {len(users)}\nKeys: {total_keys}\nTotal Balance: {total_balance} TK"
    bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['broadcast'])
def broadcast(m):
    if m.chat.id != ADMIN_ID:
        return
    msg = m.text.replace("/broadcast ", "")
    count = 0
    for uid in users:
        try:
            bot.send_message(int(uid), f"📢 ANNOUNCEMENT\n\n{msg}")
            count += 1
        except:
            pass
    bot.reply_to(m, f"Sent to {count} users")

# ====================== RUN ======================
if __name__ == "__main__":
    print("=" * 50)
    print("ANTO SHOP BOT STARTED!")
    print(f"Bot: @{bot.get_me().username}")
    print(f"Admin: {ADMIN_ID}")
    print("=" * 50)
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
