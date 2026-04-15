import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import json
import random
import string
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
BKASH_NUMBER = "01918591988"
LOGO_URL = "https://i.postimg.cc/Cxk8NxV2/istockphoto-827351040-1024x1024.jpg"

bot = telebot.TeleBot(TOKEN)

# ====================== ডাটাবেজ ======================
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

# ====================== প্রোডাক্ট ======================
if not products_db:
    products_db = {
        "1": {
            "name": "🎮 Reaper X Pro (Root)",
            "price": 349,
            "desc": "✨ ১০ দিন এক্সেস\n✅ রুট রিকোয়ার্ড\n✅ আনলক অল ফিচার",
            "stock": 10,
            "keys": ["REAPER-001", "REAPER-002"]
        },
        "2": {
            "name": "📱 Netflix Premium",
            "price": 299,
            "desc": "✨ ৩০ দিন এক্সেস\n✅ ৪কে কোয়ালিটি\n✅ পার্সোনাল অ্যাকাউন্ট",
            "stock": 15,
            "keys": ["NETFLIX-001", "NETFLIX-002"]
        }
    }
    save_db('products.json', products_db)

# ====================== মেনু ======================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛍️ শপ করুন", callback_data="shop"),
        InlineKeyboardButton("🔑 কী চেক", callback_data="check_key"),
        InlineKeyboardButton("📞 সাপোর্ট", url="https://t.me/PAPAJI_ANTO")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    if user_id not in users_db:
        users_db[user_id] = {"name": message.from_user.first_name, "orders": []}
        save_db('users.json', users_db)
    
    welcome = f"""✨ **ANTO SHOP এ স্বাগতম** ✨

💝 হ্যালো {message.from_user.first_name}!

✅ ইন্সট্যান্ট ডেলিভারি
✅ ১০০% সিকিওর
✅ ২৪/৭ সাপোর্ট

📌 নিচের বাটন থেকে সিলেক্ট করুন"""
    
    bot.send_photo(message.chat.id, LOGO_URL, caption=welcome, reply_markup=main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "shop")
def shop(call):
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, product in products_db.items():
        stock_icon = "🟢" if product['stock'] > 0 else "🔴"
        markup.add(InlineKeyboardButton(f"{stock_icon} {product['name']} - ৳{product['price']}", callback_data=f"buy_{pid}"))
    markup.add(InlineKeyboardButton("🏠 হোম", callback_data="home"))
    
    bot.edit_message_caption("🛍️ **প্রোডাক্ট সিলেক্ট করুন**", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== পেমেন্ট সিস্টেম ======================
pending = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy(call):
    pid = call.data.replace("buy_", "")
    product = products_db.get(pid)
    
    if not product or product['stock'] <= 0:
        bot.answer_callback_query(call.id, "❌ স্টক শেষ!")
        return
    
    pending[str(call.message.chat.id)] = {"pid": pid, "product": product}
    
    text = f"""💳 **পেমেন্ট পেজ**

📦 {product['name']}
💰 ৳{product['price']}
📱 bKash: `{BKASH_NUMBER}`

**পেমেন্ট করার পর:**
1️⃣ TRX আইডি পাঠান
2️⃣ স্ক্রিনশট পাঠান"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ TRX পাঠিয়েছি", callback_data="send_trx"))
    markup.add(InlineKeyboardButton("❌ বাতিল", callback_data="home"))
    
    bot.edit_message_caption(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "send_trx")
def send_trx(call):
    bot.send_message(call.message.chat.id, "📝 **আপনার bKash TRX আইডি লিখুন:**")
    bot.register_next_step_handler(call.message, process_trx)

def process_trx(message):
    if message.text.startswith('/'):
        return
    pending[str(message.chat.id)]['trx'] = message.text
    bot.reply_to(message, "✅ TRX সংরক্ষিত!\n\n📸 এখন পেমেন্টের স্ক্রিনশট পাঠান:")
    bot.register_next_step_handler(message, process_screenshot)

def process_screenshot(message):
    if message.content_type != 'photo':
        bot.reply_to(message, "❌ দয়া করে স্ক্রিনশট পাঠান!")
        bot.register_next_step_handler(message, process_screenshot)
        return
    
    pending_data = pending.get(str(message.chat.id))
    if not pending_data:
        return
    
    product = pending_data['product']
    
    admin_text = f"""🆕 **নতুন অর্ডার!**

👤 **ইউজার আইডি:** `{message.chat.id}`
📦 **প্রোডাক্ট:** {product['name']}
💰 **টাকা:** ৳{product['price']}
🔢 **TRX আইডি:** `{pending_data['trx']}`"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ অ্যাপ্রুভ", callback_data=f"approve_{message.chat.id}_{pending_data['pid']}"),
        InlineKeyboardButton("❌ রিজেক্ট", callback_data=f"reject_{message.chat.id}")
    )
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(message.chat.id, "✅ **অর্ডার অ্যাডমিনের কাছে পাঠানো হয়েছে!**\nঅ্যাপ্রুভের জন্য অপেক্ষা করুন ⏳", parse_mode="Markdown")
    
    del pending[str(message.chat.id)]

# ====================== অ্যাপ্রুভ সিস্টেম ======================
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
    save_db('products.json', products_db)
    
    user_text = f"""✅ **পেমেন্ট অ্যাপ্রুভ করা হয়েছে!** 🎉

📦 **প্রোডাক্ট:** {product['name']}
🔑 **আপনার কী:** `{key}`

💝 কেনাকাটার জন্য ধন্যবাদ!"""
    
    bot.send_message(uid, user_text, parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"✅ অর্ডার অ্যাপ্রুভ করা হয়েছে!\n📦 বাকি স্টক: {product['stock']}")
    bot.answer_callback_query(call.id, "✅ অ্যাপ্রুভ করা হয়েছে!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_order(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ তুমি অ্যাডমিন নও!")
        return
    
    uid = int(call.data.split("_")[1])
    bot.send_message(uid, "❌ **পেমেন্ট রিজেক্ট করা হয়েছে!**\nদয়া করে সঠিক তথ্য দিয়ে আবার চেষ্টা করুন।", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"❌
