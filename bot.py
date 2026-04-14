import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import os
import json
import time
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

bot = telebot.TeleBot(TOKEN)

# ================= DATABASE (JSON FILE) =================
# User data store
user_data = {}
orders = {}

# ================= PRODUCTS STRUCTURE =================
products = {
    "mods": {
        "name": "🎮 Game Mods",
        "icon": "🎮",
        "items": {
            "1": {"name": "Reaper X Pro - Root", "price": "349", "stock": 2, "bkash": "01918591988", "keys": ["REAPER-X-001"], "link": "https://t.me/whitexmodzstorefiles", "desc": "🎯 10 Day Access\n✅ Root Required\n✅ All Features Unlocked"},
            "2": {"name": "Reaper X Pro - Non Root", "price": "399", "stock": 3, "bkash": "01918591988", "keys": ["REAPER-NR-001"], "link": "https://t.me/whitexmodzstorefiles", "desc": "🎯 10 Day Access\n✅ No Root Required\n✅ VIP Features"},
            "3": {"name": "VIP Panel Access", "price": "599", "stock": 5, "bkash": "01918591988", "keys": ["VIP-001"], "link": "https://t.me/whitexmodzstorefiles", "desc": "🎯 30 Day Access\n✅ Full Panel Control\n✅ Premium Support"}
        }
    },
    "accounts": {
        "name": "📱 Premium Accounts",
        "icon": "📱",
        "items": {
            "4": {"name": "Netflix Premium", "price": "299", "stock": 10, "bkash": "01918591988", "keys": ["NF-001"], "link": "https://t.me/whitexmodzstorefiles", "desc": "🎯 30 Day Access\n✅ 4K Quality\n✅ Personal Account"},
            "5": {"name": "Spotify Premium", "price": "199", "stock": 15, "bkash": "01918591988", "keys": ["SP-001"], "link": "https://t.me/whitexmodzstorefiles", "desc": "🎯 12 Months\n✅ Ad-Free\n✅ Download Music"},
            "6": {"name": "Disney+ Hotstar", "price": "399", "stock": 8, "bkash": "01918591988", "keys": ["DS-001"], "link": "https://t.me/whitexmodzstorefiles", "desc": "🎯 1 Year\n✅ All Content\n✅ 4K Quality"}
        }
    },
    "tools": {
        "name": "🛠️ Hacking Tools",
        "icon": "🛠️",
        "items": {
            "7": {"name": "Termux Tools Pack", "price": "499", "stock": 20, "bkash": "01918591988", "keys": ["TRM-001"], "link": "https://t.me/whitexmodzstorefiles", "desc": "🎯 Lifetime Access\n✅ 100+ Tools\n✅ Updated Regularly"},
            "8": {"name": "VPN Premium", "price": "299", "stock": 25, "bkash": "01918591988", "keys": ["VPN-001"], "link": "https://t.me/whitexmodzstorefiles", "desc": "🎯 1 Year\n✅ Unlimited Bandwidth\n✅ 50+ Countries"}
        }
    }
}

# Pending payments
pending_payments = {}

# ================= MAIN MENU =================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛍️ Shop Store Now", callback_data="shop_now"),
        InlineKeyboardButton("👤 My Profile", callback_data="my_profile"),
        InlineKeyboardButton("💰 Add Balance", callback_data="add_balance"),
        InlineKeyboardButton("📈 All History", callback_data="my_orders"),
        InlineKeyboardButton("🔗 Referral", callback_data="referral"),
        InlineKeyboardButton("📖 How To Use Bot", callback_data="how_to_use"),
        InlineKeyboardButton("📞 Connect Helpline", url="https://t.me/WhiteXModz"),
        InlineKeyboardButton("🎲 Lucky Game", callback_data="lucky_game")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    # Save user
    if str(message.chat.id) not in user_data:
        user_data[str(message.chat.id)] = {
            "balance": 0,
            "orders": [],
            "joined": str(datetime.now()),
            "referrals": 0
        }
    
    welcome_text = f"""✨ **WELCOME TO OUR STORE** ✨

Hello, {message.from_user.first_name} ❤️!

• 🏅 **Store:** Buy premium services. Instant Delivery!!
• 💰 **Profile:** Your Account Details.
• 📦 **Deposit:** Add Funds to Wallet.
• 📈 **History:** Track your Orders.
• 🔗 **Referral:** Earn by inviting Friends.
• 👥 **How to Use:** How to buy
• 🔑 **Key Help:** Get Support from Owner
• 🎲 **Lucky Spin:** Win Exciting Prizes"""

    bot.send_photo(message.chat.id, "https://i.postimg.cc/ZnTLxtW2/logo.jpg", 
                   caption=welcome_text, reply_markup=main_menu(), parse_mode="Markdown")

# ================= SHOP NOW (CATEGORIES) =================
@bot.callback_query_handler(func=lambda call: call.data == "shop_now")
def shop_now(call):
    markup = InlineKeyboardMarkup(row_width=1)
    for cat_id, cat in products.items():
        markup.add(InlineKeyboardButton(f"{cat['icon']} {cat['name']}", callback_data=f"cat_{cat_id}"))
    markup.add(InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main"))
    
    bot.edit_message_caption("🛍️ **SELECT CATEGORY**\n\nChoose a product category:", 
                            call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ================= SHOW PRODUCTS IN CATEGORY =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def show_products(call):
    cat_id = call.data.replace("cat_", "")
    category = products.get(cat_id)
    
    if not category:
        return
    
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, item in category['items'].items():
        markup.add(InlineKeyboardButton(
            f"{item['name']} - ₹{item['price']} (Stock: {item['stock']})", 
            callback_data=f"product_{cat_id}_{pid}"
        ))
    markup.add(InlineKeyboardButton("🔙 Back to Categories", callback_data="shop_now"))
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="back_main"))
    
    bot.edit_message_caption(f"📦 **{category['name']}**\n\nSelect a product:", 
                            call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ================= PRODUCT DETAILS =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def product_detail(call):
    _, cat_id, pid = call.data.split("_")
    product = products[cat_id]['items'].get(pid)
    
    if not product:
        bot.answer_callback_query(call.id, "Product not found!")
        return
    
    text = f"""📦 **{product['name']}**

{product['desc']}

💰 **Price:** ₹{product['price']}
📊 **Stock Available:** {product['stock']}

✅ **Package Info:**
• Super Fast Delivery
• 24/7 Support
• Instant Replacement

Tap **Buy Now** to purchase!"""

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛒 Buy Now", callback_data=f"buy_{cat_id}_{pid}"),
        InlineKeyboardButton("🔙 Back", callback_data=f"cat_{cat_id}")
    )
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="back_main"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")

# ================= BUY PRODUCT =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_product(call):
    _, cat_id, pid = call.data.split("_")
    product = products[cat_id]['items'].get(pid)
    
    if not product or product['stock'] <= 0:
        bot.answer_callback_query(call.id, "❌ Out of stock!")
        return
    
    # Store pending payment
    pending_payments[str(call.message.chat.id)] = {
        "cat_id": cat_id,
        "pid": pid,
        "product": product
    }
    
    text = f"""💳 **PAYMENT PAGE**

📦 **Product:** {product['name']}
💰 **Amount:** ₹{product['price']}
📱 **bKash Number:** {product['bkash']}

**Instructions:**
1️⃣ Send ₹{product['price']} to {product['bkash']}
2️⃣ Send the **TRX ID** here
3️⃣ Send **Payment Screenshot**

⚠️ Send TRX ID first, then screenshot!"""

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❌ Cancel", callback_data="back_main"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=markup, parse_mode="Markdown")
    
    bot.send_message(call.message.chat.id, "💬 **Send your bKash TRX ID:**", parse_mode="Markdown")

# ================= HANDLE PAYMENT (TRX + SCREENSHOT) =================
@bot.message_handler(func=lambda m: str(m.chat.id) in pending_payments and m.text and not m.text.startswith('/'))
def handle_trx(message):
    pending = pending_payments[str(message.chat.id)]
    pending['trx'] = message.text
    pending_payments[str(message.chat.id)] = pending
    
    bot.reply_to(message, "✅ TRX ID saved!\n\n📸 **Now send the payment screenshot:**")
    
    # Set next step for screenshot
    bot.register_next_step_handler(message, handle_screenshot)

def handle_screenshot(message):
    if message.content_type != 'photo':
        bot.reply_to(message, "❌ Please send a **photo** screenshot!")
        bot.register_next_step_handler(message, handle_screenshot)
        return
    
    pending = pending_payments.get(str(message.chat.id))
    if not pending:
        return
    
    product = pending['product']
    
    # Send to admin
    admin_text = f"""🆕 **NEW ORDER!**

👤 **User:** {message.chat.id}
📛 **Name:** {message.from_user.first_name}
📦 **Product:** {product['name']}
💰 **Amount:** ₹{product['price']}
🔢 **TRX ID:** {pending['trx']}
⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{message.chat.id}_{pending['cat_id']}_{pending['pid']}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{message.chat.id}")
    )
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text, 
                   reply_markup=markup, parse_mode="Markdown")
    
    bot.send_message(message.chat.id, "✅ **Order sent to admin!**\nPlease wait for approval ⏳", parse_mode="Markdown")
    
    # Clean up
    del pending_payments[str(message.chat.id)]

# ================= APPROVE ORDER =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve_order(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ You are not admin!")
        return
    
    _, uid, cat_id, pid = call.data.split("_")
    uid = int(uid)
    
    product = products[cat_id]['items'].get(pid)
    
    if not product or product['stock'] <= 0:
        bot.send_message(ADMIN_ID, "❌ No stock available!")
        bot.answer_callback_query(call.id, "No stock!")
        return
    
    # Get key
    key = product['keys'].pop(0)
    product['stock'] -= 1
    
    # Send to user
    user_text = f"""✅ **PAYMENT APPROVED!** 🎉

📦 **Product:** {product['name']}
🔑 **Your Key:** `{key}`
🔗 **Download Link:** {product['link']}

📌 **Instructions:**
• Use the key to activate
• Contact support if any issue
• Thank you for your purchase! ❤️"""

    bot.send_message(uid, user_text, parse_mode="Markdown")
    
    # Save order history
    if str(uid) not in user_data:
        user_data[str(uid)] = {"orders": []}
    user_data[str(uid)]["orders"].append({
        "product": product['name'],
        "price": product['price'],
        "date": str(datetime.now()),
        "key": key
    })
    
    bot.send_message(ADMIN_ID, f"✅ Order approved for user {uid}\n📦 Remaining stock: {product['stock']}")
    bot.answer_callback_query(call.id, "✅ Approved!")

# ================= REJECT ORDER =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_order(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ You are not admin!")
        return
    
    uid = int(call.data.split("_")[1])
    
    bot.send_message(uid, "❌ **Payment Rejected!**\n\nPlease check your payment and try again.\nContact support: @WhiteXModz", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"❌ Order rejected for user {uid}")
    bot.answer_callback_query(call.id, "✅ Rejected!")

# ================= MY PROFILE =================
@bot.callback_query_handler(func=lambda call: call.data == "my_profile")
def my_profile(call):
    user = user_data.get(str(call.message.chat.id), {"balance": 0, "orders": [], "joined": str(datetime.now())})
    
    text = f"""👤 **MY PROFILE**

🆔 **User ID:** {call.message.chat.id}
💰 **Balance:** ₹{user.get('balance', 0)}
📦 **Total Orders:** {len(user.get('orders', []))}
👥 **Referrals:** {user.get('referrals', 0)}
📅 **Joined:** {user.get('joined', 'Unknown')}

Use /start to go back!"""
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=InlineKeyboardMarkup().add(
                                InlineKeyboardButton("🔙 Back", callback_data="back_main")
                            ), parse_mode="Markdown")

# ================= ORDER HISTORY =================
@bot.callback_query_handler(func=lambda call: call.data == "my_orders")
def my_orders(call):
    user = user_data.get(str(call.message.chat.id), {"orders": []})
    orders = user.get('orders', [])
    
    if not orders:
        text = "📭 **No orders yet!**\n\nStart shopping now!"
    else:
        text = "📜 **YOUR ORDER HISTORY**\n\n"
        for i, order in enumerate(orders[-10:], 1):
            text += f"{i}. 📦 {order['product']}\n   💰 ₹{order['price']}\n   📅 {order['date']}\n\n"
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=InlineKeyboardMarkup().add(
                                InlineKeyboardButton("🔙 Back", callback_data="back_main")
                            ), parse_mode="Markdown")

# ================= REFERRAL =================
@bot.callback_query_handler(func=lambda call: call.data == "referral")
def referral(call):
    text = f"""🔗 **REFERRAL PROGRAM**

Invite friends and earn money!

✨ **How it works:**
• Share your referral link
• Friend joins using your link
• You earn 10% of their first purchase

👥 **Your Referrals:** {user_data.get(str(call.message.chat.id), {}).get('referrals', 0)}

🔗 **Your Link:**
`https://t.me/{bot.get_me().username}?start=ref_{call.message.chat.id}`

Share this link with friends!"""
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=InlineKeyboardMarkup().add(
                                InlineKeyboardButton("🔙 Back", callback_data="back_main")
                            ), parse_mode="Markdown")

# ================= HOW TO USE =================
@bot.callback_query_handler(func=lambda call: call.data == "how_to_use")
def how_to_use(call):
    text = """📖 **HOW TO USE BOT**

1️⃣ **Buy Product:**
   • Click "Shop Store Now"
   • Select category & product
   • Click "Buy Now"

2️⃣ **Payment:**
   • Send money to given bKash number
   • Send TRX ID in chat
   • Send payment screenshot

3️⃣ **Get Product:**
   • Wait for admin approval
   • Receive key instantly
   • Enjoy your purchase!

📞 **Need Help?** Contact: @WhiteXModz"""
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=InlineKeyboardMarkup().add(
                                InlineKeyboardButton("🔙 Back", callback_data="back_main")
                            ), parse_mode="Markdown")

# ================= LUCKY GAME =================
@bot.callback_query_handler(func=lambda call: call.data == "lucky_game")
def lucky_game(call):
    import random
    prizes = ["₹50 Cash", "₹100 Cash", "Free Product", "10% Discount", "Try Again", "₹200 Cash"]
    prize = random.choice(prizes)
    
    text = f"🎲 **LUCKY SPIN** 🎲\n\nYou won: **{prize}**!\n\nContact admin to claim!"
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=InlineKeyboardMarkup().add(
                                InlineKeyboardButton("🎯 Spin Again", callback_data="lucky_game"),
                                InlineKeyboardButton("🔙 Back", callback_data="back_main")
                            ), parse_mode="Markdown")

# ================= ADD BALANCE =================
@bot.callback_query_handler(func=lambda call: call.data == "add_balance")
def add_balance(call):
    text = "💰 **ADD BALANCE**\n\nSend money to bKash: **01918591988**\n\nAfter payment, send screenshot to admin @WhiteXModz"
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id,
                            reply_markup=InlineKeyboardMarkup().add(
                                InlineKeyboardButton("🔙 Back", callback_data="back_main")
                            ), parse_mode="Markdown")

# ================= BACK TO MAIN =================
@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back_main(call):
    welcome_text = f"""✨ **WELCOME BACK!** ✨

Hello, {call.from_user.first_name}!

Choose an option from below:"""
    
    bot.edit_message_caption(welcome_text, call.message.chat.id, call.message.message_id,
                            reply_markup=main_menu(), parse_mode="Markdown")

# ================= ADMIN COMMANDS =================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        return
    
    text = """👑 **ADMIN PANEL**

📊 **Commands:**

`/addproduct cat_id|id|name|price|bkash|link|desc`
`/addkey cat_id|id|KEY`
`/stock cat_id|id|stock`
`/stats`
`/broadcast message`

**Example:**
`/addproduct mods|9|New Mod|499|019xxx|https://link.com|Cool mod`"""

    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['addproduct'])
def add_product(message):
    if message.chat.id != ADMIN_ID:
        return
    
    try:
        _, data = message.text.split(" ", 1)
        cat_id, pid, name, price, bkash, link, desc = data.split("|")
        
        if cat_id not in products:
            products[cat_id] = {"name": "New Category", "icon": "📦", "items": {}}
        
        products[cat_id]['items'][pid] = {
            "name": name,
            "price": price,
            "stock": 0,
            "bkash": bkash,
            "keys": [],
            "link": link,
            "desc": desc
        }
        
        bot.reply_to(message, f"✅ Product added: {name}")
    except:
        bot.reply_to(message, "❌ /addproduct cat_id|id|name|price|bkash|link|desc")

@bot.message_handler(commands=['addkey'])
def add_key(message):
    if message.chat.id != ADMIN_ID:
        return
    
    try:
        _, data = message.text.split(" ", 1)
        cat_id, pid, key = data.split("|")
        
        products[cat_id]['items'][pid]['keys'].append(key)
        products[cat_id]['items'][pid]['stock'] += 1
        
        bot.reply_to(message, f"✅ Key added! Total stock: {products[cat_id]['items'][pid]['stock']}")
    except:
        bot.reply_to(message, "❌ /addkey cat_id|product_id|KEY")

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id != ADMIN_ID:
        return
    
    total_users = len(user_data)
    total_orders = sum(len(u.get('orders', [])) for u in user_data.values())
    
    text = f"""📊 **BOT STATISTICS**

👥 Total Users: {total_users}
📦 Total Orders: {total_orders}
💰 Total Revenue: Calculating..."""

    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.chat.id != ADMIN_ID:
        return
    
    msg = message.text.replace("/broadcast ", "")
    count = 0
    
    for uid in user_data.keys():
        try:
            bot.send_message(int(uid), f"📢 **ANNOUNCEMENT**\n\n{msg}", parse_mode="Markdown")
            count += 1
            time.sleep(0.1)
        except:
            pass
    
    bot.reply_to(message, f"✅ Broadcast sent to {count} users!")

# ================= RUN BOT =================
if __name__ == "__main__":
    print("=" * 50)
    print("🔥 ANTO X MODZ STORE BOT STARTED!")
    print(f"🤖 Bot: @{bot.get_me().username}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("=" * 50)
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
