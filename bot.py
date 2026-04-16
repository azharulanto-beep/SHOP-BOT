import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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

# ====================== PRODUCTS ======================
if not products:
    products = {
        "1": {"name": "🔥 DRIP CLIENT PRO", "price": 399, "keys": ["DRIP-001", "DRIP-002", "DRIP-003"], "stock": 50, "desc": "✨ Premium Gaming Mod\n✅ Non Root Support\n✅ 30 Days Access\n✅ Auto Update\n✅ Anti-Ban"},
        "2": {"name": "🎮 BGMI ESP HACK", "price": 299, "keys": ["BGMI-001", "BGMI-002"], "stock": 30, "desc": "✨ ESP + Aimbot\n✅ 100% Safe\n✅ Undetected\n✅ Smooth Gameplay"},
        "3": {"name": "📱 NETFLIX PREMIUM", "price": 299, "keys": ["NF-001", "NF-002"], "stock": 20, "desc": "✨ 4K Ultra HD\n✅ 30 Days Access\n✅ Personal Account\n✅ All Devices"},
        "4": {"name": "🔧 HACKING TOOLS", "price": 499, "keys": ["HT-001", "HT-002"], "stock": 15, "desc": "✨ 100+ Tools\n✅ Lifetime Access\n✅ Regular Updates\n✅ Premium Features"}
    }
    save_db('products.json', products)

# ====================== MAIN MENU ======================
def main_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("🛍️ 𝗦𝗛𝗢𝗣 𝗡𝗢𝗪", callback_data="shop"),
        InlineKeyboardButton("👤 𝗠𝗬 𝗣𝗥𝗢𝗙𝗜𝗟𝗘", callback_data="profile")
    )
    m.add(
        InlineKeyboardButton("💰 𝗠𝗬 𝗪𝗔𝗟𝗟𝗘𝗧", callback_data="wallet"),
        InlineKeyboardButton("➕ 𝗔𝗗𝗗 𝗕𝗔𝗟𝗔𝗡𝗖𝗘", callback_data="add_balance")
    )
    m.add(
        InlineKeyboardButton("📦 𝗠𝗬 𝗢𝗥𝗗𝗘𝗥𝗦", callback_data="orders"),
        InlineKeyboardButton("🔑 𝗖𝗛𝗘𝗖𝗞 𝗞𝗘𝗬", callback_data="check_key")
    )
    m.add(
        InlineKeyboardButton("🔗 𝗥𝗘𝗙𝗘𝗥𝗥𝗔𝗟", callback_data="referral"),
        InlineKeyboardButton("📞 𝗦𝗨𝗣𝗣𝗢𝗥𝗧", url="https://t.me/PAPAJI_ANTO")
    )
    m.add(
        InlineKeyboardButton("📢 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url="https://t.me/ANTO_X_SHOP")
    )
    return m

@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.chat.id)
    if uid not in users:
        users[uid] = {"name": m.from_user.first_name, "joined": str(datetime.now()), "referrals": 0, "referred_by": None}
        save_db('users.json', users)
        add_balance(uid, 50, "🎁 Welcome Bonus")
    
    if len(m.text.split()) > 1:
        ref_code = m.text.split()[1]
        if ref_code.startswith("ref_"):
            referrer = ref_code.replace("ref_", "")
            if referrer != str(uid) and users.get(referrer):
                users[uid]["referred_by"] = referrer
                users[referrer]["referrals"] += 1
                add_balance(referrer, 50, "🔗 Referral Bonus")
                save_db('users.json', users)
                bot.send_message(int(referrer), f"🎉 **𝗡𝗲𝘄 𝗥𝗲𝗳𝗲𝗿𝗿𝗮𝗹!**\n\n{m.from_user.first_name} joined using your link!\n💰 ৳50 added to your wallet!")
    
    balance = get_balance(uid)
    
    welcome = f"""╔══════════════════════════════════════╗
║            ✨ 𝗔𝗡𝗧𝗢 𝗦𝗛𝗢𝗣 ✨            ║
╚══════════════════════════════════════╝

💝 **𝗛𝗲𝗹𝗹𝗼 {m.from_user.first_name}!**

╔══════════════════════════════════════╗
║  🏅 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗦𝗘𝗥𝗩𝗜𝗖𝗘                  ║
║  💰 𝗜𝗡𝗦𝗧𝗔𝗡𝗧 𝗗𝗘𝗟𝗜𝗩𝗘𝗥𝗬                ║
║  🔒 𝟭𝟬𝟬% 𝗦𝗘𝗖𝗨𝗥𝗘                     ║
║  🎁 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗕𝗢𝗡𝗨𝗦 ৳𝟱𝟬              ║
║  🤝 𝟮𝟰/𝟳 𝗦𝗨𝗣𝗣𝗢𝗥𝗧                    ║
╚══════════════════════════════════════╝

💰 **𝗬𝗼𝘂𝗿 𝗪𝗮𝗹𝗹𝗲𝘁 𝗕𝗮𝗹𝗮𝗻𝗰𝗲:** ৳{balance}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 **𝗢𝗪𝗡𝗘𝗥:** 𝗣𝗔𝗣𝗔𝗝𝗜 𝗔𝗡𝗧𝗢
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    bot.send_photo(m.chat.id, LOGO_URL, caption=welcome, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== SHOP ======================
@bot.callback_query_handler(func=lambda c: c.data == "shop")
def shop(c):
    m = InlineKeyboardMarkup(row_width=1)
    for pid, p in products.items():
        stock_icon = "🟢" if p['stock'] > 0 else "🔴"
        m.add(InlineKeyboardButton(f"{stock_icon} 𝗛𝗢𝗧  {p['name']}  ৳{p['price']}", callback_data=f"prod_{pid}"))
    m.add(InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞 𝗧𝗢 𝗛𝗢𝗠𝗘", callback_data="home"))
    
    bot.edit_message_caption(
        "╔══════════════════════════════════════╗\n"
        "║        🛍️ 𝗦𝗘𝗟𝗘𝗖𝗧 𝗣𝗥𝗢𝗗𝗨𝗖𝗧         ║\n"
        "╚══════════════════════════════════════╝\n\n"
        "📦 **𝗖𝗵𝗼𝗼𝘀𝗲 𝘆𝗼𝘂𝗿 𝗳𝗮𝘃𝗼𝗿𝗶𝘁𝗲 𝗽𝗿𝗼𝗱𝘂𝗰𝘁:**\n",
        c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("prod_"))
def prod_detail(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p:
        return
    
    text = f"""╔══════════════════════════════════════╗
║           📦 𝗣𝗥𝗢𝗗𝗨𝗖𝗧 𝗗𝗘𝗧𝗔𝗜𝗟𝗦          ║
╚══════════════════════════════════════╝

🔥 **{p['name']}**

{p['desc']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 💰 **𝗣𝗿𝗶𝗰𝗲:** ৳{p['price']}
┃ 📊 **𝗦𝘁𝗼𝗰𝗸:** {p['stock']} 𝗹𝗲𝗳𝘁
┃ 🚚 **𝗗𝗲𝗹𝗶𝘃𝗲𝗿𝘆:** 𝗜𝗻𝘀𝘁𝗮𝗻𝘁
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✅ **𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀:**
• 𝗜𝗻𝘀𝘁𝗮𝗻𝘁 𝗗𝗲𝗹𝗶𝘃𝗲𝗿𝘆
• 𝟮𝟰/𝟳 𝗦𝘂𝗽𝗽𝗼𝗿𝘁
• 𝗠𝗼𝗻𝗲𝘆 𝗕𝗮𝗰𝗸 𝗚𝘂𝗮𝗿𝗮𝗻𝘁𝗲𝗲

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("🛒 𝗕𝗨𝗬 𝗡𝗢𝗪", callback_data=f"buy_{pid}"),
        InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data="shop")
    )
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

# ====================== BUY ======================
pending = {}

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p or p['stock'] <= 0:
        bot.answer_callback_query(c.id, "❌ 𝗦𝗧𝗢𝗖𝗞 𝗘𝗡𝗗𝗘𝗗!")
        return
    
    pending[str(c.message.chat.id)] = {"pid": pid, "product": p, "price": p['price']}
    balance = get_balance(c.message.chat.id)
    
    text = f"""╔══════════════════════════════════════╗
║           💳 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗢𝗣𝗧𝗜𝗢𝗡           ║
╚══════════════════════════════════════╝

📦 **𝗣𝗿𝗼𝗱𝘂𝗰𝘁:** {p['name']}
💰 **𝗔𝗺𝗼𝘂𝗻𝘁:** ৳{p['price']}

💵 **𝗬𝗼𝘂𝗿 𝗪𝗮𝗹𝗹𝗲𝘁 𝗕𝗮𝗹𝗮𝗻𝗰𝗲:** ৳{balance}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗹𝗲𝗰𝘁 𝗽𝗮𝘆𝗺𝗲𝗻𝘁 𝗺𝗲𝘁𝗵𝗼𝗱:"""
    
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("💳 𝗪𝗔𝗟𝗟𝗘𝗧", callback_data="pay_wallet"),
        InlineKeyboardButton("📱 𝗕𝗞𝗔𝗦𝗛", callback_data="pay_bkash")
    )
    m.add(
        InlineKeyboardButton("🟢 𝗡𝗔𝗚𝗔𝗗", callback_data="pay_nagad"),
        InlineKeyboardButton("❌ 𝗖𝗔𝗡𝗖𝗘𝗟", callback_data="home")
    )
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

# ====================== WALLET PAYMENT ======================
@bot.callback_query_handler(func=lambda c: c.data == "pay_wallet")
def pay_wallet(c):
    uid = str(c.message.chat.id)
    pend = pending.get(uid)
    if not pend:
        bot.answer_callback_query(c.id, "❌ 𝗦𝗘𝗦𝗦𝗜𝗢𝗡 𝗘𝗫𝗣𝗜𝗥𝗘𝗗!")
        return
    
    if deduct_balance(uid, pend['price'], f"🛒 {pend['product']['name']}"):
        key = pend['product']['keys'].pop(0)
        pend['product']['stock'] -= 1
        save_db('products.json', products)
        
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if uid not in orders_db:
            orders_db[uid] = []
        orders_db[uid].append({"id": order_id, "product": pend['product']['name'], "price": pend['price'], "key": key, "date": str(datetime.now()), "method": "𝗪𝗔𝗟𝗟𝗘𝗧"})
        save_db('orders.json', orders_db)
        
        new_balance = get_balance(uid)
        
        text = f"""╔══════════════════════════════════════╗
║        ✅ 𝗣𝗨𝗥𝗖𝗛𝗔𝗦𝗘 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟        ║
╚══════════════════════════════════════╝

📦 **𝗣𝗿𝗼𝗱𝘂𝗰𝘁:** {pend['product']['name']}
💰 **𝗣𝗮𝗶𝗱:** ৳{pend['price']}
🔑 **𝗬𝗼𝘂𝗿 𝗞𝗲𝘆:** `{key}`

💝 **𝗡𝗲𝘄 𝗕𝗮𝗹𝗮𝗻𝗰𝗲:** ৳{new_balance}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
𝗧𝗵𝗮𝗻𝗸 𝘆𝗼𝘂 𝗳𝗼𝗿 𝘀𝗵𝗼𝗽𝗽𝗶𝗻𝗴 𝘄𝗶𝘁𝗵 𝘂𝘀! 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        m = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home"))
        bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")
        del pending[uid]
    else:
        bot.answer_callback_query(c.id, "❌ 𝗜𝗡𝗦𝗨𝗙𝗙𝗜𝗖𝗜𝗘𝗡𝗧 𝗕𝗔𝗟𝗔𝗡𝗖𝗘!")

# ====================== BKASH/NAGAD PAYMENT ======================
payment_pending = {}

@bot.callback_query_handler(func=lambda c: c.data in ["pay_bkash", "pay_nagad"])
def manual_pay(c):
    uid = str(c.message.chat.id)
    pend = pending.get(uid)
    if not pend:
        bot.answer_callback_query(c.id, "❌ 𝗦𝗘𝗦𝗦𝗜𝗢𝗡 𝗘𝗫𝗣𝗜𝗥𝗘𝗗!")
        return
    
    method = "𝗕𝗞𝗔𝗦𝗛" if c.data == "pay_bkash" else "𝗡𝗔𝗚𝗔𝗗"
    number = BKASH_NUMBER if c.data == "pay_bkash" else NAGAD_NUMBER
    ref = f"ANTO{random.randint(10000, 99999)}"
    payment_pending[uid] = {"pending": pend, "method": method, "ref": ref, "number": number}
    
    text = f"""╔══════════════════════════════════════╗
║           💳 {method} 𝗣𝗔𝗬𝗠𝗘𝗡𝗧           ║
╚══════════════════════════════════════╝

📦 **𝗣𝗿𝗼𝗱𝘂𝗰𝘁:** {pend['product']['name']}
💰 **𝗔𝗺𝗼𝘂𝗻𝘁:** ৳{pend['price']}

📱 **{method} 𝗡𝘂𝗺𝗯𝗲𝗿:** `{number}`
🔖 **𝗥𝗲𝗳𝗲𝗿𝗲𝗻𝗰𝗲:** `{ref}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📌 𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝗜𝗻𝘀𝘁𝗿𝘂𝗰𝘁𝗶𝗼𝗻𝘀:**

1️⃣ **𝗦𝗲𝗻𝗱 ৳{pend['price']}** 𝘁𝗼 {number}
2️⃣ **𝗦𝗲𝗻𝗱 𝗧𝗥𝗫 𝗜𝗗** 𝗵𝗲𝗿𝗲
3️⃣ **𝗦𝗲𝗻𝗱 𝗽𝗮𝘆𝗺𝗲𝗻𝘁 𝘀𝗰𝗿𝗲𝗲𝗻𝘀𝗵𝗼𝘁**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("✅ 𝗦𝗘𝗡𝗗 𝗧𝗥𝗫", callback_data="send_trx"))
    m.add(InlineKeyboardButton("❌ 𝗖𝗔𝗡𝗖𝗘𝗟", callback_data="home"))
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data == "send_trx")
def send_trx(c):
    bot.send_message(c.message.chat.id, "📝 **𝗦𝗲𝗻𝗱 𝘆𝗼𝘂𝗿 𝗧𝗥𝗫 𝗜𝗗:**")
    bot.register_next_step_handler(c.message, process_trx)

def process_trx(m):
    if m.text.startswith('/'):
        return
    uid = str(m.chat.id)
    if uid in payment_pending:
        payment_pending[uid]['trx'] = m.text
        bot.reply_to(m, "✅ **𝗧𝗥𝗫 𝗦𝗔𝗩𝗘𝗗!**\n\n📸 **𝗡𝗼𝘄 𝘀𝗲𝗻𝗱 𝗽𝗮𝘆𝗺𝗲𝗻𝘁 𝘀𝗰𝗿𝗲𝗲𝗻𝘀𝗵𝗼𝘁:**")
        bot.register_next_step_handler(m, process_ss)

def process_ss(m):
    if m.content_type != 'photo':
        bot.reply_to(m, "❌ 𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝗮 𝘀𝗰𝗿𝗲𝗲𝗻𝘀𝗵𝗼𝘁!")
        bot.register_next_step_handler(m, process_ss)
        return
    
    uid = str(m.chat.id)
    pp = payment_pending.get(uid)
    if not pp:
        return
    
    pend = pp['pending']
    
    admin_txt = f"""╔══════════════════════════════════════╗
║           🆕 𝗡𝗘𝗪 𝗢𝗥𝗗𝗘𝗥            ║
╚══════════════════════════════════════╝

👤 **𝗨𝘀𝗲𝗿 𝗜𝗗:** `{m.chat.id}`
👤 **𝗡𝗮𝗺𝗲:** {m.from_user.first_name}
📦 **𝗣𝗿𝗼𝗱𝘂𝗰𝘁:** {pend['product']['name']}
💰 **𝗔𝗺𝗼𝘂𝗻𝘁:** ৳{pend['price']}
💳 **𝗠𝗲𝘁𝗵𝗼𝗱:** {pp['method']}
🔢 **𝗧𝗥𝗫 𝗜𝗗:** `{pp['trx']}`
🔖 **𝗥𝗲𝗳:** `{pp['ref']}`
📱 **𝗡𝘂𝗺𝗯𝗲𝗿:** {pp['number']}
⏰ **𝗧𝗶𝗺𝗲:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘", callback_data=f"app_{uid}_{pend['pid']}"), InlineKeyboardButton("❌ 𝗥𝗘𝗝𝗘𝗖𝗧", callback_data=f"rej_{uid}"))
    
    bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=admin_txt, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(m.chat.id, "✅ **𝗢𝗿𝗱𝗲𝗿 𝘀𝗲𝗻𝘁 𝘁𝗼 𝗮𝗱𝗺𝗶𝗻!**\n⏳ 𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁 𝗳𝗼𝗿 𝗮𝗽𝗽𝗿𝗼𝘃𝗮𝗹.", parse_mode="Markdown")
    del payment_pending[uid]

# ====================== APPROVE/REJECT ======================
@bot.callback_query_handler(func=lambda c: c.data.startswith("app_"))
def approve(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "❌ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗱𝗺𝗶𝗻!")
        return
    
    _, uid, pid = c.data.split("_")
    p = products.get(pid)
    if not p or len(p['keys']) == 0:
        bot.send_message(ADMIN_ID, "❌ 𝗡𝗼 𝗸𝗲𝘆𝘀 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲!")
        bot.answer_callback_query(c.id, "𝗡𝗼 𝗸𝗲𝘆𝘀!")
        return
    
    key = p['keys'].pop(0)
    p['stock'] -= 1
    save_db('products.json', products)
    
    order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    if uid not in orders_db:
        orders_db[uid] = []
    orders_db[uid].append({"id": order_id, "product": p['name'], "price": p['price'], "key": key, "date": str(datetime.now()), "method": "𝗕𝗞𝗔𝗦𝗛/𝗡𝗔𝗚𝗔𝗗"})
    save_db('orders.json', orders_db)
    
    user_text = f"""╔══════════════════════════════════════╗
║        ✅ 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗        ║
╚══════════════════════════════════════╝

📦 **𝗣𝗿𝗼𝗱𝘂𝗰𝘁:** {p['name']}
💰 **𝗔𝗺𝗼𝘂𝗻𝘁:** ৳{p['price']}
🔑 **𝗬𝗼𝘂𝗿 𝗞𝗲𝘆:** `{key}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
𝗧𝗵𝗮𝗻𝗸 𝘆𝗼𝘂 𝗳𝗼𝗿 𝘀𝗵𝗼𝗽𝗽𝗶𝗻𝗴 𝘄𝗶𝘁𝗵 𝘂𝘀! 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    bot.send_message(int(uid), user_text, parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"✅ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗳𝗼𝗿 𝘂𝘀𝗲𝗿 {uid}")
    bot.answer_callback_query(c.id, "✅ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱!")

@bot.callback_query_handler(func=lambda c: c.data.startswith("rej_"))
def reject(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "❌ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗱𝗺𝗶𝗻!")
        return
    
    uid = c.data.split("_")[1]
    bot.send_message(int(uid), "❌ **𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗!**\n\n𝗣𝗹𝗲𝗮𝘀𝗲 𝗰𝗼𝗻𝘁𝗮𝗰𝘁 𝘀𝘂𝗽𝗽𝗼𝗿𝘁: @PAPAJI_ANTO", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"❌ 𝗥𝗲𝗷𝗲𝗰𝘁𝗲𝗱 𝘂𝘀𝗲𝗿 {uid}")
    bot.answer_callback_query(c.id, "✅ 𝗥𝗲𝗷𝗲𝗰𝘁𝗲𝗱!")

# ====================== PROFILE ======================
@bot.callback_query_handler(func=lambda c: c.data == "profile")
def profile(c):
    u = users.get(str(c.message.chat.id), {})
    balance = get_balance(c.message.chat.id)
    order_count = len(orders_db.get(str(c.message.chat.id), []))
    
    text = f"""╔══════════════════════════════════════╗
║            👤 𝗠𝗬 𝗣𝗥𝗢𝗙𝗜𝗟𝗘            ║
╚══════════════════════════════════════╝

🆔 **𝗨𝘀𝗲𝗿 𝗜𝗗:** `{c.message.chat.id}`
👤 **𝗡𝗮𝗺𝗲:** {u.get('name', '𝗨𝗻𝗸𝗻𝗼𝘄𝗻')}
📅 **𝗝𝗼𝗶𝗻𝗲𝗱:** {u.get('joined', '𝗨𝗻𝗸𝗻𝗼𝘄𝗻')[:10]}

💰 **𝗪𝗮𝗹𝗹𝗲𝘁 𝗕𝗮𝗹𝗮𝗻𝗰𝗲:** ৳{balance}
📦 **𝗧𝗼𝘁𝗮𝗹 𝗢𝗿𝗱𝗲𝗿𝘀:** {order_count}
👥 **𝗥𝗲𝗳𝗲𝗿𝗿𝗮𝗹𝘀:** {u.get('referrals', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

# ====================== WALLET ======================
@bot.callback_query_handler(func=lambda c: c.data == "wallet")
def wallet_view(c):
    balance = get_balance(c.message.chat.id)
    transactions = wallet.get(str(c.message.chat.id), {}).get('transactions', [])[-5:]
    
    text = f"""╔══════════════════════════════════════╗
║            💰 𝗠𝗬 𝗪𝗔𝗟𝗟𝗘𝗧            ║
╚══════════════════════════════════════╝

💵 **𝗖𝘂𝗿𝗿𝗲𝗻𝘁 𝗕𝗮𝗹𝗮𝗻𝗰𝗲:** ৳{balance}

📜 **𝗥𝗲𝗰𝗲𝗻𝘁 𝗧𝗿𝗮𝗻𝘀𝗮𝗰𝘁𝗶𝗼𝗻𝘀:**
"""
    if transactions:
        for t in reversed(transactions):
            text += f"• {t['type']} ৳{t['amount']} - {t['date'][:16]}\n"
    else:
        text += "• 𝗡𝗼 𝘁𝗿𝗮𝗻𝘀𝗮𝗰𝘁𝗶𝗼𝗻𝘀 𝘆𝗲𝘁\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("➕ 𝗔𝗗𝗗 𝗕𝗔𝗟𝗔𝗡𝗖𝗘", callback_data="add_balance"), InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home"))
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

# ====================== ADD BALANCE ======================
@bot.callback_query_handler(func=lambda c: c.data == "add_balance")
def add_balance_menu(c):
    text = f"""╔══════════════════════════════════════╗
║            💰 𝗔𝗗𝗗 𝗕𝗔𝗟𝗔𝗡𝗖𝗘            ║
╚══════════════════════════════════════╝

📱 **𝗕𝗞𝗮𝘀𝗵 𝗡𝘂𝗺𝗯𝗲𝗿:** `{BKASH_NUMBER}`
📱 **𝗡𝗮𝗴𝗮𝗱 𝗡𝘂𝗺𝗯𝗲𝗿:** `{NAGAD_NUMBER}`

**📌 𝗜𝗻𝘀𝘁𝗿𝘂𝗰𝘁𝗶𝗼𝗻𝘀:**
1️⃣ 𝗦𝗲𝗻𝗱 𝗺𝗼𝗻𝗲𝘆 𝘁𝗼 𝗮𝗻𝘆 𝗻𝘂𝗺𝗯𝗲𝗿
2️⃣ 𝗦𝗲𝗻𝗱 𝗧𝗥𝗫 𝗜𝗗 𝗮𝗻𝗱 𝗮𝗺𝗼𝘂𝗻𝘁
3️⃣ 𝗦𝗲𝗻𝗱 𝘀𝗰𝗿𝗲𝗲𝗻𝘀𝗵𝗼𝘁

**𝗠𝗶𝗻𝗶𝗺𝘂𝗺 𝗔𝗱𝗱:** ৳𝟭𝟬𝟬
**𝗠𝗮𝘅𝗶𝗺𝘂𝗺 𝗔𝗱𝗱:** ৳𝟱𝟬𝟬𝟬

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")
    bot.send_message(c.message.chat.id, "📝 **𝗦𝗲𝗻𝗱 𝗮𝗺𝗼𝘂𝗻𝘁 𝗮𝗻𝗱 𝗧𝗥𝗫 𝗜𝗗:**\n\n𝗘𝘅𝗮𝗺𝗽𝗹𝗲: `500 8Y7X9K2M4N`", parse_mode="Markdown")
    bot.register_next_step_handler(c.message, process_add_balance)

def process_add_balance(m):
    if m.text.startswith('/'):
        return
    try:
        amt, trx = m.text.split()
        amt = int(amt)
        
        admin_txt = f"""╔══════════════════════════════════════╗
║        💰 𝗕𝗔𝗟𝗔𝗡𝗖𝗘 𝗥𝗘𝗤𝗨𝗘𝗦𝗧        ║
╚══════════════════════════════════════╝

👤 **𝗨𝘀𝗲𝗿:** `{m.chat.id}`
👤 **𝗡𝗮𝗺𝗲:** {m.from_user.first_name}
💰 **𝗔𝗺𝗼𝘂𝗻𝘁:** ৳{amt}
🔢 **𝗧𝗥𝗫 𝗜𝗗:** `{trx}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘", callback_data=f"addbal_{m.chat.id}_{amt}"), InlineKeyboardButton("❌ 𝗥𝗘𝗝𝗘𝗖𝗧", callback_data=f"rej_{m.chat.id}"))
        
        bot.send_message(ADMIN_ID, admin_txt, reply_markup=markup, parse_mode="Markdown")
        bot.reply_to(m, "✅ **𝗥𝗲𝗾𝘂𝗲𝘀𝘁 𝘀𝗲𝗻𝘁 𝘁𝗼 𝗮𝗱𝗺𝗶𝗻!**\n⏳ 𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁.", parse_mode="Markdown")
    except:
        bot.reply_to(m, "❌ **𝗪𝗿𝗼𝗻𝗴 𝗳𝗼𝗿𝗺𝗮𝘁!**\n\n𝗨𝘀𝗲: `500 8Y7X9K2M4N`", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("addbal_"))
def approve_balance(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "❌ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗱𝗺𝗶𝗻!")
        return
    
    _, uid, amt = c.data.split("_")
    add_balance(int(uid), int(amt), "➕ 𝗔𝗱𝗺𝗶𝗻 𝗔𝗱𝗱")
    bot.send_message(int(uid), f"✅ **৳{amt} 𝗮𝗱𝗱𝗲𝗱 𝘁𝗼 𝘆𝗼𝘂𝗿 𝘄𝗮𝗹𝗹𝗲𝘁!**", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"✅ 𝗔𝗱𝗱𝗲𝗱 ৳{amt} 𝘁𝗼 𝘂𝘀𝗲𝗿 {uid}")
    bot.answer_callback_query(c.id, "✅ 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 𝗮𝗱𝗱𝗲𝗱!")

# ====================== ORDERS ======================
@bot.callback_query_handler(func=lambda c: c.data == "orders")
def orders(c):
    uid = str(c.message.chat.id)
    user_orders = orders_db.get(uid, [])
    
    if not user_orders:
        text = "📭 **𝗡𝗼 𝗼𝗿𝗱𝗲𝗿𝘀 𝘆𝗲𝘁!**\n\n𝗦𝘁𝗮𝗿𝘁 𝘀𝗵𝗼𝗽𝗽𝗶𝗻𝗴 𝗻𝗼𝘄!"
    else:
        text = "╔══════════════════════════════════════╗\n║           📦 𝗠𝗬 𝗢𝗥𝗗𝗘𝗥𝗦            ║\n╚══════════════════════════════════════╝\n\n"
        for o in user_orders[-10:]:
            text += f"🆔 **𝗜𝗗:** `{o.get('id', '𝗡/𝗔')}`\n"
            text += f"📦 **𝗣𝗿𝗼𝗱𝘂𝗰𝘁:** {o['product']}\n"
            text += f"💰 **𝗔𝗺𝗼𝘂𝗻𝘁:** ৳{o['price']}\n"
            text += f"🔑 **𝗞𝗲𝘆:** `{o.get('key', '𝗡/𝗔')}`\n"
            text += f"📅 **𝗗𝗮𝘁𝗲:** {o['date'][:10]}\n"
            text += f"💳 **𝗠𝗲𝘁𝗵𝗼𝗱:** {o.get('method', '𝗡/𝗔')}\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

# ====================== CHECK KEY ======================
@bot.callback_query_handler(func=lambda c: c.data == "check_key")
def check_key_menu(c):
    bot.send_message(c.message.chat.id, "🔑 **𝗘𝗻𝘁𝗲𝗿 𝘆𝗼𝘂𝗿 𝗸𝗲𝘆:**", parse_mode="Markdown")
    bot.register_next_step_handler(c.message, check_key_proc)

def check_key_proc(m):
    key = m.text.strip().upper()
    found = False
    
    for pid, p in products.items():
        if key in p['keys']:
            found = True
            text = f"✅ **𝗩𝗔𝗟𝗜𝗗 𝗞𝗘𝗬!**\n\n📦 **𝗣𝗿𝗼𝗱𝘂𝗰𝘁:** {p['name']}\n💝 **𝗬𝗼𝘂 𝗰𝗮𝗻 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗸𝗲𝘆.**"
            bot.reply_to(m, text, parse_mode="Markdown")
            break
    
    if not found:
        bot.reply_to(m, "❌ **𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗞𝗘𝗬!**\n\n𝗞𝗲𝘆 𝗶𝘀 𝘄𝗿𝗼𝗻𝗴 𝗼𝗿 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝘂𝘀𝗲𝗱.", parse_mode="Markdown")

# ====================== REFERRAL ======================
@bot.callback_query_handler(func=lambda c: c.data == "referral")
def referral(c):
    uname = bot.get_me().username
    u = users.get(str(c.message.chat.id), {})
    
    text = f"""╔══════════════════════════════════════╗
║           🔗 𝗥𝗘𝗙𝗘𝗥𝗥𝗔𝗟            ║
╚══════════════════════════════════════╝

💰 **𝗘𝗮𝗿𝗻 𝟭𝟬% 𝗰𝗼𝗺𝗺𝗶𝘀𝘀𝗶𝗼𝗻** 𝗼𝗻 𝗲𝘃𝗲𝗿𝘆 𝗽𝘂𝗿𝗰𝗵𝗮𝘀𝗲!

👥 **𝗬𝗼𝘂𝗿 𝗥𝗲𝗳𝗲𝗿𝗿𝗮𝗹𝘀:** {u.get('referrals', 0)}

🔗 **𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸:**
`https://t.me/{uname}?start=ref_{c.message.chat.id}`

**📌 𝗛𝗼𝘄 𝗶𝘁 𝘄𝗼𝗿𝗸𝘀:**
1️⃣ 𝗦𝗵𝗮𝗿𝗲 𝘆𝗼𝘂𝗿 𝗹𝗶𝗻𝗸
2️⃣ 𝗙𝗿𝗶𝗲𝗻𝗱𝘀 𝗷𝗼𝗶𝗻 𝘂𝘀𝗶𝗻𝗴 𝘆𝗼𝘂𝗿 𝗹𝗶𝗻𝗸
3️⃣ 𝗬𝗼𝘂 𝗴𝗲𝘁 𝟭𝟬% 𝗼𝗳 𝘁𝗵𝗲𝗶𝗿 𝗽𝘂𝗿𝗰𝗵𝗮𝘀𝗲𝘀

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    m = InlineKeyboardMarkup()
    m.add(
        InlineKeyboardButton("📤 𝗦𝗛𝗔𝗥𝗘 𝗟𝗜𝗡𝗞", url=f"https://t.me/share/url?url=https://t.me/{uname}?start=ref_{c.message.chat.id}&text=🔥 𝗝𝗼𝗶𝗻 𝗔𝗡𝗧𝗢 𝗦𝗛𝗢𝗣 𝗳𝗼𝗿 𝗽𝗿𝗲𝗺𝗶𝘂𝗺 𝘀𝗲𝗿𝘃𝗶𝗰𝗲𝘀! 💝"),
        InlineKeyboardButton("🏠 𝗛𝗢𝗠𝗘", callback_data="home")
    )
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

# ====================== HOME ======================
@bot.callback_query_handler(func=lambda c: c.data == "home")
def home(c):
    balance = get_balance(c.message.chat.id)
    
    welcome = f"""╔══════════════════════════════════════╗
║            ✨ 𝗔𝗡𝗧𝗢 𝗦𝗛𝗢𝗣 ✨            ║
╚══════════════════════════════════════╝

💝 **𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗯𝗮𝗰𝗸 {c.from_user.first_name}!**

💰 **𝗬𝗼𝘂𝗿 𝗪𝗮𝗹𝗹𝗲𝘁 𝗕𝗮𝗹𝗮𝗻𝗰𝗲:** ৳{balance}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 **𝗢𝗪𝗡𝗘𝗥:** 𝗣𝗔𝗣𝗔𝗝𝗜 𝗔𝗡𝗧𝗢
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    bot.edit_message_caption(welcome, c.message.chat.id, c.message.message_id, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== ADMIN COMMANDS ======================
@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.chat.id != ADMIN_ID:
        return
    
    text = """╔══════════════════════════════════════╗
║         👑 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟          ║
╚══════════════════════════════════════╝

📦 **𝗣𝗥𝗢𝗗𝗨𝗖𝗧 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧:**
`/addkey 𝗣𝗜𝗗|𝗞𝗘𝗬` - 𝗔𝗱𝗱 𝗸𝗲𝘆
`/products` - 𝗟𝗶𝘀𝘁 𝗽𝗿𝗼𝗱𝘂𝗰𝘁𝘀

💰 **𝗪𝗔𝗟𝗟𝗘𝗧 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧:**
`/addbalance 𝗨𝗜𝗗 𝗔𝗠𝗢𝗨𝗡𝗧` - 𝗔𝗱𝗱 𝗯𝗮𝗹𝗮𝗻𝗰𝗲

👥 **𝗨𝗦𝗘𝗥 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧:**
`/users` - 𝗟𝗶𝘀𝘁 𝘂𝘀𝗲𝗿𝘀
`/stats` - 𝗦𝘁𝗮𝘁𝗶𝘀𝘁𝗶𝗰𝘀
`/broadcast 𝗠𝗘𝗦𝗦𝗔𝗚𝗘` - 𝗦𝗲𝗻𝗱 𝘁𝗼 𝗮𝗹𝗹

⚙️ **𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦:**
`/setbkash 𝗡𝗨𝗠𝗕𝗘𝗥` - 𝗦𝗲𝘁 𝗯𝗞𝗮𝘀𝗵
`/setnagad 𝗡𝗨𝗠𝗕𝗘𝗥` - 𝗦𝗲𝘁 𝗡𝗮𝗴𝗮𝗱

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

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
            bot.reply_to(m, f"✅ **𝗞𝗲𝘆 𝗮𝗱𝗱𝗲𝗱:** `{key}`", parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ **𝗣𝗿𝗼𝗱𝘂𝗰𝘁 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱!**")
    except:
        bot.reply_to(m, "❌ **𝗨𝘀𝗲:** `/addkey 𝗣𝗜𝗗|𝗞𝗘𝗬`")

@bot.message_handler(commands=['products'])
def list_prod(m):
    if m.chat.id != ADMIN_ID:
        return
    text = "📦 **𝗣𝗥𝗢𝗗𝗨𝗖𝗧𝗦:**\n\n"
    for pid, p in products.items():
        text += f"🆔 **{pid}** | {p['name']}\n   💰 ৳{p['price']} | 🔑 {len(p['keys'])} | 📦 {p['stock']}\n\n"
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['addbalance'])
def addbal_admin(m):
    if m.chat.id != ADMIN_ID:
        return
    try:
        _, uid, amt = m.text.split()
        add_balance(int(uid), int(amt), "👑 𝗔𝗱𝗺𝗶𝗻 𝗔𝗱𝗱")
        bot.send_message(int(uid), f"✅ **৳{amt} 𝗮𝗱𝗱𝗲𝗱 𝘁𝗼 𝘆𝗼𝘂𝗿 𝘄𝗮𝗹𝗹𝗲𝘁!**", parse_mode="Markdown")
        bot.reply_to(m, f"✅ **𝗔𝗱𝗱𝗲𝗱 ৳{amt} 𝘁𝗼 {uid}**")
    except:
        bot.reply_to(m, "❌ **𝗨𝘀𝗲:** `/addbalance 𝗨𝗜𝗗 𝗔𝗠𝗢𝗨𝗡𝗧`")

@bot.message_handler(commands=['users'])
def list_users(m):
    if m.chat.id != ADMIN_ID:
        return
    text = "👥 **𝗨𝗦𝗘𝗥𝗦:**\n\n"
    for uid, u in list(users.items())[:30]:
        balance = get_balance(uid)
        text += f"🆔 `{uid}` | {u.get('name', '𝗨𝗻𝗸𝗻𝗼𝘄𝗻')}\n   💰 ৳{balance} | 📦 {len(orders_db.get(uid, []))}\n\n"
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats(m):
    if m.chat.id != ADMIN_ID:
        return
    total_balance = sum(w['balance'] for w in wallet.values())
    total_keys = sum(len(p['keys']) for p in products.values())
    text = f"📊 **𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦**\n\n👥 **𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀:** {len(users)}\n🔑 **𝗧𝗼𝘁𝗮𝗹 𝗞𝗲𝘆𝘀:** {total_keys}\n💰 **𝗧𝗼𝘁𝗮𝗹 𝗕𝗮𝗹𝗮𝗻𝗰𝗲:** ৳{total_balance}\n📦 **𝗧𝗼𝘁𝗮𝗹 𝗣𝗿𝗼𝗱𝘂𝗰𝘁𝘀:** {len(products)}"
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast(m):
    if m.chat.id != ADMIN_ID:
        return
    msg = m.text.replace("/broadcast ", "")
    count = 0
    for uid in users:
        try:
            bot.send_message(int(uid), f"📢 **𝗔𝗡𝗡𝗢𝗨𝗡𝗖𝗘𝗠𝗘𝗡𝗧**\n\n{msg}", parse_mode="Markdown")
            count += 1
            time.sleep(0.05)
        except:
            pass
    bot.reply_to(m, f"✅ **𝗦𝗲𝗻𝘁 𝘁𝗼 {count} 𝘂𝘀𝗲𝗿𝘀**")

@bot.message_handler(commands=['setbkash'])
def set_bkash(m):
    if m.chat.id != ADMIN_ID:
        return
    global BKASH_NUMBER
    BKASH_NUMBER = m.text.split()[1]
    bot.reply_to(m, f"✅ **𝗯𝗞𝗮𝘀𝗵 𝘀𝗲𝘁 𝘁𝗼:** `{BKASH_NUMBER}`", parse_mode="Markdown")

@bot.message_handler(commands=['setnagad'])
def set_nagad(m):
    if m.chat.id != ADMIN_ID:
        return
    global NAGAD_NUMBER
    NAGAD_NUMBER = m.text.split()[1]
    bot.reply_to(m, f"✅ **𝗡𝗮𝗴𝗮𝗱 𝘀𝗲𝘁 𝘁𝗼:** `{NAGAD_NUMBER}`", parse_mode="Markdown")

# ====================== RUN ======================
if __name__ == "__main__":
    print("=" * 60)
    print("🔥 𝗔𝗡𝗧𝗢 𝗦𝗛𝗢𝗣 𝗨𝗟𝗧𝗜𝗠𝗔𝗧𝗘 𝗣𝗥𝗢 𝗘𝗗𝗜𝗧𝗜𝗢𝗡")
    print(f"🤖 𝗕𝗼𝘁: @{bot.get_me().username}")
    print(f"👑 𝗔𝗱𝗺𝗶𝗻: {ADMIN_ID}")
    print("=" * 60)
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"⚠️ 𝗘𝗿𝗿𝗼𝗿: {e}")
            time.sleep(5)
