from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import json
import random
import time
from datetime import datetime, timedelta
import threading

# Flask app for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Bot code
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
BKASH_NUMBER = "01918591988"
LOGO_URL = "https://i.postimg.cc/Cxk8NxV2/istockphoto-827351040-1024x1024.jpg"

bot = telebot.TeleBot(TOKEN)

# Database
def load_db(f):
    try:
        with open(f, 'r') as file:
            return json.load(file)
    except:
        return {}

def save_db(f, data):
    with open(f, 'w') as file:
        json.dump(data, file, indent=4)

users_db = load_db('users.json')
wallet_db = load_db('wallet.json')

# Products
products = {
    "1": {"name": "🔥 DRIP CLINT", "price": 400, "keys": ["DRIP-001"], "stock": 5},
    "2": {"name": "🎮 BGMI ESP", "price": 299, "keys": ["BGMI-001"], "stock": 3}
}

# Wallet functions
def get_balance(uid):
    uid = str(uid)
    if uid not in wallet_db:
        wallet_db[uid] = {"balance": 0}
        save_db('wallet.json', wallet_db)
    return wallet_db[uid]["balance"]

def add_balance(uid, amount):
    uid = str(uid)
    if uid not in wallet_db:
        wallet_db[uid] = {"balance": 0}
    wallet_db[uid]["balance"] += amount
    save_db('wallet.json', wallet_db)

def deduct_balance(uid, amount):
    uid = str(uid)
    if get_balance(uid) >= amount:
        wallet_db[uid]["balance"] -= amount
        save_db('wallet.json', wallet_db)
        return True
    return False

# Main menu
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛍️ SHOP", callback_data="shop"),
        InlineKeyboardButton("💰 WALLET", callback_data="wallet")
    )
    markup.add(
        InlineKeyboardButton("🎲 SPIN", callback_data="spin"),
        InlineKeyboardButton("📞 SUPPORT", url="https://t.me/PAPAJI_ANTO")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.chat.id)
    if uid not in users_db:
        users_db[uid] = {"name": m.from_user.first_name, "joined": str(datetime.now())}
        save_db('users.json', users_db)
    
    bal = get_balance(m.chat.id)
    bot.send_photo(m.chat.id, LOGO_URL, 
                   caption=f"✨ ANTO SHOP\nHello {m.from_user.first_name}!\n💰 Balance: ৳{bal}", 
                   reply_markup=main_menu())

# Shop
@bot.callback_query_handler(func=lambda c: c.data == "shop")
def shop(c):
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, p in products.items():
        markup.add(InlineKeyboardButton(f"{p['name']} - ৳{p['price']}", callback_data=f"buy_{pid}"))
    markup.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    bot.edit_message_caption("🛍️ SELECT PRODUCT:", c.message.chat.id, c.message.message_id, reply_markup=markup)

# Buy
pending = {}
@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p or p['stock'] <= 0:
        bot.answer_callback_query(c.id, "Out of stock!")
        return
    
    pending[str(c.message.chat.id)] = {"pid": pid, "product": p, "amount": p['price']}
    bal = get_balance(c.message.chat.id)
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("💳 PAY", callback_data="pay_wallet"),
        InlineKeyboardButton("❌ CANCEL", callback_data="home")
    )
    bot.edit_message_caption(f"💳 PAYMENT\n{p['name']} - ৳{p['price']}\nYour Balance: ৳{bal}", 
                            c.message.chat.id, c.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "pay_wallet")
def pay(c):
    uid = str(c.message.chat.id)
    pend = pending.get(uid)
    if not pend:
        bot.answer_callback_query(c.id, "Try again!")
        return
    
    if deduct_balance(int(uid), pend['amount']):
        key = pend['product']['keys'].pop(0)
        pend['product']['stock'] -= 1
        
        bot.edit_message_caption(f"✅ SUCCESS!\n🔑 Key: {key}\nNew Balance: ৳{get_balance(uid)}", 
                                c.message.chat.id, c.message.message_id,
                                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home")))
        del pending[uid]
    else:
        bot.answer_callback_query(c.id, "Insufficient balance!")

# Wallet
@bot.callback_query_handler(func=lambda c: c.data == "wallet")
def wallet(c):
    bal = get_balance(c.message.chat.id)
    bot.edit_message_caption(f"💰 BALANCE: ৳{bal}", c.message.chat.id, c.message.message_id,
                            reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home")))

# Spin
spin_cd = {}
@bot.callback_query_handler(func=lambda c: c.data == "spin")
def spin(c):
    uid = str(c.message.chat.id)
    if uid in spin_cd:
        last = datetime.fromisoformat(spin_cd[uid])
        if datetime.now() - last < timedelta(hours=24):
            bot.answer_callback_query(c.id, "Come back tomorrow!")
            return
    
    prize = random.choice([5,10,20,50,0,0,5])
    if prize > 0:
        add_balance(uid, prize)
        text = f"🎉 You won ৳{prize}!"
    else:
        text = "😢 Better luck next time!"
    
    spin_cd[uid] = str(datetime.now())
    bot.edit_message_caption(text, c.message.chat.id, c.message.message_id,
                            reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home")))

# Home
@bot.callback_query_handler(func=lambda c: c.data == "home")
def home(c):
    bal = get_balance(c.message.chat.id)
    bot.edit_message_caption(f"✨ Welcome back!\n💰 Balance: ৳{bal}", 
                            c.message.chat.id, c.message.message_id, reply_markup=main_menu())

# Admin
@bot.message_handler(commands=['addbalance'])
def add_bal(m):
    if m.chat.id != ADMIN_ID:
        return
    try:
        _, uid, amt = m.text.split()
        add_balance(int(uid), int(amt))
        bot.reply_to(m, f"✅ Added ৳{amt} to {uid}")
    except:
        bot.reply_to(m, "❌ /addbalance USER_ID AMOUNT")

# Run both Flask and Bot
def run_bot():
    bot.infinity_polling(timeout=60)

if __name__ == "__main__":
    # Start bot in background
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
