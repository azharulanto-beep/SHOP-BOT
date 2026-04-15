import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import json
import time
import random
import string
import qrcode
from io import BytesIO
from datetime import datetime, timedelta

# ====================== তোর টোকেনগুলো এখানে বসাবি ======================
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
BKASH_NUMBER = "01918591988"  # তোর বিকাশ নম্বর দিবি

# ====================== তোর লোগো লিংক ======================
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
orders_db = load_db('orders.json')

# ====================== প্রোডাক্ট ডাটাবেজ ======================
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

# ====================== QR জেনারেটর (তোর স্ক্যানার) ======================
def generate_qr(amount, ref):
    payment_data = f"bkash://pay?amount={amount}&merchant={BKASH_NUMBER}&ref={ref}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(payment_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#E2136E", back_color="white")
    bio = BytesIO()
    bio.name = 'qr.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

# ====================== মেইন মেনু ======================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛍️ শপ করুন", callback_data="shop"),
        InlineKeyboardButton("🔑 কী চেক", callback_data="check_key"),
        InlineKeyboardButton("📞 সাপোর্ট", url="https://t.me/PAPAJI_ANTO")
    )
    return markup

# ====================== স্টার্ট ======================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    if user_id not in users_db:
        users_db[user_id] = {"name": message.from_user.first_name, "balance": 0, "orders": []}
        save_db('users.json', users_db)
    
    welcome = f"""✨ **ANTO SHOP এ স্বাগতম** ✨

💝 হ্যালো {message.from_user.first_name}!

✅ ইন্সট্যান্ট ডেলিভারি
✅ ১০০% সিকিওর
✅ ২৪/৭ সাপোর্ট

📌 নিচের বাটন থেকে সিলেক্ট করুন"""
    
    bot.send_photo(message.chat.id, LOGO_URL, caption=welcome, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== শপ ======================
@bot.callback_query_handler(func=lambda call: call.data == "shop")
def shop(call):
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, product in products_db.items():
        markup.add(InlineKeyboardButton(f"🟢 {product['name']} - ৳{product['price']}", callback_data=f"buy_{pid}"))
    markup.add(InlineKeyboardButton("🏠 হোম", callback_data="home"))
    
    bot.edit_message_caption("🛍️ **প্রোডাক্ট সিলেক্ট করুন**", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== কেনাকাটা ও পেমেন্ট ======================
pending = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy(call):
    pid = call.data.replace("buy_", "")
    product = products_db.get(pid)
    
    if not product or product['stock'] <= 0:
        bot.answer_callback_query(call.id, "❌ স্টক শেষ!")
        return
    
    ref = f"ANTO{random.randint(10000, 99999)}"
    pending[str(call.message.chat.id)] = {"pid": pid, "product": product, "ref": ref}
    
    qr_image = generate_qr(product['price'], ref)
    
    text = f"""💳 **পেমেন্ট পেজ**

📦 {product['name']}
💰 ৳{product['price']}
📱 bKash: {BKASH_NUMBER}
🔖 রেফ: `{ref}`

**নিচের QR স্ক্যান করে পেমেন্ট কর**"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ TRX পাঠিয়েছি", callback_data="send_trx"))
    markup.add(InlineKeyboardButton("❌ বাতিল", callback_data="home"))
    
    bot.send_photo(call.message.chat.id, qr_image, caption=text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "send_trx")
def send_trx(call):
    bot.send_message(call.message.chat.id, "📝 **TRX আইডি লিখুন:**")
    bot.register_next_step_handler(call.message, process_trx)

def process_trx(message):
    if message.text.startswith('/'):
        return
    pending[str(message.chat.id)]['trx'] = message.text
    bot.reply_to(message, "✅ TRX সংরক্ষিত! এখন স্ক্রিনশট পাঠান:")
    bot.register_next_step_handler(message, process_screenshot)

def process_screenshot(message):
    if message.content_type != 'photo':
        bot.reply_to(message, "❌ ফটো পাঠান!")
        bot.register_next_step_handler(message, process_screenshot)
        return
    
    pending_data = pending.get(str(message.chat.id))
    if not pending_data:
        return
    
    product = pending_data['product']
    
    # অ্যাডমিনকে নোটিফিকেশন
    admin_text = f"🆕 অর্ডার!\n\n👤 {message.chat.id}\n📦 {product['name']}\n💰 ৳{product['price']}\n🔢 {pending_data['trx']}"
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text)
    
    # ইউজারকে মেসেজ
    bot.send_message(message.chat.id, "✅ অর্ডার পাঠানো হয়েছে! অ্যাপ্রুভের জন্য অপেক্ষা করুন।")
    del pending[str(message.chat.id)]

# ====================== কী চেক ======================
@bot.callback_query_handler(func=lambda call: call.data == "check_key")
def check_key(call):
    bot.send_message(call.message.chat.id, "🔑 **আপনার কী লিখুন:**")
    bot.register_next_step_handler(call.message, process_key_check)

def process_key_check(message):
    key = message.text.strip().upper()
    found = False
    for pid, product in products_db.items():
        if key in product['keys']:
            found = True
            bot.reply_to(message, f"✅ **ভ্যালিড কী!**\n📦 {product['name']}\n💝 ইউজ করতে পারবেন।")
            break
    if not found:
        bot.reply_to(message, "❌ **ইনভ্যালিড কী!**")

# ====================== অ্যাডমিন প্যানেল ======================
@bot.message_handler(commands=['approve'])
def approve(message):
    if message.chat.id != ADMIN_ID:
        return
    # এখানে তোর অর্ডার অ্যাপ্রুভ করার সিস্টেম বসাতে পারিস
    bot.reply_to(message, "✅ অর্ডার অ্যাপ্রুভ করা হয়েছে!")

# ====================== হোম ======================
@bot.callback_query_handler(func=lambda call: call.data == "home")
def home(call):
    bot.edit_message_caption(f"✨ হ্যালো {call.from_user.first_name}!", call.message.chat.id, call.message.message_id, reply_markup=main_menu(), parse_mode="Markdown")

# ====================== রান ======================
if __name__ == "__main__":
    print("🔥 ANTO SHOP RUNNING...")
    print(f"🤖 Bot: @{bot.get_me().username}")
    print(f"👑 Admin: {ADMIN_ID}")
    print(f"🖼️ Logo: {LOGO_URL}")
    bot.infinity_polling()
