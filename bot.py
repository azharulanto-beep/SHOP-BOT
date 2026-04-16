import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import json
import random
import string
import time
import hashlib
from datetime import datetime, timedelta

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ANTO@2026")

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
reviews_db = load_db('reviews.json')
warranty_db = load_db('warranty.json')
points_db = load_db('points.json')
coupons_db = load_db('coupons.json')
tickets_db = load_db('tickets.json')

# ====================== DEFAULT SETTINGS ======================
if not settings:
    settings = {
        "bot_name": "🔥 ANTO ULTIMATE STORE 🔥",
        "logo_url": "https://i.postimg.cc/qvt6CQjk/logo.jpg",
        "support_url": "https://t.me/PAPAJI_ANTO",
        "channel_url": "https://t.me/ANTO_X_SHOP",
        "currency": "৳",
        "welcome_bonus": 50,
        "referral_percent": 10,
        "points_rate": 10
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

# ====================== POINTS FUNCTIONS ======================
def get_points(uid):
    uid = str(uid)
    if uid not in points_db:
        points_db[uid] = {"points": 0, "history": []}
        save_db('points.json', points_db)
    return points_db[uid]["points"]

def add_points(uid, pts, reason=""):
    uid = str(uid)
    if uid not in points_db:
        points_db[uid] = {"points": 0, "history": []}
    points_db[uid]["points"] += pts
    points_db[uid]["history"].append({"type": "ADD", "points": pts, "reason": reason, "date": str(datetime.now())})
    save_db('points.json', points_db)

def deduct_points(uid, pts, reason=""):
    uid = str(uid)
    if get_points(uid) >= pts:
        points_db[uid]["points"] -= pts
        points_db[uid]["history"].append({"type": "DEDUCT", "points": pts, "reason": reason, "date": str(datetime.now())})
        save_db('points.json', points_db)
        return True
    return False

# ====================== PRODUCTS ======================
if not products:
    products = {
        "1": {
            "name": "🔥 DRIP CLIENT PRO",
            "price": 399,
            "desc": "Premium Gaming Mod\n✅ Non Root Support\n✅ 30 Days Access\n✅ Auto Update",
            "keys": ["DRIP-001", "DRIP-002", "DRIP-003"],
            "stock": 50,
            "sold": 0,
            "rating": 4.8,
            "warranty": 7,
            "category": "mods"
        },
        "2": {
            "name": "🎮 BGMI ESP HACK",
            "price": 299,
            "desc": "ESP + Aimbot\n✅ 100% Safe\n✅ Undetected\n✅ Smooth Gameplay",
            "keys": ["BGMI-001", "BGMI-002", "BGMI-003"],
            "stock": 30,
            "sold": 0,
            "rating": 4.9,
            "warranty": 7,
            "category": "mods"
        },
        "3": {
            "name": "📱 NETFLIX PREMIUM",
            "price": 299,
            "desc": "4K Ultra HD\n✅ 30 Days Access\n✅ Personal Account\n✅ All Devices",
            "keys": ["NF-001", "NF-002", "NF-003"],
            "stock": 20,
            "sold": 0,
            "rating": 4.7,
            "warranty": 30,
            "category": "accounts"
        }
    }
    save_db('products.json', products)

# ====================== MAIN MENU ======================
def main_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("🛍️ SHOP NOW", callback_data="shop"),
        InlineKeyboardButton("👤 MY PROFILE", callback_data="profile")
    )
    m.add(
        InlineKeyboardButton("💰 MY WALLET", callback_data="wallet"),
        InlineKeyboardButton("💎 MY POINTS", callback_data="points")
    )
    m.add(
        InlineKeyboardButton("📦 MY ORDERS", callback_data="orders"),
        InlineKeyboardButton("🎁 OFFERS", callback_data="offers")
    )
    m.add(
        InlineKeyboardButton("🔗 REFERRAL", callback_data="referral"),
        InlineKeyboardButton("⭐ REVIEWS", callback_data="reviews")
    )
    m.add(
        InlineKeyboardButton("🛡️ WARRANTY", callback_data="warranty"),
        InlineKeyboardButton("🎫 SUPPORT", callback_data="support")
    )
    m.add(
        InlineKeyboardButton("📞 SUPPORT", url=settings.get("support_url", "https://t.me/PAPAJI_ANTO")),
        InlineKeyboardButton("📢 JOIN CHANNEL", url=settings.get("channel_url", "https://t.me/ANTO_X_SHOP"))
    )
    return m

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
        add_points(uid, settings.get("welcome_bonus", 50), "🎁 Welcome Points")
    
    # Check referral
    if len(m.text.split()) > 1:
        ref_code = m.text.split()[1]
        if ref_code.startswith("ref_"):
            referrer = ref_code.replace("ref_", "")
            if referrer != str(uid) and users.get(referrer):
                users[uid]["referred_by"] = referrer
                users[referrer]["referrals"] += 1
                bonus = settings.get("welcome_bonus", 50)
                add_balance(referrer, bonus, "🔗 Referral Bonus")
                save_db('users.json', users)
                bot.send_message(int(referrer), f"🎉 New Referral!\n\n{m.from_user.first_name} joined using your link!\n💰 {settings.get('currency', '৳')}{bonus} added!")
    
    balance = get_balance(uid)
    points = get_points(uid)
    logo = settings.get("logo_url", "https://i.postimg.cc/qvt6CQjk/logo.jpg")
    bot_name = settings.get("bot_name", "🔥 ANTO ULTIMATE STORE 🔥")
    
    welcome = f"""{bot_name}

💝 Hello {m.from_user.first_name}!

💰 Balance: {settings.get('currency', '৳')}{balance}
💎 Points: {points}

Select an option below:"""
    
    bot.send_photo(m.chat.id, logo, caption=welcome, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== SHOP ======================
@bot.callback_query_handler(func=lambda c: c.data == "shop")
def shop(c):
    if not products:
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
        bot.edit_message_caption("📭 No products available!", c.message.chat.id, c.message.message_id, reply_markup=markup)
        return
    
    m = InlineKeyboardMarkup(row_width=1)
    for pid, p in products.items():
        stock_icon = "🟢" if p.get('stock', 0) > 0 else "🔴"
        m.add(InlineKeyboardButton(f"{stock_icon} {p['name']} - {settings.get('currency', '৳')}{p['price']} ⭐{p.get('rating', 0)}", callback_data=f"prod_{pid}"))
    m.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption("🛍️ SELECT YOUR PRODUCT:\n━━━━━━━━━━━━━━━━━━━━", c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("prod_"))
def prod_detail(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p:
        return
    
    text = f"""╔════════════════════════════╗
║      📦 {p['name']}      ║
╚════════════════════════════╝

{p.get('desc', 'No description')}

┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 💰 Price: {settings.get('currency', '৳')}{p['price']}
┃ 📊 Stock: {p.get('stock', 0)} left
┃ ⭐ Rating: {p.get('rating', 0)}/5
┃ 📈 Sold: {p.get('sold', 0)}
┃ 🛡️ Warranty: {p.get('warranty', 7)} days
┗━━━━━━━━━━━━━━━━━━━━━━━━┛

✅ Instant Delivery
✅ 24/7 Support
✅ Money Back Guarantee"""
    
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("🛒 BUY NOW", callback_data=f"buy_{pid}"),
        InlineKeyboardButton("⭐ RATE", callback_data=f"rate_{pid}")
    )
    m.add(InlineKeyboardButton("🔙 BACK", callback_data="shop"))
    m.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

# ====================== BUY SYSTEM ======================
pending_purchase = {}

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p or p.get('stock', 0) <= 0:
        bot.answer_callback_query(c.id, "❌ OUT OF STOCK!")
        return
    
    pending_purchase[str(c.message.chat.id)] = {"pid": pid, "product": p, "price": p['price']}
    balance = get_balance(c.message.chat.id)
    points = get_points(c.message.chat.id)
    
    text = f"""💳 PAYMENT OPTION

📦 Product: {p['name']}
💰 Amount: {settings.get('currency', '৳')}{p['price']}

💵 Your Balance: {settings.get('currency', '৳')}{balance}
💎 Your Points: {points} (100 points = {settings.get('currency', '৳')}10)

Choose payment method:"""
    
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("💳 WALLET", callback_data="pay_wallet"),
        InlineKeyboardButton("💎 POINTS", callback_data="pay_points")
    )
    m.add(InlineKeyboardButton("❌ CANCEL", callback_data="home"))
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data == "pay_wallet")
def pay_wallet(c):
    uid = str(c.message.chat.id)
    pend = pending_purchase.get(uid)
    if not pend:
        bot.answer_callback_query(c.id, "❌ Session expired!")
        return
    
    if deduct_balance(uid, pend['price'], f"🛒 {pend['product']['name']}"):
        # Complete purchase
        key = pend['product']['keys'].pop(0) if pend['product'].get('keys') else "OUT_OF_STOCK"
        pend['product']['stock'] -= 1
        pend['product']['sold'] = pend['product'].get('sold', 0) + 1
        save_db('products.json', products)
        
        # Save order
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        if uid not in orders:
            orders[uid] = []
        orders[uid].append({
            "id": order_id,
            "product": pend['product']['name'],
            "price": pend['price'],
            "key": key,
            "date": str(datetime.now()),
            "method": "WALLET",
            "warranty_expiry": str(datetime.now() + timedelta(days=pend['product'].get('warranty', 7)))
        })
        save_db('orders.json', orders)
        
        # Add loyalty points
        points_earned = int(pend['price'] / settings.get('points_rate', 10))
        add_points(uid, points_earned, f"🛒 Purchase: {pend['product']['name']}")
        
        new_balance = get_balance(uid)
        new_points = get_points(uid)
        
        # Save warranty
        warranty_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        warranty_db[warranty_id] = {
            "user_id": uid,
            "product": pend['product']['name'],
            "order_id": order_id,
            "expiry": str(datetime.now() + timedelta(days=pend['product'].get('warranty', 7))),
            "status": "active"
        }
        save_db('warranty.json', warranty_db)
        
        text = f"""✅ PURCHASE SUCCESSFUL! 🎉

📦 Product: {pend['product']['name']}
💰 Paid: {settings.get('currency', '৳')}{pend['price']}
🔑 Your Key: `{key}`
🆔 Order ID: `{order_id}`
🛡️ Warranty ID: `{warranty_id}`

💎 Points Earned: {points_earned}
💵 New Balance: {settings.get('currency', '৳')}{new_balance}
💎 Total Points: {new_points}

Thank you for shopping! 🎉"""
        
        m = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
        bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")
        del pending_purchase[uid]
    else:
        bot.answer_callback_query(c.id, f"❌ Insufficient balance! Need {settings.get('currency', '৳')}{pend['price'] - get_balance(uid)} more!")

@bot.callback_query_handler(func=lambda c: c.data == "pay_points")
def pay_points(c):
    uid = str(c.message.chat.id)
    pend = pending_purchase.get(uid)
    if not pend:
        bot.answer_callback_query(c.id, "❌ Session expired!")
        return
    
    points_needed = pend['price'] * 10  # 100 points = 10 currency
    current_points = get_points(uid)
    
    if current_points >= points_needed:
        deduct_points(uid, points_needed, f"🛒 {pend['product']['name']}")
        
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
            "method": "POINTS",
            "warranty_expiry": str(datetime.now() + timedelta(days=pend['product'].get('warranty', 7)))
        })
        save_db('orders.json', orders)
        
        warranty_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        warranty_db[warranty_id] = {
            "user_id": uid,
            "product": pend['product']['name'],
            "order_id": order_id,
            "expiry": str(datetime.now() + timedelta(days=pend['product'].get('warranty', 7))),
            "status": "active"
        }
        save_db('warranty.json', warranty_db)
        
        new_points = get_points(uid)
        
        text = f"""✅ PURCHASE SUCCESSFUL! 🎉

📦 Product: {pend['product']['name']}
💎 Paid: {points_needed} Points
🔑 Your Key: `{key}`
🆔 Order ID: `{order_id}`
🛡️ Warranty ID: `{warranty_id}`

💎 Remaining Points: {new_points}

Thank you for shopping! 🎉"""
        
        m = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
        bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")
        del pending_purchase[uid]
    else:
        bot.answer_callback_query(c.id, f"❌ Insufficient points! Need {points_needed} points, you have {current_points}")

# ====================== PROFILE ======================
@bot.callback_query_handler(func=lambda c: c.data == "profile")
def profile(c):
    u = users.get(str(c.message.chat.id), {})
    balance = get_balance(c.message.chat.id)
    points = get_points(c.message.chat.id)
    order_count = len(orders.get(str(c.message.chat.id), []))
    
    text = f"""╔════════════════════════════╗
║        👤 MY PROFILE        ║
╚════════════════════════════╝

🆔 ID: `{c.message.chat.id}`
👤 Name: {u.get('name', 'Unknown')}
📅 Joined: {u.get('joined', 'Unknown')[:10]}

💰 Balance: {settings.get('currency', '৳')}{balance}
💎 Points: {points}
📦 Orders: {order_count}
👥 Referrals: {u.get('referrals', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

# ====================== WALLET ======================
@bot.callback_query_handler(func=lambda c: c.data == "wallet")
def wallet_view(c):
    balance = get_balance(c.message.chat.id)
    transactions = wallet.get(str(c.message.chat.id), {}).get('transactions', [])[-5:]
    
    text = f"""╔════════════════════════════╗
║        💰 MY WALLET        ║
╚════════════════════════════╝

💵 Current Balance: {settings.get('currency', '৳')}{balance}

📜 Recent Transactions:
"""
    if transactions:
        for t in reversed(transactions):
            text += f"• {t['type']} {settings.get('currency', '৳')}{t['amount']} - {t['date'][:16]}\n"
    else:
        text += "• No transactions yet\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━━━"
    
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("➕ ADD BALANCE", callback_data="add_balance"), InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

# ====================== POINTS ======================
@bot.callback_query_handler(func=lambda c: c.data == "points")
def points_view(c):
    points = get_points(c.message.chat.id)
    history = points_db.get(str(c.message.chat.id), {}).get('history', [])[-5:]
    
    text = f"""╔════════════════════════════╗
║        💎 MY POINTS        ║
╚════════════════════════════╝

💎 Current Points: {points}

📜 Recent Activity:
"""
    if history:
        for h in reversed(history):
            text += f"• {h['type']} {h['points']} pts - {h['date'][:16]}\n"
    else:
        text += "• No activity yet\n"
    
    text += "\n💡 100 points = 10 currency discount"
    
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

# ====================== ORDERS ======================
@bot.callback_query_handler(func=lambda c: c.data == "orders")
def orders_view(c):
    uid = str(c.message.chat.id)
    user_orders = orders.get(uid, [])
    
    if not user_orders:
        text = "📭 NO ORDERS YET!\n\nStart shopping now!"
    else:
        text = "╔════════════════════════════╗\n║        📦 MY ORDERS        ║\n╚════════════════════════════╝\n\n"
        for o in user_orders[-10:]:
            text += f"🆔 Order: `{o.get('id', 'N/A')}`\n"
            text += f"📦 Product: {o['product']}\n"
            text += f"💰 Amount: {settings.get('currency', '৳')}{o['price']}\n"
            text += f"🔑 Key: `{o.get('key', 'N/A')}`\n"
            text += f"📅 Date: {o['date'][:10]}\n"
            text += f"💳 Method: {o.get('method', 'N/A')}\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

# ====================== OFFERS ======================
@bot.callback_query_handler(func=lambda c: c.data == "offers")
def offers(c):
    text = """╔════════════════════════════╗
║        🎁 ACTIVE OFFERS        ║
╚════════════════════════════╝

🔥 BUY 1 GET 1 FREE
• On selected items
• Use code: BOGO2024

🎉 20% OFF ON FIRST PURCHASE
• Automatically applied

💰 REFERRAL BONUS
• {currency}50 per referral
• Unlimited earnings

💎 LOYALTY POINTS
• {points} points per {currency}100 spent
• Redeem for discounts

━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    text = text.replace("{currency}", settings.get('currency', '৳')).replace("{points}", str(settings.get('points_rate', 10)))
    
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

# ====================== REFERRAL ======================
@bot.callback_query_handler(func=lambda c: c.data == "referral")
def referral(c):
    uname = bot.get_me().username
    u = users.get(str(c.message.chat.id), {})
    
    text = f"""╔════════════════════════════╗
║        🔗 REFERRAL PROGRAM        ║
╚════════════════════════════╝

💰 Earn {settings.get('referral_percent', 10)}% commission on every purchase!

👥 Your Referrals: {u.get('referrals', 0)}

🔗 Your Link:
`https://t.me/{uname}?start=ref_{c.message.chat.id}`

📌 How it works:
1️⃣ Share your link
2️⃣ Friends join using your link
3️⃣ You get {settings.get('referral_percent', 10)}% of their purchases

━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    m = InlineKeyboardMarkup()
    m.add(
        InlineKeyboardButton("📤 SHARE LINK", url=f"https://t.me/share/url?url=https://t.me/{uname}?start=ref_{c.message.chat.id}&text=🔥 Join ANTO SHOP for premium services! 💝"),
        InlineKeyboardButton("🏠 HOME", callback_data="home")
    )
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

# ====================== REVIEWS ======================
@bot.callback_query_handler(func=lambda c: c.data == "reviews")
def reviews(c):
    all_reviews = list(reviews_db.values())[-10:]
    
    if not all_reviews:
        text = "⭐ NO REVIEWS YET!\n\nBe the first to leave a review!"
    else:
        text = "╔════════════════════════════╗\n║        ⭐ CUSTOMER REVIEWS        ║\n╚════════════════════════════╝\n\n"
        for r in reversed(all_reviews):
            stars = "⭐" * r.get('rating', 0)
            text += f"{stars}\n"
            text += f"📦 {r.get('product', 'N/A')}\n"
            text += f"💬 {r.get('comment', 'N/A')[:50]}\n"
            text += f"👤 {r.get('user', 'Anonymous')}\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("⭐ LEAVE REVIEW", callback_data="leave_review"), InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data == "leave_review")
def leave_review(c):
    bot.send_message(c.message.chat.id, "📝 **Send your review:**\n\nFormat: `PRODUCT_ID|RATING|COMMENT`\n\nExample: `1|5|Amazing product!`", parse_mode="Markdown")
    bot.register_next_step_handler(c.message, save_review)

def save_review(m):
    try:
        pid, rating, comment = m.text.split("|")
        rating = int(rating)
        product = products.get(pid, {})
        
        review_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        reviews_db[review_id] = {
            "user": m.from_user.first_name,
            "user_id": str(m.chat.id),
            "product": product.get('name', 'Unknown'),
            "product_id": pid,
            "rating": rating,
            "comment": comment,
            "date": str(datetime.now())
        }
        save_db('reviews.json', reviews_db)
        
        # Update product rating
        product_reviews = [r for r in reviews_db.values() if r.get('product_id') == pid]
        if product_reviews:
            avg_rating = sum(r.get('rating', 0) for r in product_reviews) / len(product_reviews)
            products[pid]['rating'] = round(avg_rating, 1)
            save_db('products.json', products)
        
        bot.reply_to(m, "✅ Review added! Thank you for your feedback! ⭐")
    except:
        bot.reply_to(m, "❌ Wrong format! Use: `1|5|Your comment here`", parse_mode="Markdown")

# ====================== WARRANTY ======================
@bot.callback_query_handler(func=lambda c: c.data == "warranty")
def warranty_menu(c):
    text = """╔════════════════════════════╗
║        🛡️ WARRANTY SYSTEM        ║
╚════════════════════════════╝

✅ 7 Days Warranty on All Products
✅ 30 Days Premium Warranty Available
✅ Instant Replacement for Defective Keys

📌 **Commands:**
`/checkwarranty WARRANTY_ID` - Check warranty status
`/claimwarranty ORDER_ID` - Claim warranty

━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

@bot.message_handler(commands=['checkwarranty'])
def check_warranty(m):
    try:
        warranty_id = m.text.split()[1]
        w = warranty_db.get(warranty_id)
        if not w:
            bot.reply_to(m, "❌ Invalid warranty ID!")
            return
        
        expiry = datetime.fromisoformat(w['expiry'])
        days_left = (expiry - datetime.now()).days
        
        if days_left > 0:
            status = f"✅ ACTIVE - {days_left} days left"
        else:
            status = "❌ EXPIRED"
        
        text = f"""🛡️ WARRANTY INFO

Warranty ID: `{warranty_id}`
Product: {w.get('product', 'N/A')}
Status: {status}
Expiry: {w.get('expiry', 'N/A')[:10]}"""
        
        bot.reply_to(m, text, parse_mode="Markdown")
    except:
        bot.reply_to(m, "❌ Use: `/checkwarranty WARRANTY_ID`", parse_mode="Markdown")

@bot.message_handler(commands=['claimwarranty'])
def claim_warranty(m):
    try:
        order_id = m.text.split()[1]
        
        # Find order
        for uid, user_orders in orders.items():
            for o in user_orders:
                if o.get('id') == order_id:
                    # Check warranty expiry
                    expiry = datetime.fromisoformat(o.get('warranty_expiry', '2000-01-01'))
                    if datetime.now() > expiry:
                        bot.reply_to(m, "❌ Warranty expired! Can't claim.")
                        return
                    
                    # Get new key
                    pid = None
                    for p_id, p in products.items():
                        if p['name'] == o['product']:
                            pid = p_id
                            break
                    
                    if pid and products[pid].get('keys'):
                        new_key = products[pid]['keys'].pop(0)
                        products[pid]['stock'] -= 1
                        save_db('products.json', products)
                        
                        # Update order with new key
                        o['key'] = new_key
                        o['claim_date'] = str(datetime.now())
                        save_db('orders.json', orders)
                        
                        bot.reply_to(m, f"✅ Warranty Claim Approved!\n\nNew Key: `{new_key}`", parse_mode="Markdown")
                        bot.send_message(ADMIN_ID, f"🛡️ Warranty claimed for order {order_id} by user {m.chat.id}")
                    else:
                        bot.reply_to(m, "❌ No replacement key available! Contact admin.")
                    return
        
        bot.reply_to(m, "❌ Order not found!")
    except:
        bot.reply_to(m, "❌ Use: `/claimwarranty ORDER_ID`", parse_mode="Markdown")

# ====================== SUPPORT TICKET ======================
@bot.callback_query_handler(func=lambda c: c.data == "support")
def support_menu(c):
    text = """🎫 SUPPORT TICKET SYSTEM

📌 **Commands:**
`/createticket` - Create new support ticket
`/mytickets` - View your tickets

━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("🎫 CREATE TICKET", callback_data="create_ticket"), InlineKeyboardButton("🏠 HOME", callback_data="home"))
    
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data == "create_ticket")
def create_ticket(c):
    bot.send_message(c.message.chat.id, "📝 **Describe your issue:**\n\nSend your message and admin will reply soon.")
    bot.register_next_step_handler(c.message, save_ticket)

def save_ticket(m):
    ticket_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    tickets_db[ticket_id] = {
        "user_id": str(m.chat.id),
        "user_name": m.from_user.first_name,
        "issue": m.text,
        "status": "open",
        "created": str(datetime.now()),
        "messages": []
    }
    save_db('tickets.json', tickets_db)
    
    # Notify admin
    admin_text = f"🆕 NEW TICKET!\n\nID: {ticket_id}\nUser: {m.chat.id}\nIssue: {m.text}"
    bot.send_message(ADMIN_ID, admin_text)
    
    bot.reply_to(m, f"✅ Ticket created!\n\nTicket ID: `{ticket_id}`\n\nAdmin will reply soon.", parse_mode="Markdown")

@bot.message_handler(commands=['mytickets'])
def my_tickets(m):
    user_tickets = {tid: t for tid, t in tickets_db.items() if t.get('user_id') == str(m.chat.id)}
    
    if not user_tickets:
        bot.reply_to(m, "📭 No tickets found!")
        return
    
    text = "🎫 YOUR TICKETS\n\n"
    for tid, t in user_tickets.items():
        status_emoji = "🟢" if t['status'] == 'open' else "🔴"
        text += f"{status_emoji} `{tid}` - {t['created'][:10]}\n"
    
    bot.reply_to(m, text, parse_mode="Markdown")

# ====================== ADD BALANCE ======================
@bot.callback_query_handler(func=lambda c: c.data == "add_balance")
def add_balance_menu(c):
    text = f"""💰 ADD BALANCE

📱 BKash: `01918591988`
📱 Nagad: `01918591988`

Instructions:
1. Send money to any number
2. Send TRX ID and amount
3. Send screenshot

Minimum: 100 {settings.get('currency', '৳')}
Maximum: 5000 {settings.get('currency', '৳')}

━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    m = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id, reply_markup=m, parse_mode="Markdown")
    bot.send_message(c.message.chat.id, "📝 Send amount and TRX ID:\n\nExample: `500 8Y7X9K2M4N`", parse_mode="Markdown")
    bot.register_next_step_handler(c.message, process_add_balance)

def process_add_balance(m):
    try:
        amt, trx = m.text.split()
        amt = int(amt)
        
        admin_text = f"""💰 BALANCE REQUEST

User: {m.chat.id}
Name: {m.from_user.first_name}
Amount: {settings.get('currency', '৳')}{amt}
TRX: {trx}"""
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_bal_{m.chat.id}_{amt}"),
            InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{m.chat.id}")
        )
        
        bot.send_message(ADMIN_ID, admin_text, reply_markup=markup)
        bot.reply_to(m, "✅ Request sent to admin! Please wait.")
    except:
        bot.reply_to(m, "❌ Wrong format! Use: `500 8Y7X9K2M4N`", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("approve_bal_"))
def approve_balance(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "❌ You are not admin!")
        return
    
    _, _, uid, amt = c.data.split("_")
    add_balance(int(uid), int(amt), "Admin Add")
    bot.send_message(int(uid), f"✅ {settings.get('currency', '৳')}{amt} added to your wallet!", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"✅ Added {settings.get('currency', '৳')}{amt} to user {uid}")
    bot.answer_callback_query(c.id, "✅ Balance added!")

@bot.callback_query_handler(func=lambda c: c.data.startswith("reject_"))
def reject_action(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "❌ You are not admin!")
        return
    
    uid = c.data.split("_")[1]
    bot.send_message(int(uid), "❌ Request rejected! Please try again with correct information.", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"❌ Rejected request for user {uid}")
    bot.answer_callback_query(c.id, "✅ Rejected!")

# ====================== HOME ======================
@bot.callback_query_handler(func=lambda c: c.data == "home")
def home(c):
    balance = get_balance(c.message.chat.id)
    points = get_points(c.message.chat.id)
    logo = settings.get("logo_url", "https://i.postimg.cc/qvt6CQjk/logo.jpg")
    bot_name = settings.get("bot_name", "🔥 ANTO ULTIMATE STORE 🔥")
    
    welcome = f"""{bot_name}

💝 Welcome back {c.from_user.first_name}!

💰 Balance: {settings.get('currency', '৳')}{balance}
💎 Points: {points}

Select an option below:"""
    
    bot.edit_message_caption(welcome, c.message.chat.id, c.message.message_id, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== ADMIN PANEL (PASSWORD PROTECTED) ======================
admin_session = {}

@bot.message_handler(commands=['admin'])
def admin_login(m):
    bot.send_message(m.chat.id, "🔐 **ENTER ADMIN PASSWORD:**", parse_mode="Markdown")
    bot.register_next_step_handler(m, verify_admin)

def verify_admin(m):
    if m.text == ADMIN_PASSWORD:
        admin_session[str(m.chat.id)] = True
        show_admin_panel(m.chat.id)
    else:
        bot.send_message(m.chat.id, "❌ **WRONG PASSWORD!**", parse_mode="Markdown")

def show_admin_panel(chat_id):
    text = """╔══════════════════════════════════════╗
║              👑 ADMIN PANEL              ║
╚══════════════════════════════════════╝

📊 **STATISTICS:**
`/stats` - View bot statistics

📦 **PRODUCT MANAGEMENT:**
`/addproduct NAME|PRICE|DESC` - Add product
`/addkey PID|KEY` - Add product key
`/products` - List all products
`/delproduct PID` - Delete product

💰 **WALLET MANAGEMENT:**
`/addbalance UID AMOUNT` - Add balance
`/users` - List all users

🖼️ **SETTINGS:**
`/setlogo URL` - Change bot logo
`/setname NAME` - Change bot name
`/setcurrency SYMBOL` - Change currency

📢 **OTHER:**
`/broadcast MSG` - Send to all users
`/tickets` - View support tickets

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    bot.send_message(chat_id, text, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ Access denied! Use /admin first.")
        return
    
    total_users = len(users)
    total_orders = sum(len(o) for o in orders.values())
    total_keys = sum(len(p.get('keys', [])) for p in products.values())
    total_balance = sum(w.get('balance', 0) for w in wallet.values())
    total_points = sum(p.get('points', 0) for p in points_db.values())
    
    text = f"""📊 **BOT STATISTICS**

👥 Total Users: {total_users}
📦 Total Orders: {total_orders}
🔑 Total Keys: {total_keys}
💰 Total Balance: {settings.get('currency', '৳')}{total_balance}
💎 Total Points: {total_points}
📦 Total Products: {len(products)}"""
    
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['addproduct'])
def add_product(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ Access denied! Use /admin first.")
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
            "sold": 0,
            "rating": 0,
            "warranty": 7,
            "category": "general"
        }
        save_db('products.json', products)
        bot.reply_to(m, f"✅ Product added! ID: {new_id}\n{name} - {settings.get('currency', '৳')}{price}")
    except:
        bot.reply_to(m, "❌ Use: `/addproduct NAME|PRICE|DESC`", parse_mode="Markdown")

@bot.message_handler(commands=['addkey'])
def add_key(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ Access denied! Use /admin first.")
        return
    
    try:
        _, pid, key = m.text.split("|")
        if pid in products:
            products[pid]['keys'].append(key.upper())
            products[pid]['stock'] += 1
            save_db('products.json', products)
            bot.reply_to(m, f"✅ Key added: {key}")
        else:
            bot.reply_to(m, "❌ Product not found!")
    except:
        bot.reply_to(m, "❌ Use: `/addkey PID|KEY`", parse_mode="Markdown")

@bot.message_handler(commands=['products'])
def list_products(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ Access denied! Use /admin first.")
        return
    
    text = "📦 **PRODUCTS:**\n\n"
    for pid, p in products.items():
        text += f"🆔 {pid} | {p['name']}\n   💰 {settings.get('currency', '৳')}{p['price']} | 🔑 {len(p.get('keys', []))} | 📦 {p.get('stock', 0)}\n\n"
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['users'])
def list_users(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ Access denied! Use /admin first.")
        return
    
    text = "👥 **USERS:**\n\n"
    for uid, u in list(users.items())[:30]:
        balance = get_balance(uid)
        points = get_points(uid)
        text += f"🆔 {uid} | {u.get('name', 'Unknown')}\n   💰 {settings.get('currency', '৳')}{balance} | 💎 {points}\n\n"
    bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['setlogo'])
def set_logo(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ Access denied! Use /admin first.")
        return
    
    try:
        logo_url = m.text.split()[1]
        settings['logo_url'] = logo_url
        save_db('settings.json', settings)
        bot.reply_to(m, f"✅ Logo updated!\n{logo_url}")
    except:
        bot.reply_to(m, "❌ Use: `/setlogo URL`", parse_mode="Markdown")

@bot.message_handler(commands=['setname'])
def set_name(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ Access denied! Use /admin first.")
        return
    
    name = m.text.replace("/setname ", "")
    settings['bot_name'] = name
    save_db('settings.json', settings)
    bot.reply_to(m, f"✅ Bot name updated!\n{name}")

@bot.message_handler(commands=['setcurrency'])
def set_currency(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ Access denied! Use /admin first.")
        return
    
    currency = m.text.split()[1]
    settings['currency'] = currency
    save_db('settings.json', settings)
    bot.reply_to(m, f"✅ Currency updated! {currency}")

@bot.message_handler(commands=['broadcast'])
def broadcast(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ Access denied! Use /admin first.")
        return
    
    msg = m.text.replace("/broadcast ", "")
    count = 0
    for uid in users:
        try:
            bot.send_message(int(uid), f"📢 **ANNOUNCEMENT**\n\n{msg}", parse_mode="Markdown")
            count += 1
            time.sleep(0.05)
        except:
            pass
    bot.reply_to(m, f"✅ Sent to {count} users")

@bot.message_handler(commands=['tickets'])
def list_tickets(m):
    if str(m.chat.id) not in admin_session:
        bot.reply_to(m, "❌ Access denied! Use /admin first.")
        return
    
    if not tickets_db:
        bot.reply_to(m, "📭 No tickets!")
        return
    
    text = "🎫 **TICKETS:**\n\n"
    for tid, t in tickets_db.items():
        status = "🟢 OPEN" if t['status'] == 'open' else "🔴 CLOSED"
        text += f"`{tid}` | {status} | {t['user_name']}\n"
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

# ====================== RUN ======================
if __name__ == "__main__":
    print("=" * 60)
    print("🔥 ANTO ULTIMATE STORE BOT STARTED!")
    print(f"🤖 Bot: @{bot.get_me().username}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("=" * 60)
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
