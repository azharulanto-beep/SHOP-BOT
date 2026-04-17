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
        "bot_name": "✨ 𝗔𝗡𝗧𝗢 𝗦𝗛𝗢𝗣 ✨",
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
            "name": "🔥 𝗗𝗥𝗜𝗣 𝗖𝗟𝗜𝗘𝗡𝗧 𝗣𝗥𝗢",
            "price": 399,
            "desc": "✅ 𝗡𝗼𝗻 𝗥𝗼𝗼𝘁 𝗦𝘂𝗽𝗽𝗼𝗿𝘁\n✅ 𝟯𝟬 𝗗𝗮𝘆𝘀 𝗔𝗰𝗰𝗲𝘀𝘀\n✅ 𝗔𝘂𝘁𝗼 𝗨𝗽𝗱𝗮𝘁𝗲",
            "keys": ["DRIP-001", "DRIP-002", "DRIP-003"],
            "stock": 50,
            "sold": 0
        },
        "2": {
            "name": "🎮 𝗕𝗚𝗠𝗜 𝗘𝗦𝗣 𝗛𝗔𝗖𝗞",
            "price": 299,
            "desc": "✅ 𝗘𝗦𝗣 + 𝗔𝗶𝗺𝗯𝗼𝘁\n✅ 𝟭𝟬𝟬% 𝗦𝗮𝗳𝗲\n✅ 𝗨𝗻𝗱𝗲𝘁𝗲𝗰𝘁𝗲𝗱",
            "keys": ["BGMI-001", "BGMI-002", "BGMI-003"],
            "stock": 30,
            "sold": 0
        },
        "3": {
            "name": "📱 𝗡𝗘𝗧𝗙𝗟𝗜𝗫 𝗣𝗥𝗘𝗠𝗜𝗨𝗠",
            "price": 299,
            "desc": "✅ 𝟰𝗞 𝗨𝗹𝘁𝗿𝗮 𝗛𝗗\n✅ 𝟯𝟬 𝗗𝗮𝘆𝘀 𝗔𝗰𝗰𝗲𝘀𝘀\n✅ 𝗣𝗲𝗿𝘀𝗼𝗻𝗮𝗹 𝗔𝗰𝗰𝗼𝘂𝗻𝘁",
            "keys": ["NF-001", "NF-002", "NF-003"],
            "stock": 20,
            "sold": 0
        }
    }
    save_db('products.json', products)

# ====================== MAIN MENU (PROFESSIONAL DESIGN) ======================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛍️ 𝗦𝗛𝗢𝗣 𝗡𝗢𝗪", callback_data="shop"),
        InlineKeyboardButton("👤 𝗠𝗬 𝗣𝗥𝗢𝗙𝗜𝗟𝗘", callback_data="profile")
    )
    markup.add(
        InlineKeyboardButton("💰 𝗠𝗬 𝗪𝗔𝗟𝗟𝗘𝗧", callback_data="wallet"),
        InlineKeyboardButton("➕ 𝗔𝗗𝗗 𝗕𝗔𝗟𝗔𝗡𝗖𝗘", callback_data="add_balance")
    )
    markup.add(
        InlineKeyboardButton("📦 𝗠𝗬 𝗢𝗥𝗗𝗘𝗥𝗦", callback_data="orders"),
        InlineKeyboardButton("🔗 𝗥𝗘𝗙𝗘𝗥𝗥𝗔𝗟", callback_data="referral")
    )
    markup.add(
        InlineKeyboardButton("📞 𝗦𝗨𝗣𝗣𝗢𝗥𝗧", url=settings.get("support_url")),
        InlineKeyboardButton("📢 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url=settings.get("channel_url"))
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
        add_balance(uid, settings.get("welcome_bonus", 50), "🎁 Welcome Bonus")
    
    # Check referral
    if len(m.text.split()) > 1:
        ref_code = m.text.split()[1]
        if ref_code.startswith("ref_"):
            referrer = ref_code.replace("ref_", "")
            if referrer != str(uid) and users.get(referrer):
                users[uid]["referred_by"] = referrer
                users[referrer]["referrals"] += 1
                add_balance(referrer, settings.get("welcome_bonus", 50), "🔗 Referral Bonus")
                save_db('users.json', users)
                bot.send_message(int(referrer), f"🎉 𝗡𝗲𝘄 𝗥𝗲𝗳𝗲𝗿𝗿𝗮𝗹!\n\n{ m.from_user.first_name} 𝗷𝗼𝗶𝗻𝗲𝗱 𝘂𝘀𝗶𝗻𝗴 𝘆𝗼𝘂𝗿 𝗹𝗶𝗻𝗸!")
    
    balance = get_balance(uid)
    logo = settings.get("logo_url")
    bot_name = settings.get("bot_name")
    
    welcome = f"""╔══════════════════════════════════════╗
║          {bot_name}          ║
╚══════════════════════════════════════╝

💝 𝗛𝗲𝗹𝗹𝗼 {m.from_user.first_name}!

💰 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: {settings.get('currency')}{balance}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 𝗢𝘄𝗻𝗲𝗿: 𝗣𝗔𝗣𝗔𝗝𝗜 𝗔𝗡𝗧𝗢
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    try:
        bot.send_photo(m.chat.id, logo, caption=welcome, reply_markup=main_menu(), parse_mode="Markdown")
    except:
        bot.send_message(m.chat.id, welcome, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== SHOP ======================
@bot.callback_query_handler(func=lambda c: c.data == "shop")
def shop(c):
    if not products:
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home"))
        bot.edit_message_caption("📭 𝗡𝗼 𝗽𝗿𝗼𝗱𝘂𝗰𝘁𝘀 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲!", c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")
        return
    
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, p in products.items():
        stock_icon = "🟢" if p.get('stock', 0) > 0 else "🔴"
        markup.add(InlineKeyboardButton(f"{stock_icon} {p['name']} - {settings.get('currency')}{p['price']}", callback_data=f"prod_{pid}"))
    markup.add(InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home"))
    
    bot.edit_message_caption("🛍️ 𝗦𝗘𝗟𝗘𝗖𝗧 𝗬𝗢𝗨𝗥 𝗣𝗥𝗢𝗗𝗨𝗖𝗧:\n━━━━━━━━━━━━━━━━━━━━", c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("prod_"))
def prod_detail(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p:
        return
    
    text = f"""╔══════════════════════════════════════╗
║              📦 𝗣𝗥𝗢𝗗𝗨𝗖𝗧              ║
╚══════════════════════════════════════╝

🔥 {p['name']}

{p.get('desc')}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 💰 𝗣𝗿𝗶𝗰𝗲: {settings.get('currency')}{p['price']}
┃ 📊 𝗦𝘁𝗼𝗰𝗸: {p.get('stock', 0)} 𝗹𝗲𝗳𝘁
┃ 📈 𝗦𝗼𝗹𝗱: {p.get('sold', 0)}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✅ 𝗜𝗻𝘀𝘁𝗮𝗻𝘁 𝗗𝗲𝗹𝗶𝘃𝗲𝗿𝘆
✅ 𝟮𝟰/𝟳 𝗦𝘂𝗽𝗽𝗼𝗿𝘁

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("🛒 𝗕𝗨𝗬 𝗡𝗢𝗪", callback_data=f"buy_{pid}"), InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data="shop"))
    markup.add(InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home"))
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== BUY SYSTEM ======================
pending_purchase = {}

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p or p.get('stock', 0) <= 0:
        bot.answer_callback_query(c.id, "❌ 𝗢𝗨𝗧 𝗢𝗙 𝗦𝗧𝗢𝗖𝗞!")
        return
    
    pending_purchase[str(c.message.chat.id)] = {"pid": pid, "product": p, "price": p['price']}
    balance = get_balance(c.message.chat.id)
    
    text = f"""╔══════════════════════════════════════╗
║            💳 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗢𝗣𝗧𝗜𝗢𝗡            ║
╚══════════════════════════════════════╝

📦 𝗣𝗿𝗼𝗱𝘂𝗰𝘁: {p['name']}
💰 𝗔𝗺𝗼𝘂𝗻𝘁: {settings.get('currency')}{p['price']}

💵 𝗬𝗼𝘂𝗿 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: {settings.get('currency')}{balance}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

𝗖𝗵𝗼𝗼𝘀𝗲 𝗽𝗮𝘆𝗺𝗲𝗻𝘁 𝗺𝗲𝘁𝗵𝗼𝗱:"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💳 𝗪𝗔𝗟𝗟𝗘𝗧", callback_data="pay_wallet"),
        InlineKeyboardButton("📱 𝗕𝗞𝗔𝗦𝗛", callback_data="pay_bkash"),
        InlineKeyboardButton("🟢 𝗡𝗔𝗚𝗔𝗗", callback_data="pay_nagad"),
        InlineKeyboardButton("❌ 𝗖𝗔𝗡𝗖𝗘𝗟", callback_data="home")
    )
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== WALLET PAYMENT ======================
@bot.callback_query_handler(func=lambda c: c.data == "pay_wallet")
def pay_wallet(c):
    uid = str(c.message.chat.id)
    pend = pending_purchase.get(uid)
    if not pend:
        bot.answer_callback_query(c.id, "❌ 𝗦𝗲𝘀𝘀𝗶𝗼𝗻 𝗲𝘅𝗽𝗶𝗿𝗲𝗱!")
        return
    
    if deduct_balance(uid, pend['price'], f"Purchase: {pend['product']['name']}"):
        key = pend['product']['keys'].pop(0) if pend['product'].get('keys') else "𝗢𝗨𝗧_𝗢𝗙_𝗦𝗧𝗢𝗖𝗞"
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
            "method": "𝗪𝗔𝗟𝗟𝗘𝗧"
        })
        save_db('orders.json', orders)
        
        new_balance = get_balance(uid)
        
        text = f"""╔══════════════════════════════════════╗
║        ✅ 𝗣𝗨𝗥𝗖𝗛𝗔𝗦𝗘 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟!        ║
╚══════════════════════════════════════╝

📦 𝗣𝗿𝗼𝗱𝘂𝗰𝘁: {pend['product']['name']}
💰 𝗣𝗮𝗶𝗱: {settings.get('currency')}{pend['price']}
🔑 𝗬𝗼𝘂𝗿 𝗞𝗲𝘆: `{key}`
🆔 𝗢𝗿𝗱𝗲𝗿 𝗜𝗗: `{order_id}`

💵 𝗡𝗲𝘄 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: {settings.get('currency')}{new_balance}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 𝗧𝗵𝗮𝗻𝗸 𝘆𝗼𝘂 𝗳𝗼𝗿 𝘀𝗵𝗼𝗽𝗽𝗶𝗻𝗴!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home"))
        bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")
        del pending_purchase[uid]
    else:
        bot.answer_callback_query(c.id, f"❌ 𝗜𝗻𝘀𝘂𝗳𝗳𝗶𝗰𝗶𝗲𝗻𝘁 𝗯𝗮𝗹𝗮𝗻𝗰𝗲! 𝗡𝗲𝗲𝗱 {settings.get('currency')}{pend['price'] - get_balance(uid)} 𝗺𝗼𝗿𝗲!")

# ====================== BKASH/NAGAD PAYMENT ======================
payment_pending = {}

@bot.callback_query_handler(func=lambda c: c.data in ["pay_bkash", "pay_nagad"])
def manual_pay(c):
    uid = str(c.message.chat.id)
    pend = pending_purchase.get(uid)
    if not pend:
        bot.answer_callback_query(c.id, "❌ 𝗦𝗲𝘀𝘀𝗶𝗼𝗻 𝗲𝘅𝗽𝗶𝗿𝗲𝗱!")
        return
    
    method = "𝗕𝗞𝗔𝗦𝗛" if c.data == "pay_bkash" else "𝗡𝗔𝗚𝗔𝗗"
    number = settings.get("bkash") if c.data == "pay_bkash" else settings.get("nagad")
    ref = f"ANTO{random.randint(10000, 99999)}"
    payment_pending[uid] = {"pending": pend, "method": method, "ref": ref, "number": number}
    
    text = f"""╔══════════════════════════════════════╗
║           💳 {method} 𝗣𝗔𝗬𝗠𝗘𝗡𝗧           ║
╚══════════════════════════════════════╝

📦 𝗣𝗿𝗼𝗱𝘂𝗰𝘁: {pend['product']['name']}
💰 𝗔𝗺𝗼𝘂𝗻𝘁: {settings.get('currency')}{pend['price']}

📱 {method} 𝗡𝘂𝗺𝗯𝗲𝗿: `{number}`
🔖 𝗥𝗲𝗳𝗲𝗿𝗲𝗻𝗰𝗲: `{ref}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 𝗜𝗻𝘀𝘁𝗿𝘂𝗰𝘁𝗶𝗼𝗻𝘀:
1️⃣ 𝗦𝗲𝗻𝗱 {settings.get('currency')}{pend['price']} 𝘁𝗼 {number}
2️⃣ 𝗦𝗲𝗻𝗱 𝗧𝗥𝗫 𝗜𝗗
3️⃣ 𝗦𝗲𝗻𝗱 𝗽𝗮𝘆𝗺𝗲𝗻𝘁 𝘀𝗰𝗿𝗲𝗲𝗻𝘀𝗵𝗼𝘁

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ 𝗦𝗘𝗡𝗗 𝗧𝗥𝗫", callback_data="send_trx"))
    markup.add(InlineKeyboardButton("❌ 𝗖𝗔𝗡𝗖𝗘𝗟", callback_data="home"))
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data == "send_trx")
def send_trx(c):
    bot.send_message(c.message.chat.id, "📝 𝗦𝗲𝗻𝗱 𝘆𝗼𝘂𝗿 𝗧𝗥𝗫 𝗜𝗗:", parse_mode="Markdown")
    bot.register_next_step_handler(c.message, process_trx)

def process_trx(m):
    if m.text.startswith('/'):
        return
    uid = str(m.chat.id)
    if uid in payment_pending:
        payment_pending[uid]['trx'] = m.text
        bot.reply_to(m, "✅ 𝗧𝗥𝗫 𝗦𝗮𝘃𝗲𝗱!\n\n📸 𝗡𝗼𝘄 𝘀𝗲𝗻𝗱 𝗽𝗮𝘆𝗺𝗲𝗻𝘁 𝘀𝗰𝗿𝗲𝗲𝗻𝘀𝗵𝗼𝘁:", parse_mode="Markdown")
        bot.register_next_step_handler(m, process_screenshot)

def process_screenshot(m):
    if m.content_type != 'photo':
        bot.reply_to(m, "❌ 𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝗮 𝘀𝗰𝗿𝗲𝗲𝗻𝘀𝗵𝗼𝘁!")
        bot.register_next_step_handler(m, process_screenshot)
        return
    
    uid = str(m.chat.id)
    pp = payment_pending.get(uid)
    if not pp:
        return
    
    pend = pp['pending']
    
    admin_text = f"""🆕 𝗡𝗘𝗪 𝗢𝗥𝗗𝗘𝗥!

👤 𝗨𝘀𝗲𝗿: `{m.chat.id}`
👤 𝗡𝗮𝗺𝗲: {m.from_user.first_name}
📦 𝗣𝗿𝗼𝗱𝘂𝗰𝘁: {pend['product']['name']}
💰 𝗔𝗺𝗼𝘂𝗻𝘁: {settings.get('currency')}{pend['price']}
💳 𝗠𝗲𝘁𝗵𝗼𝗱: {pp['method']}
🔢 𝗧𝗥𝗫 𝗜𝗗: `{pp['trx']}`
🔖 𝗥𝗲𝗳: `{pp['ref']}`
📱 𝗡𝘂𝗺𝗯𝗲𝗿: {pp['number']}
⏰ 𝗧𝗶𝗺𝗲: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘", callback_data=f"approve_{uid}_{pend['pid']}"),
        InlineKeyboardButton("❌ 𝗥𝗘𝗝𝗘𝗖𝗧", callback_data=f"reject_{uid}")
    )
    
    bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=admin_text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(m.chat.id, "✅ 𝗢𝗿𝗱𝗲𝗿 𝘀𝗲𝗻𝘁 𝘁𝗼 𝗮𝗱𝗺𝗶𝗻! 𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁.", parse_mode="Markdown")
    del payment_pending[uid]

# ====================== APPROVE/REJECT ======================
@bot.callback_query_handler(func=lambda c: c.data.startswith("approve_"))
def approve(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "❌ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗱𝗺𝗶𝗻!")
        return
    
    _, uid, pid = c.data.split("_")
    p = products.get(pid)
    if not p or len(p.get('keys', [])) == 0:
        bot.send_message(ADMIN_ID, "❌ 𝗡𝗼 𝗸𝗲𝘆𝘀 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲!")
        bot.answer_callback_query(c.id, "𝗡𝗼 𝗸𝗲𝘆𝘀!")
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
        "method": "𝗕𝗞𝗔𝗦𝗛/𝗡𝗔𝗚𝗔𝗗"
    })
    save_db('orders.json', orders)
    
    user_text = f"""╔══════════════════════════════════════╗
║        ✅ 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗!        ║
╚══════════════════════════════════════╝

📦 𝗣𝗿𝗼𝗱𝘂𝗰𝘁: {p['name']}
💰 𝗔𝗺𝗼𝘂𝗻𝘁: {settings.get('currency')}{p['price']}
🔑 𝗬𝗼𝘂𝗿 𝗞𝗲𝘆: `{key}`
🆔 𝗢𝗿𝗱𝗲𝗿 𝗜𝗗: `{order_id}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 𝗧𝗵𝗮𝗻𝗸 𝘆𝗼𝘂 𝗳𝗼𝗿 𝘀𝗵𝗼𝗽𝗽𝗶𝗻𝗴!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    bot.send_message(int(uid), user_text, parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"✅ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗳𝗼𝗿 𝘂𝘀𝗲𝗿 {uid}")
    bot.answer_callback_query(c.id, "✅ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱!")

@bot.callback_query_handler(func=lambda c: c.data.startswith("reject_"))
def reject(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "❌ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗱𝗺𝗶𝗻!")
        return
    
    uid = c.data.split("_")[1]
    bot.send_message(int(uid), "❌ 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗!\n\n𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝘀𝘂𝗽𝗽𝗼𝗿𝘁: @PAPAJI_ANTO", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"❌ 𝗥𝗲𝗷𝗲𝗰𝘁𝗲𝗱 𝘂𝘀𝗲𝗿 {uid}")
    bot.answer_callback_query(c.id, "✅ 𝗥𝗲𝗷𝗲𝗰𝘁𝗲𝗱!")

# ====================== PROFILE ======================
@bot.callback_query_handler(func=lambda c: c.data == "profile")
def profile(c):
    u = users.get(str(c.message.chat.id), {})
    balance = get_balance(c.message.chat.id)
    order_count = len(orders.get(str(c.message.chat.id), []))
    
    text = f"""╔══════════════════════════════════════╗
║              👤 𝗠𝗬 𝗣𝗥𝗢𝗙𝗜𝗟𝗘              ║
╚══════════════════════════════════════╝

🆔 𝗜𝗗: `{c.message.chat.id}`
👤 𝗡𝗮𝗺𝗲: {u.get('name', '𝗨𝗻𝗸𝗻𝗼𝘄𝗻')}
📅 𝗝𝗼𝗶𝗻𝗲𝗱: {u.get('joined', '𝗨𝗻𝗸𝗻𝗼𝘄𝗻')[:10]}

💰 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: {settings.get('currency')}{balance}
📦 𝗢𝗿𝗱𝗲𝗿𝘀: {order_count}
👥 𝗥𝗲𝗳𝗲𝗿𝗿𝗮𝗹𝘀: {u.get('referrals', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== WALLET VIEW ======================
@bot.callback_query_handler(func=lambda c: c.data == "wallet")
def wallet_view(c):
    balance = get_balance(c.message.chat.id)
    transactions = wallet.get(str(c.message.chat.id), {}).get('transactions', [])[-5:]
    
    text = f"""╔══════════════════════════════════════╗
║              💰 𝗠𝗬 𝗪𝗔𝗟𝗟𝗘𝗧              ║
╚══════════════════════════════════════╝

💵 𝗖𝘂𝗿𝗿𝗲𝗻𝘁 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: {settings.get('currency')}{balance}

📜 𝗥𝗲𝗰𝗲𝗻𝘁 𝗧𝗿𝗮𝗻𝘀𝗮𝗰𝘁𝗶𝗼𝗻𝘀:
"""
    if transactions:
        for t in reversed(transactions):
            text += f"• {t['type']} {settings.get('currency')}{t['amount']} - {t['date'][:16]}\n"
    else:
        text += "• 𝗡𝗼 𝘁𝗿𝗮𝗻𝘀𝗮𝗰𝘁𝗶𝗼𝗻𝘀 𝘆𝗲𝘁\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➕ 𝗔𝗗𝗗 𝗕𝗔𝗟𝗔𝗡𝗖𝗘", callback_data="add_balance"), InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home"))
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== ORDERS ======================
@bot.callback_query_handler(func=lambda c: c.data == "orders")
def orders_view(c):
    uid = str(c.message.chat.id)
    user_orders = orders.get(uid, [])
    
    if not user_orders:
        text = "📭 𝗡𝗢 𝗢𝗥𝗗𝗘𝗥𝗦 𝗬𝗘𝗧!\n\n𝗦𝘁𝗮𝗿𝘁 𝘀𝗵𝗼𝗽𝗽𝗶𝗻𝗴 𝗻𝗼𝘄!"
    else:
        text = "╔══════════════════════════════════════╗\n║              📦 𝗠𝗬 𝗢𝗥𝗗𝗘𝗥𝗦              ║\n╚══════════════════════════════════════╝\n\n"
        for o in user_orders[-10:]:
            text += f"🆔 𝗢𝗿𝗱𝗲𝗿: `{o.get('id', '𝗡/𝗔')}`\n"
            text += f"📦 𝗣𝗿𝗼𝗱𝘂𝗰𝘁: {o['product']}\n"
            text += f"💰 𝗔𝗺𝗼𝘂𝗻𝘁: {settings.get('currency')}{o['price']}\n"
            text += f"🔑 𝗞𝗲𝘆: `{o.get('key', '𝗡/𝗔')}`\n"
            text += f"📅 𝗗𝗮𝘁𝗲: {o['date'][:10]}\n"
            text += f"💳 𝗠𝗲𝘁𝗵𝗼𝗱: {o.get('method', '𝗡/𝗔')}\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== REFERRAL ======================
@bot.callback_query_handler(func=lambda c: c.data == "referral")
def referral(c):
    uname = bot.get_me().username
    u = users.get(str(c.message.chat.id), {})
    
    text = f"""╔══════════════════════════════════════╗
║              🔗 𝗥𝗘𝗙𝗘𝗥𝗥𝗔𝗟              ║
╚══════════════════════════════════════╝

💰 𝗘𝗮𝗿𝗻 {settings.get('referral_percent')}% 𝗰𝗼𝗺𝗺𝗶𝘀𝘀𝗶𝗼𝗻!

👥 𝗬𝗼𝘂𝗿 𝗥𝗲𝗳𝗲𝗿𝗿𝗮𝗹𝘀: {u.get('referrals', 0)}

🔗 𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸:
`https://t.me/{uname}?start=ref_{c.message.chat.id}`

📌 𝗛𝗼𝘄 𝗶𝘁 𝘄𝗼𝗿𝗸𝘀:
1️⃣ 𝗦𝗵𝗮𝗿𝗲 𝘆𝗼𝘂𝗿 𝗹𝗶𝗻𝗸
2️⃣ 𝗙𝗿𝗶𝗲𝗻𝗱𝘀 𝗷𝗼𝗶𝗻 𝘂𝘀𝗶𝗻𝗴 𝘆𝗼𝘂𝗿 𝗹𝗶𝗻𝗸
3️⃣ 𝗬𝗼𝘂 𝗴𝗲𝘁 {settings.get('referral_percent')}% 𝗼𝗳 𝘁𝗵𝗲𝗶𝗿 𝗽𝘂𝗿𝗰𝗵𝗮𝘀𝗲𝘀

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📤 𝗦𝗛𝗔𝗥𝗘 𝗟𝗜𝗡𝗞", url=f"https://t.me/share/url?url=https://t.me/{uname}?start=ref_{c.message.chat.id}&text=🔥 𝗝𝗼𝗶𝗻 𝗔𝗡𝗧𝗢 𝗦𝗛𝗢𝗣 𝗳𝗼𝗿 𝗽𝗿𝗲𝗺𝗶𝘂𝗺 𝘀𝗲𝗿𝘃𝗶𝗰𝗲𝘀! 💝"),
        InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home")
    )
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== ADD BALANCE ======================
@bot.callback_query_handler(func=lambda c: c.data == "add_balance")
def add_balance_menu(c):
    text = f"""╔══════════════════════════════════════╗
║              💰 𝗔𝗗𝗗 𝗕𝗔𝗟𝗔𝗡𝗖𝗘              ║
╚══════════════════════════════════════╝

📱 𝗕𝗞𝗮𝘀𝗵: `{settings.get('bkash')}`
📱 𝗡𝗮𝗴𝗮𝗱: `{settings.get('nagad')}`

📌 𝗜𝗻𝘀𝘁𝗿𝘂𝗰𝘁𝗶𝗼𝗻𝘀:
1️⃣ 𝗦𝗲𝗻𝗱 𝗺𝗼𝗻𝗲𝘆 𝘁𝗼 𝗮𝗻𝘆 𝗻𝘂𝗺𝗯𝗲𝗿
2️⃣ 𝗦𝗲𝗻𝗱 𝗧𝗥𝗫 𝗜𝗗 + 𝗔𝗺𝗼𝘂𝗻𝘁
3️⃣ 𝗦𝗲𝗻𝗱 𝘀𝗰𝗿𝗲𝗲𝗻𝘀𝗵𝗼𝘁

𝗠𝗶𝗻𝗶𝗺𝘂𝗺: {settings.get('currency')}100
𝗠𝗮𝘅𝗶𝗺𝘂𝗺: {settings.get('currency')}5000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(c.message.chat.id, "📝 𝗦𝗲𝗻𝗱 𝗮𝗺𝗼𝘂𝗻𝘁 𝗮𝗻𝗱 𝗧𝗥𝗫 𝗜𝗗:\n\n𝗘𝘅𝗮𝗺𝗽𝗹𝗲: `500 8Y7X9K2M4N`", parse_mode="Markdown")
    bot.register_next_step_handler(c.message, process_add_balance)

def process_add_balance(m):
    try:
        amt, trx = m.text.split()
        amt = int(amt)
        
        admin_text = f"""💰 𝗕𝗔𝗟𝗔𝗡𝗖𝗘 𝗥𝗘𝗤𝗨𝗘𝗦𝗧

👤 𝗨𝘀𝗲𝗿: `{m.chat.id}`
👤 𝗡𝗮𝗺𝗲: {m.from_user.first_name}
💰 𝗔𝗺𝗼𝘂𝗻𝘁: {settings.get('currency')}{amt}
🔢 𝗧𝗥𝗫 𝗜𝗗: `{trx}`"""
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘", callback_data=f"addbal_{m.chat.id}_{amt}"),
            InlineKeyboardButton("❌ 𝗥𝗘𝗝𝗘𝗖𝗧", callback_data=f"reject_{m.chat.id}")
        )
        
        bot.send_message(ADMIN_ID, admin_text, reply_markup=markup, parse_mode="Markdown")
        bot.reply_to(m, "✅ 𝗥𝗲𝗾𝘂𝗲𝘀𝘁 𝘀𝗲𝗻𝘁 𝘁𝗼 𝗮𝗱𝗺𝗶𝗻! 𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁.", parse_mode="Markdown")
    except:
        bot.reply_to(m, "❌ 𝗪𝗿𝗼𝗻𝗴 𝗳𝗼𝗿𝗺𝗮𝘁!\n\n𝗨𝘀𝗲: `500 8Y7X9K2M4N`", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("addbal_"))
def approve_balance(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "❌ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗱𝗺𝗶𝗻!")
        return
    
    _, _, uid, amt = c.data.split("_")
    add_balance(int(uid), int(amt), "𝗔𝗱𝗺𝗶𝗻 𝗔𝗱𝗱")
    bot.send_message(int(uid), f"✅ {settings.get('currency')}{amt} 𝗮𝗱𝗱𝗲𝗱 𝘁𝗼 𝘆𝗼𝘂𝗿 𝘄𝗮𝗹𝗹𝗲𝘁!", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"✅ 𝗔𝗱𝗱𝗲𝗱 {settings.get('currency')}{amt} 𝘁𝗼 𝘂𝘀𝗲𝗿 {uid}")
    bot.answer_callback_query(c.id, "✅ 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 𝗮𝗱𝗱𝗲𝗱!")

# ====================== HOME ======================
@bot.callback_query_handler(func=lambda c: c.data == "home")
def home(c):
    balance = get_balance(c.message.chat.id)
    bot_name = settings.get("bot_name")
    
    welcome = f"""╔══════════════════════════════════════╗
║          {bot_name}          ║
╚══════════════════════════════════════╝

💝 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗯𝗮𝗰𝗸 {c.from_user.first_name}!

💰 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: {settings.get('currency')}{balance}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 𝗢𝘄𝗻𝗲𝗿: 𝗣𝗔𝗣𝗔𝗝𝗜 𝗔𝗡𝗧𝗢
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    try:
        logo = settings.get("logo_url")
        bot.send_photo(c.message.chat.id, logo, caption=welcome, reply_markup=main_menu(), parse_mode="Markdown")
    except:
        bot.send_message(c.message.chat.id, welcome, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== ADMIN PANEL ======================
admin_session = {}

@bot.message_handler(commands=['admin'])
def admin_login(m):
    bot.send_message(m.chat.id, "🔐 𝗘𝗡𝗧𝗘𝗥 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗦𝗦𝗪𝗢𝗥𝗗:", parse_mode="Markdown")
    bot.register_next_step_handler(m, verify_admin)

def verify_admin(m):
    if m.text == ADMIN_PASSWORD:
        admin_session[str(m.chat.id)] = True
        show_admin_panel(m.chat.id)
    else:
        bot.send_message(m.chat.id, "❌ 𝗪𝗥𝗢𝗡𝗚 𝗣𝗔𝗦𝗦𝗪𝗢𝗥𝗗!", parse_mode="Markdown")

def show_admin_panel(chat_id):
    text = """╔══════════════════════════════════════╗
║              👑 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟              ║
╚══════════════════════════════════════╝

📊 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦:
`/stats` - 𝗩𝗶𝗲𝘄 𝗯𝗼𝘁 𝘀𝘁𝗮𝘁𝗶𝘀𝘁𝗶𝗰𝘀

📦 𝗣𝗥𝗢𝗗𝗨𝗖𝗧 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧:
`/addproduct 𝗡𝗔𝗠𝗘|𝗣𝗥𝗜𝗖𝗘|𝗗𝗘𝗦𝗖` - 𝗔𝗱𝗱 𝗽𝗿𝗼𝗱𝘂𝗰𝘁
`/addkey 𝗣𝗜𝗗|𝗞𝗘𝗬` - 𝗔𝗱𝗱 𝗽𝗿𝗼𝗱𝘂𝗰𝘁 𝗸𝗲𝘆
`/products` - 𝗟𝗶𝘀𝘁 𝗮𝗹𝗹 𝗽𝗿𝗼𝗱𝘂𝗰𝘁𝘀
`/delproduct 𝗣𝗜𝗗` - 𝗗𝗲𝗹𝗲𝘁𝗲 𝗽𝗿𝗼𝗱𝘂𝗰𝘁

💰 𝗪𝗔𝗟𝗟𝗘𝗧 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧:
`/addbalance 𝗨𝗜𝗗 𝗔𝗠𝗢𝗨𝗡𝗧` - 𝗔𝗱𝗱 𝗯𝗮𝗹𝗮𝗻𝗰𝗲
`/users` - 𝗟𝗶𝘀𝘁 𝗮𝗹𝗹 𝘂𝘀𝗲𝗿𝘀

🖼️ 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦:
`/setlogo 𝗨𝗥𝗟` - 𝗖𝗵𝗮𝗻𝗴𝗲 𝗯𝗼𝘁 𝗹𝗼𝗴𝗼
`/setname 𝗡𝗔𝗠𝗘` - 𝗖𝗵𝗮𝗻𝗴𝗲 𝗯𝗼𝘁 𝗻𝗮𝗺𝗲
`/setcurrency 𝗦𝗬𝗠𝗕𝗢𝗟` - 𝗖𝗵𝗮𝗻𝗴𝗲 𝗰𝘂𝗿𝗿𝗲𝗻𝗰𝘆
`/setbkash 𝗡𝗨𝗠𝗕𝗘𝗥` - 𝗖𝗵𝗮𝗻𝗴𝗲 𝗕𝗞𝗮𝘀𝗵 𝗻𝘂𝗺𝗯𝗲𝗿
`/setnagad 𝗡𝗨𝗠𝗕𝗘𝗥` - 𝗖𝗵𝗮𝗻𝗴𝗲 𝗡𝗮𝗴𝗮𝗱 𝗻𝘂𝗺𝗯𝗲𝗿

📢 𝗢𝗧𝗛𝗘𝗥:
`/broadcast 𝗠𝗦𝗚` - 𝗦𝗲𝗻𝗱 𝘁𝗼 𝗮𝗹𝗹 𝘂𝘀𝗲𝗿𝘀

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    bot.send_message(chat_id, text, parse_mode="Markdown")

# ====================== ADMIN COMMANDS ======================
@bot.message_handler(commands=['stats'])
def stats(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱! 𝗨𝘀𝗲 /𝗮𝗱𝗺𝗶𝗻 𝗳𝗶𝗿𝘀𝘁.", parse_mode="Markdown")
        return
    
    total_users = len(users)
    total_orders = sum(len(o) for o in orders.values())
    total_keys = sum(len(p.get('keys', [])) for p in products.values())
    total_balance = sum(w.get('balance', 0) for w in wallet.values())
    
    text = f"""📊 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦

👥 𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀: {total_users}
📦 𝗧𝗼𝘁𝗮𝗹 𝗢𝗿𝗱𝗲𝗿𝘀: {total_orders}
🔑 𝗧𝗼𝘁𝗮𝗹 𝗞𝗲𝘆𝘀: {total_keys}
💰 𝗧𝗼𝘁𝗮𝗹 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: {settings.get('currency')}{total_balance}
📦 𝗧𝗼𝘁𝗮𝗹 𝗣𝗿𝗼𝗱𝘂𝗰𝘁𝘀: {len(products)}"""
    
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['addproduct'])
def add_product(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱! 𝗨𝘀𝗲 /𝗮𝗱𝗺𝗶𝗻 𝗳𝗶𝗿𝘀𝘁.", parse_mode="Markdown")
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
        bot.reply_to(m, f"✅ 𝗣𝗿𝗼𝗱𝘂𝗰𝘁 𝗮𝗱𝗱𝗲𝗱! 𝗜𝗗: {new_id}\n{name} - {settings.get('currency')}{price}", parse_mode="Markdown")
    except:
        bot.reply_to(m, "❌ 𝗨𝘀𝗲: `/addproduct 𝗡𝗔𝗠𝗘|𝗣𝗥𝗜𝗖𝗘|𝗗𝗘𝗦𝗖`", parse_mode="Markdown")

@bot.message_handler(commands=['addkey'])
def add_key(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱! 𝗨𝘀𝗲 /𝗮𝗱𝗺𝗶𝗻 𝗳𝗶𝗿𝘀𝘁.", parse_mode="Markdown")
        return
    
    try:
        _, pid, key = m.text.split("|")
        if pid in products:
            products[pid]['keys'].append(key.upper())
            products[pid]['stock'] += 1
            save_db('products.json', products)
            bot.reply_to(m, f"✅ 𝗞𝗲𝘆 𝗮𝗱𝗱𝗲𝗱: `{key}`", parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ 𝗣𝗿𝗼𝗱𝘂𝗰𝘁 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱!", parse_mode="Markdown")
    except:
        bot.reply_to(m, "❌ 𝗨𝘀𝗲: `/addkey 𝗣𝗜𝗗|𝗞𝗘𝗬`", parse_mode="Markdown")

@bot.message_handler(commands=['products'])
def list_products(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱! 𝗨𝘀𝗲 /𝗮𝗱𝗺𝗶𝗻 𝗳𝗶𝗿𝘀𝘁.", parse_mode="Markdown")
        return
    
    text = "📦 𝗣𝗥𝗢𝗗𝗨𝗖𝗧𝗦:\n\n"
    for pid, p in products.items():
        text += f"🆔 {pid} | {p['name']}\n   💰 {settings.get('currency')}{p['price']} | 🔑 {len(p.get('keys', []))} | 📦 {p.get('stock', 0)}\n\n"
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['delproduct'])
def del_product(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱! 𝗨𝘀𝗲 /𝗮𝗱𝗺𝗶𝗻 𝗳𝗶𝗿𝘀𝘁.", parse_mode="Markdown")
        return
    
    try:
        pid = m.text.split()[1]
        if pid in products:
            del products[pid]
            save_db('products.json', products)
            bot.reply_to(m, f"✅ 𝗣𝗿𝗼𝗱𝘂𝗰𝘁 {pid} 𝗱𝗲𝗹𝗲𝘁𝗲𝗱!", parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ 𝗣𝗿𝗼𝗱𝘂𝗰𝘁 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱!", parse_mode="Markdown")
    except:
        bot.reply_to(m, "❌ 𝗨𝘀𝗲: `/delproduct 𝗣𝗜𝗗`", parse_mode="Markdown")

@bot.message_handler(commands=['users'])
def list_users(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱! 𝗨𝘀𝗲 /𝗮𝗱𝗺𝗶𝗻 𝗳𝗶𝗿𝘀𝘁.", parse_mode="Markdown")
        return
    
    text = "👥 𝗨𝗦𝗘𝗥𝗦:\n\n"
    for uid, u in list(users.items())[:30]:
        balance = get_balance(uid)
        text += f"🆔 {uid} | {u.get('name', '𝗨𝗻𝗸𝗻𝗼𝘄𝗻')}\n   💰 {settings.get('currency')}{balance}\n\n"
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['addbalance'])
def add_balance_admin(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱! 𝗨𝘀𝗲 /𝗮𝗱𝗺𝗶𝗻 𝗳𝗶𝗿𝘀𝘁.", parse_mode="Markdown")
        return
    
    try:
        _, uid, amt = m.text.split()
        add_balance(int(uid), int(amt), "𝗔𝗱𝗺𝗶𝗻 𝗔𝗱𝗱")
        bot.send_message(int(uid), f"✅ {settings.get('currency')}{amt} 𝗮𝗱𝗱𝗲𝗱 𝘁𝗼 𝘆𝗼𝘂𝗿 𝘄𝗮𝗹𝗹𝗲𝘁!", parse_mode="Markdown")
        bot.reply_to(m, f"✅ 𝗔𝗱𝗱𝗲𝗱 {settings.get('currency')}{amt} 𝘁𝗼 𝘂𝘀𝗲𝗿 {uid}", parse_mode="Markdown")
    except:
        bot.reply_to(m, "❌ 𝗨𝘀𝗲: `/addbalance 𝗨𝗜𝗗 𝗔𝗠𝗢𝗨𝗡𝗧`", parse_mode="Markdown")

@bot.message_handler(commands=['setlogo'])
def set_logo(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱! 𝗨𝘀𝗲 /𝗮𝗱𝗺𝗶𝗻 𝗳𝗶𝗿𝘀𝘁.", parse_mode="Markdown")
        return
    
    try:
        logo_url = m.text.split()[1]
        settings['logo_url'] = logo_url
        save_db('settings.json', settings)
        bot.reply_to(m, f"✅ 𝗟𝗼𝗴𝗼 𝘂𝗽𝗱𝗮𝘁𝗲𝗱!\n{logo_url}", parse_mode="Markdown")
    except:
        bot.reply_to(m, "❌ 𝗨𝘀𝗲: `/setlogo 𝗨𝗥𝗟`", parse_mode="Markdown")

@bot.message_handler(commands=['setname'])
def set_name(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱! 𝗨𝘀𝗲 /𝗮𝗱𝗺𝗶𝗻 𝗳𝗶𝗿𝘀𝘁.", parse_mode="Markdown")
        return
    
    name = m.text.replace("/setname ", "")
    settings['bot_name'] = name
    save_db('settings.json', settings)
    bot.reply_to(m, f"✅ 𝗕𝗼𝘁 𝗻𝗮𝗺𝗲 𝘂𝗽𝗱𝗮𝘁𝗲𝗱!\n{name}", parse_mode="Markdown")

@bot.message_handler(commands=['setcurrency'])
def set_currency(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱! 𝗨𝘀𝗲 /𝗮𝗱𝗺𝗶𝗻 𝗳𝗶𝗿𝘀𝘁.", parse_mode="Markdown")
        return
    
    currency = m.text.split()[1]
    settings['currency'] = currency
    save_db('settings.json', settings)
    bot.reply_to(m, f"✅ 𝗖𝘂𝗿𝗿𝗲𝗻𝗰𝘆 𝘂𝗽𝗱𝗮𝘁𝗲𝗱! {currency}", parse_mode="Markdown")

@bot.message_handler(commands=['setbkash'])
def set_bkash(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱! 𝗨𝘀𝗲 /𝗮𝗱𝗺𝗶𝗻 𝗳𝗶𝗿𝘀𝘁.", parse_mode="Markdown")
        return
    
    bkash = m.text.split()[1]
    settings['bkash'] = bkash
    save_db('settings.json', settings)
    bot.reply_to(m, f"✅ 𝗕𝗞𝗮𝘀𝗵 𝗻𝘂𝗺𝗯𝗲𝗿 𝘂𝗽𝗱𝗮𝘁𝗲𝗱! {bkash}", parse_mode="Markdown")

@bot.message_handler(commands=['setnagad'])
def set_nagad(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱! 𝗨𝘀𝗲 /𝗮𝗱𝗺𝗶𝗻 𝗳𝗶𝗿𝘀𝘁.", parse_mode="Markdown")
        return
    
    nagad = m.text.split()[1]
    settings['nagad'] = nagad
    save_db('settings.json', settings)
    bot.reply_to(m, f"✅ 𝗡𝗮𝗴𝗮𝗱 𝗻𝘂𝗺𝗯𝗲𝗿 𝘂𝗽𝗱𝗮𝘁𝗲𝗱! {nagad}", parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱! 𝗨𝘀𝗲 /𝗮𝗱𝗺𝗶𝗻 𝗳𝗶𝗿𝘀𝘁.", parse_mode="Markdown")
        return
    
    msg = m.text.replace("/broadcast ", "")
    count = 0
    for uid in users:
        try:
            bot.send_message(int(uid), f"📢 𝗔𝗡𝗡𝗢𝗨𝗡𝗖𝗘𝗠𝗘𝗡𝗧\n\n{msg}", parse_mode="Markdown")
            count += 1
            time.sleep(0.05)
        except:
            pass
    bot.reply_to(m, f"✅ 𝗦𝗲𝗻𝘁 𝘁𝗼 {count} 𝘂𝘀𝗲𝗿𝘀", parse_mode="Markdown")

# ====================== RUN ======================
if __name__ == "__main__":
    print("=" * 60)
    print("✨ ANTO SHOP ULTIMATE BOT STARTED!")
    print(f"🤖 Bot: @{bot.get_me().username}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("=" * 60)
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
