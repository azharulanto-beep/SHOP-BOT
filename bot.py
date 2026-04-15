import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import os
import json
import random
import string
import time
from datetime import datetime, timedelta

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
ADMIN_PASSWORD = "ANTO2026@X"  # তোর পাসওয়ার্ড

bot = telebot.TeleBot(TOKEN)

# ================= ব্র্যান্ডিং =================
BOT_NAME = "✨ ANTO X SHOP ✨"
OWNER_NAME = "PAPAJI ANTO"
BOT_USERNAME = "@PAPAJI_ANTO"
CHANNEL_LINK = "https://t.me/ANTO_X_SHOP"
DEVELOPER_LINK = "https://t.me/PAPAJI_ANTO"
LOGO_URL = "https://i.postimg.cc/Cxk8NxV2/istockphoto-827351040-1024x1024.jpg"
BKASH_NUMBER = "01918591988"

# ================= ডাটাবেজ =================
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
orders_db = load_db('orders.json')
settings_db = load_db('settings.json')

# ================= সেটিংস =================
if not settings_db:
    settings_db = {
        "channel_url": CHANNEL_LINK,
        "developer_url": DEVELOPER_LINK,
        "support_url": "https://t.me/PAPAJI_ANTO",
        "bkash": BKASH_NUMBER,
        "bot_name": BOT_NAME
    }
    save_db('settings.json', settings_db)

# ================= প্রোডাক্ট ডাটাবেজ =================
if not products_db:
    products_db = {
        "1": {
            "name": "🎮 Drip Client - Non Root",
            "price": 399,
            "desc": "✨ Non Root Version\n✅ All Features Unlocked\n✅ 30 Days Access\n✅ Auto Update",
            "apk_link": "https://t.me/ANTO_X_SHOP",
            "keys": ["DRIP-NR-001", "DRIP-NR-002"],
            "stock": 10,
            "sold": 0,
            "category": "mods"
        },
        "2": {
            "name": "🎮 Drip Client - Root",
            "price": 449,
            "desc": "✨ Root Version\n✅ ESP + AIMBOT\n✅ 30 Days Access\n✅ Best Performance",
            "apk_link": "https://t.me/ANTO_X_SHOP",
            "keys": ["DRIP-RT-001", "DRIP-RT-002"],
            "stock": 8,
            "sold": 0,
            "category": "mods"
        },
        "3": {
            "name": "🔧 Hg ApkMod - Non Root + Root",
            "price": 499,
            "desc": "✨ Both Version Support\n✅ All in One\n✅ Lifetime Access\n✅ Premium Features",
            "apk_link": "https://t.me/ANTO_X_SHOP",
            "keys": ["HG-001", "HG-002"],
            "stock": 15,
            "sold": 0,
            "category": "mods"
        },
        "4": {
            "name": "⚔️ Pato Team - Non Root (Safe)",
            "price": 349,
            "desc": "✨ Safe Version\n✅ No Ban Risk\n✅ 30 Days Access\n✅ Undetected",
            "apk_link": "https://t.me/ANTO_X_SHOP",
            "keys": ["PATO-S-001", "PATO-S-002"],
            "stock": 12,
            "sold": 0,
            "category": "mods"
        },
        "5": {
            "name": "💀 Pato Team - Non Root (Brutal)",
            "price": 399,
            "desc": "✨ Brutal Version\n✅ Max Features\n✅ 30 Days Access\n✅ Best for Gaming",
            "apk_link": "https://t.me/ANTO_X_SHOP",
            "keys": ["PATO-B-001", "PATO-B-002"],
            "stock": 10,
            "sold": 0,
            "category": "mods"
        },
        "6": {
            "name": "🎯 Prime Hook - Non Root",
            "price": 449,
            "desc": "✨ Prime Hook Features\n✅ Non Root\n✅ 30 Days Access\n✅ Smooth Gameplay",
            "apk_link": "https://t.me/ANTO_X_SHOP",
            "keys": ["PRIME-001", "PRIME-002"],
            "stock": 8,
            "sold": 0,
            "category": "mods"
        },
        "7": {
            "name": "🔥 Reaper X Pro - Root",
            "price": 499,
            "desc": "✨ Reaper X Root Version\n✅ Best Features\n✅ 30 Days Access\n✅ Pro Performance",
            "apk_link": "https://t.me/ANTO_X_SHOP",
            "keys": ["REAPER-R-001", "REAPER-R-002"],
            "stock": 10,
            "sold": 0,
            "category": "mods"
        },
        "8": {
            "name": "🔥 Reaper X Pro - Non Root",
            "price": 549,
            "desc": "✨ Reaper X Non Root\n✅ Premium Unlocked\n✅ 30 Days Access\n✅ VIP Features",
            "apk_link": "https://t.me/ANTO_X_SHOP",
            "keys": ["REAPER-N-001", "REAPER-N-002"],
            "stock": 7,
            "sold": 0,
            "category": "mods"
        },
        "9": {
            "name": "💎 Haxx Cker Pro - Root",
            "price": 599,
            "desc": "✨ Haxx Cker Pro\n✅ Advanced Features\n✅ Lifetime Access\n✅ Pro Tools",
            "apk_link": "https://t.me/ANTO_X_SHOP",
            "keys": ["HAXX-001", "HAXX-002"],
            "stock": 5,
            "sold": 0,
            "category": "mods"
        }
    }
    save_db('products.json', products_db)

# ================= মেইন মেনু বাটন =================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🛍️ SHOP NOW", callback_data="shop_now"),
        InlineKeyboardButton("📢 OUR CHANNELS", url=settings_db.get("channel_url", CHANNEL_LINK)),
        InlineKeyboardButton("👨‍💻 BOT DEVELOPER", url=settings_db.get("developer_url", DEVELOPER_LINK))
    )
    markup.add(
        InlineKeyboardButton("👤 MY PROFILE", callback_data="my_profile"),
        InlineKeyboardButton("💰 ADD BALANCE", callback_data="add_balance"),
        InlineKeyboardButton("📜 ALL HISTORY", callback_data="my_orders")
    )
    markup.add(
        InlineKeyboardButton("🔗 REFERRAL", callback_data="referral"),
        InlineKeyboardButton("📖 HOW TO USE", callback_data="how_to_use"),
        InlineKeyboardButton("🎲 LUCKY GAME", callback_data="lucky_game")
    )
    return markup

# ================= স্টার্ট মেসেজ =================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    if user_id not in users_db:
        users_db[user_id] = {
            "name": message.from_user.first_name,
            "username": message.from_user.username,
            "balance": 0,
            "orders": [],
            "joined": str(datetime.now()),
            "referrals": 0,
            "referred_by": None
        }
        save_db('users.json', users_db)
    
    # চেক রেফারেল
    if len(message.text.split()) > 1:
        ref_code = message.text.split()[1]
        if ref_code.startswith("ref_"):
            referrer = ref_code.replace("ref_", "")
            if referrer != str(user_id) and users_db.get(referrer):
                users_db[str(user_id)]["referred_by"] = referrer
                users_db[referrer]["referrals"] += 1
                save_db('users.json', users_db)
                bot.send_message(int(referrer), f"🎉 **নতুন রেফারেল!**\n\n{message.from_user.first_name} আপনার লিংক ব্যবহার করে জয়েন করেছেন!")
    
    welcome_text = f"""╔══════════════════════════════╗
║      ✨ **ANTO X SHOP** ✨      ║
╚══════════════════════════════╝

💝 **হ্যালো {message.from_user.first_name}!**

🎉 **প্রিমিয়াম শপে স্বাগতম**

╔══════════════════════════════╗
║ 🏅 **প্রিমিয়াম সার্ভিস**         ║
║ 💰 **ইন্সট্যান্ট ডেলিভারি**      ║
║ 🔒 **১০০% সিকিওর**              ║
║ 🔑 **লাইসেন্স কী জেনারেটর**      ║
║ 👥 **রেফারেল বোনাস**            ║
║ 📞 **২৪/৭ সাপোর্ট**             ║
╚══════════════════════════════╝

⚠️ **প্লিজ সিলেক্ট ইওর প্রোডাক্ট** ⚠️

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 **ওনার:** {OWNER_NAME}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    bot.send_photo(message.chat.id, LOGO_URL, caption=welcome_text, reply_markup=main_menu(), parse_mode="Markdown")

# ================= শপ নাও =================
@bot.callback_query_handler(func=lambda call: call.data == "shop_now")
def shop_now(call):
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, product in products_db.items():
        stock_icon = "🟢" if product['stock'] > 0 else "🔴"
        markup.add(InlineKeyboardButton(f"{stock_icon} {product['name']} - ৳{product['price']}", callback_data=f"product_{pid}"))
    markup.add(InlineKeyboardButton("🔙 ব্যাক টু মেনু", callback_data="back_main"))
    
    bot.edit_message_caption("🛍️ **প্লিজ সিলেক্ট ইওর প্রোডাক্ট** 🛍️\n\nনিচ থেকে আপনার পছন্দের প্রোডাক্ট বাছাই করুন:",
                            call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ================= প্রোডাক্ট ডিটেইলস =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def product_detail(call):
    pid = call.data.replace("product_", "")
    product = products_db.get(pid)
    
    if not product:
        bot.answer_callback_query(call.id, "প্রোডাক্ট খুঁজে পাওয়া যায়নি!")
        return
    
    text = f"""╔══════════════════════════════╗
║      📦 **{product['name']}**      ║
╚══════════════════════════════╝

{product['desc']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 💰 **মূল্য:** ৳{product['price']}
┃ 📊 **স্টক:** {product['stock']} টি
┃ 📈 **বিক্রি:** {product['sold']}
┃ 🚚 **ডেলিভারি:** ইন্সট্যান্ট
┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✅ **ফিচারসমূহ:**
• ইন্সট্যান্ট ডেলিভারি
• ২৪/৭ সাপোর্ট
• মানি-ব্যাক গ্যারান্টি

━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛒 এখন কিনুন", callback_data=f"buy_{pid}"),
        InlineKeyboardButton("📥 APK লিংক", url=product['apk_link'])
    )
    markup.add(InlineKeyboardButton("🔙 ব্যাক", callback_data="shop_now"))
    markup.add(InlineKeyboardButton("🏠 মেইন মেনু", callback_data="back_main"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ================= কেনাকাটা =================
pending_payments = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_product(call):
    pid = call.data.replace("buy_", "")
    product = products_db.get(pid)
    
    if not product or product['stock'] <= 0:
        bot.answer_callback_query(call.id, "❌ স্টক শেষ!")
        return
    
    ref = f"ANTO{random.randint(10000, 99999)}"
    pending_payments[str(call.message.chat.id)] = {
        "pid": pid,
        "product": product,
        "ref": ref
    }
    
    text = f"""╔══════════════════════════════╗
║        💳 **পেমেন্ট পেজ**        ║
╚══════════════════════════════╝

📦 **প্রোডাক্ট:** {product['name']}
💰 **টাকা:** ৳{product['price']}
📱 **bKash:** `{settings_db.get('bkash', BKASH_NUMBER)}`

**নির্দেশনা:**
1️⃣ উপরের bKash নম্বরে টাকা পাঠান
2️⃣ TRX আইডি পাঠান
3️⃣ স্ক্রিনশট পাঠান

🔖 **রেফারেন্স:** `{ref}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ TRX পাঠিয়েছি", callback_data="send_trx"),
        InlineKeyboardButton("❌ বাতিল", callback_data="back_main")
    )
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "send_trx")
def send_trx(call):
    bot.send_message(call.message.chat.id, "📝 **আপনার bKash TRX আইডি লিখুন:**", parse_mode="Markdown")
    bot.register_next_step_handler(call.message, process_trx)

def process_trx(message):
    if message.text.startswith('/'):
        return
    pending_payments[str(message.chat.id)]['trx'] = message.text
    bot.reply_to(message, "✅ TRX সংরক্ষিত!\n\n📸 **এখন পেমেন্টের স্ক্রিনশট পাঠান:**", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_screenshot)

def process_screenshot(message):
    if message.content_type != 'photo':
        bot.reply_to(message, "❌ দয়া করে স্ক্রিনশট পাঠান!")
        bot.register_next_step_handler(message, process_screenshot)
        return
    
    pending_data = pending_payments.get(str(message.chat.id))
    if not pending_data:
        return
    
    product = pending_data['product']
    
    admin_text = f"""╔══════════════════════════════╗
║        🆕 **নতুন অর্ডার**        ║
╚══════════════════════════════╝

👤 **ইউজার:** {message.chat.id}
👤 **নাম:** {message.from_user.first_name}
📦 **প্রোডাক্ট:** {product['name']}
💰 **টাকা:** ৳{product['price']}
🔢 **TRX আইডি:** `{pending_data['trx']}`
🔖 **রেফ:** `{pending_data['ref']}`
⏰ **সময়:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ অ্যাপ্রুভ", callback_data=f"approve_{message.chat.id}_{pending_data['pid']}"),
        InlineKeyboardButton("❌ রিজেক্ট", callback_data=f"reject_{message.chat.id}")
    )
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(message.chat.id, "✅ **অর্ডার অ্যাডমিনের কাছে পাঠানো হয়েছে!**\nঅ্যাপ্রুভের জন্য অপেক্ষা করুন ⏳", parse_mode="Markdown")
    
    del pending_payments[str(message.chat.id)]

# ================= অ্যাপ্রুভ =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve_order(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ তুমি অ্যাডমিন নও!")
        return
    
    _, uid, pid = call.data.split("_")
    uid = int(uid)
    product = products_db.get(pid)
    
    if not product or len(product['keys']) == 0:
        bot.send_message(ADMIN_ID, "❌ কোনো কী নেই!")
        bot.answer_callback_query(call.id, "কী নেই!")
        return
    
    key = product['keys'].pop(0)
    product['stock'] -= 1
    product['sold'] += 1
    save_db('products.json', products_db)
    
    # অর্ডার সেভ
    order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    if str(uid) not in users_db:
        users_db[str(uid)] = {"orders": []}
    users_db[str(uid)]["orders"].append({
        "id": order_id,
        "product": product['name'],
        "price": product['price'],
        "key": key,
        "date": str(datetime.now())
    })
    save_db('users.json', users_db)
    
    user_text = f"""╔══════════════════════════════╗
║   ✅ **পেমেন্ট অ্যাপ্রুভড!**   ║
╚══════════════════════════════╝

📦 **প্রোডাক্ট:** {product['name']}
🔑 **আপনার কী:** `{key}`
📥 **APK লিংক:** {product['apk_link']}

💝 কেনাকাটার জন্য ধন্যবাদ!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    bot.send_message(uid, user_text, parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"✅ অর্ডার অ্যাপ্রুভ করা হয়েছে!\n📦 বাকি স্টক: {product['stock']}")
    bot.answer_callback_query(call.id, "✅ অ্যাপ্রুভ করা হয়েছে!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_order(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ তুমি অ্যাডমিন নও!")
        return
    
    uid = int(call.data.split("_")[1])
    bot.send_message(uid, "❌ **পেমেন্ট রিজেক্ট করা হয়েছে!**\n\nদয়া করে সঠিক তথ্য দিয়ে আবার চেষ্টা করুন।\nযোগাযোগ: @PAPAJI_ANTO", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"❌ ইউজার {uid} এর অর্ডার রিজেক্ট করা হয়েছে!")
    bot.answer_callback_query(call.id, "❌ রিজেক্ট করা হয়েছে!")

# ================= মাই প্রোফাইল =================
@bot.callback_query_handler(func=lambda call: call.data == "my_profile")
def my_profile(call):
    user = users_db.get(str(call.message.chat.id), {})
    
    text = f"""╔══════════════════════════════╗
║        👤 **মাই প্রোফাইল**       ║
╚══════════════════════════════╝

🆔 **আইডি:** `{call.message.chat.id}`
👤 **নাম:** {user.get('name', 'Unknown')}
💰 **ব্যালেন্স:** ৳{user.get('balance', 0)}
📦 **অর্ডার:** {len(user.get('orders', []))}
👥 **রেফারেল:** {user.get('referrals', 0)}
📅 **জয়েন:** {user.get('joined', 'Unknown')[:10]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 ব্যাক", callback_data="back_main"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ================= মাই অর্ডার =================
@bot.callback_query_handler(func=lambda call: call.data == "my_orders")
def my_orders(call):
    user = users_db.get(str(call.message.chat.id), {})
    orders = user.get('orders', [])
    
    if not orders:
        text = "📭 **কোনো অর্ডার নেই!**\n\nশপিং করে অর্ডার করুন।"
    else:
        text = "╔══════════════════════════════╗\n║       📜 **অর্ডার হিস্ট্রি**      ║\n╚══════════════════════════════╝\n\n"
        for i, order in enumerate(orders[-10:], 1):
            text += f"{i}. 📦 {order['product']}\n   💰 ৳{order['price']}\n   📅 {order['date'][:10]}\n\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 ব্যাক", callback_data="back_main"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ================= রেফারেল =================
@bot.callback_query_handler(func=lambda call: call.data == "referral")
def referral(call):
    user = users_db.get(str(call.message.chat.id), {})
    bot_username = bot.get_me().username
    
    text = f"""╔══════════════════════════════╗
║       🔗 **রেফারেল প্রোগ্রাম**     ║
╚══════════════════════════════╝

👥 **ইওর রেফারেল:** {user.get('referrals', 0)}
💰 **আয়:** ৳{user.get('referral_earnings', 0)}

**🔗 ইওর লিংক:**
`https://t.me/{bot_username}?start=ref_{call.message.chat.id}`

**কিভাবে কাজ করে:**
1️⃣ লিংক শেয়ার করুন
2️⃣ ফ্রেন্ড জয়েন করলে
3️⃣ কমিশন পাবেন ১০%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📤 শেয়ার লিংক", url=f"https://t.me/share/url?url=https://t.me/{bot_username}?start=ref_{call.message.chat.id}"),
        InlineKeyboardButton("🔙 ব্যাক", callback_data="back_main")
    )
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ================= অ্যাড ব্যালেন্স =================
@bot.callback_query_handler(func=lambda call: call.data == "add_balance")
def add_balance_menu(call):
    text = f"""💰 **অ্যাড ব্যালেন্স**

📱 bKash: `{settings_db.get('bkash', BKASH_NUMBER)}`

**নির্দেশনা:**
1️⃣ bKash এ টাকা পাঠান
2️⃣ ট্রানজাকশন আইডি ও স্ক্রিনশট পাঠান
3️⃣ অ্যাডমিন অ্যাপ্রুভ করলে ব্যালেন্স এড হবে

**ন্যূনতম: ৳100**
━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 ব্যাক", callback_data="back_main"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ================= হাউ টু ইউজ =================
@bot.callback_query_handler(func=lambda call: call.data == "how_to_use")
def how_to_use(call):
    text = f"""📖 **হাউ টু ইউজ বট**

1️⃣ **প্রোডাক্ট কেনা:**
   • SHOP NOW বাটন চাপুন
   • প্রোডাক্ট সিলেক্ট করুন
   • বাই নাও চাপুন

2️⃣ **পেমেন্ট:**
   • bKash নম্বরে টাকা পাঠান
   • TRX আইডি পাঠান
   • স্ক্রিনশট পাঠান

3️⃣ **প্রোডাক্ট পাওয়া:**
   • অ্যাডমিন অ্যাপ্রুভ করবেন
   • কী ও লিংক পাবেন

━━━━━━━━━━━━━━━━━━━━
💝 **সাপোর্ট:** @PAPAJI_ANTO
━━━━━━━━━━━━━━━━━━━━"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 ব্যাক", callback_data="back_main"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ================= লাকি গেম =================
@bot.callback_query_handler(func=lambda call: call.data == "lucky_game")
def lucky_game(call):
    prizes = ["৳50", "৳100", "৳200", "ডিসকাউন্ট 10%", "ফ্রি প্রোডাক্ট", "আবার চেষ্টা"]
    prize = random.choice(prizes)
    
    text = f"🎲 **লাকি গেম** 🎲\n\nআপনি পেলেন: **{prize}** !\n\nযোগাযোগ করুন: @PAPAJI_ANTO"
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🔄 আবার খেলুন", callback_data="lucky_game"),
        InlineKeyboardButton("🔙 ব্যাক", callback_data="back_main")
    )
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ================= ওনার প্যানেল =================
@bot.message_handler(commands=['owner'])
def owner_panel(message):
    bot.send_message(message.chat.id, "🔑 **পাসওয়ার্ড লিখুন:**", parse_mode="Markdown")
    bot.register_next_step_handler(message, check_owner_password)

def check_owner_password(message):
    if message.text == ADMIN_PASSWORD:
        owner_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "❌ **ভুল পাসওয়ার্ড!**", parse_mode="Markdown")

def owner_menu(chat_id):
    text = """╔══════════════════════════════╗
║       👑 **ওনার প্যানেল**       ║
╚══════════════════════════════╝

📊 **কমান্ড লিস্ট:**

`/products` - সব প্রোডাক্ট দেখুন
`/addproduct নাম|মূল্য|এপিক লিংক|বিবরণ`
`/addkey প্রোডাক্ট_আইডি|কী`
`/removekey কী`
`/setstock প্রোডাক্ট_আইডি|স্টক`
`/addbalance ইউজার_আইডি|টাকা`
`/broadcast মেসেজ`
`/stats` - পরিসংখ্যান
`/users` - সব ইউজার
`/orders` - সব অর্ডার
`/setbkash নম্বর` - bKash নম্বর সেট
`/setchannel লিংক` - চ্যানেল লিংক সেট

━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    bot.send_message(chat_id, text, parse_mode="Markdown")

# ================= অ্যাডমিন কমান্ড =================
@bot.message_handler(commands=['addproduct'])
def add_product(message):
    if message.chat.id != ADMIN_ID:
        return
    
    try:
        _, data = message.text.split(" ", 1)
        name, price, apk_link, desc = data.split("|")
        
        new_id = str(len(products_db) + 1)
        products_db[new_id] = {
            "name": name,
            "price": int(price),
            "desc": desc,
            "apk_link": apk_link,
            "keys": [],
            "stock": 0,
            "sold": 0,
            "category": "mods"
        }
        save_db('products.json', products_db)
        bot.reply_to(message, f"✅ প্রোডাক্ট এড করা হয়েছে!\n🆔 আইডি: {new_id}\n📦 {name}\n💰 ৳{price}")
    except:
        bot.reply_to(message, "❌ `/addproduct নাম|মূল্য|এপিক লিংক|বিবরণ`")

@bot.message_handler(commands=['addkey'])
def add_key(message):
    if message.chat.id != ADMIN_ID:
        return
    
    try:
        _, data = message.text.split(" ", 1)
        pid, key = data.split("|")
        
        if pid not in products_db:
            bot.reply_to(message, "❌ প্রোডাক্ট আইডি ভুল!")
            return
        
        products_db[pid]['keys'].append(key.upper())
        products_db[pid]['stock'] += 1
        save_db('products.json', products_db)
        bot.reply_to(message, f"✅ কী এড করা হয়েছে!\n🔑 {key}\n📦 স্টক: {products_db[pid]['stock']}")
    except:
        bot.reply_to(message, "❌ `/addkey প্রোডাক্ট_আইডি|কী`")

@bot.message_handler(commands=['products'])
def list_products(message):
    if message.chat.id != ADMIN_ID:
        return
    
    text = "📦 **প্রোডাক্ট লিস্ট:**\n\n"
    for pid, p in products_db.items():
        text += f"🆔 {pid} | {p['name']}\n   💰 ৳{p['price']} | 📦 {p['stock']} | 📥 {p['sold']}\n\n"
    
    bot.reply_to(message, text)

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id != ADMIN_ID:
        return
    
    total_users = len(users_db)
    total_orders = sum(len(u.get('orders', [])) for u in users_db.values())
    total_keys = sum(len(p.get('keys', [])) for p in products_db.values())
    
    text = f"""📊 **বট পরিসংখ্যান**

👥 **ইউজার:** {total_users}
📦 **অর্ডার:** {total_orders}
🔑 **মোট কী:** {total_keys}
💰 **বিক্রি:** {sum(p.get('sold', 0) for p in products_db.values())}

━━━━━━━━━━━━━━━━━━━━"""
    
    bot.reply_to(message, text)

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.chat.id != ADMIN_ID:
        return
    
    msg = message.text.replace("/broadcast ", "")
    count = 0
    
    for uid in users_db.keys():
        try:
            bot.send_message(int(uid), f"📢 **ঘোষণা**\n\n{msg}", parse_mode="Markdown")
            count += 1
            time.sleep(0.05)
        except:
            pass
    
    bot.reply_to(message, f"✅ {count} জন ইউজারকে মেসেজ পাঠানো হয়েছে!")

@bot.message_handler(commands=['setbkash'])
def set_bkash(message):
    if message.chat.id != ADMIN_ID:
        return
    
    try:
        bkash = message.text.split()[1]
        settings_db['bkash'] = bkash
        save_db('settings.json', settings_db)
        bot.reply_to(message, f"✅ bKash নম্বর সেট করা হয়েছে: {bkash}")
    except:
        bot.reply_to(message, "❌ `/setbkash 019XXXXXXXX`")

@bot.message_handler(commands=['setchannel'])
def set_channel(message):
    if message.chat.id != ADMIN_ID:
        return
    
    try:
        channel = message.text.split()[1]
        settings_db['channel_url'] = channel
        save_db('settings.json', settings_db)
        bot.reply_to(message, f"✅ চ্যানেল লিংক সেট করা হয়েছে: {channel}")
    except:
        bot.reply_to(message, "❌ `/setchannel https://t.me/...`")

@bot.message_handler(commands=['users'])
def list_users(message):
    if message.chat.id != ADMIN_ID:
        return
    
    text = "👥 **ইউজার লিস্ট:**\n\n"
    for uid, u in list(users_db.items())[:50]:
        text += f"🆔 {uid} | {u.get('name', 'Unknown')}\n   💰 ৳{u.get('balance', 0)} | 📦 {len(u.get('orders', []))}\n\n"
    
    bot.reply_to(message, text)

# ================= ব্যাক টু মেনু =================
@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back_main(call):
    welcome_text = f"""╔══════════════════════════════╗
║      ✨ **ANTO X SHOP** ✨      ║
╚══════════════════════════════╝

💝 **হ্যালো {call.from_user.first_name}!**

⚠️ **প্লিজ সিলেক্ট ইওর প্রোডাক্ট** ⚠️

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 **ওনার:** {OWNER_NAME}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    bot.edit_message_caption(welcome_text, call.message.chat.id, call.message.message_id,
                            reply_markup=main_menu(), parse_mode="Markdown")

# ================= রান =================
if __name__ == "__main__":
    print("=" * 50)
    print("🔥 ANTO X SHOP BOT STARTED!")
    print(f"🤖 Bot: @{bot.get_me().username}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print(f"🔑 Admin Password: {ADMIN_PASSWORD}")
    print("=" * 50)
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
