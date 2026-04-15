import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os, json, random, string, time, hashlib
from datetime import datetime, timedelta

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
BKASH_NUMBER = "01918591988"
NAGAD_NUMBER = "01918591988"  # নগদ নম্বর
LOGO_URL = "https://i.postimg.cc/Cxk8NxV2/istockphoto-827351040-1024x1024.jpg"

bot = telebot.TeleBot(TOKEN)

# ================= DATABASE =================
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
coupons = load_db('coupons.json')
withdraws = load_db('withdraws.json')

# ================= PRODUCTS =================
if not products:
    products = {
        "1": {"name": "🔥 DRIP CLINT", "price": 400, "keys": ["DRIP-001"], "stock": 10, "durations": {"7d": 400, "10d": 550, "30d": 1500}},
        "2": {"name": "🎮 BGMI ESP", "price": 299, "keys": ["BGMI-001"], "stock": 8, "durations": {"7d": 299, "15d": 499, "30d": 899}}
    }
    save_db('products.json', products)

# ================= WALLET =================
def get_bal(uid):
    uid = str(uid)
    if uid not in wallet:
        wallet[uid] = {"balance": 0, "transactions": []}
        save_db('wallet.json', wallet)
    return wallet[uid]["balance"]

def add_bal(uid, amt, reason=""):
    uid = str(uid)
    if uid not in wallet:
        wallet[uid] = {"balance": 0, "transactions": []}
    wallet[uid]["balance"] += amt
    wallet[uid]["transactions"].append({"type": "add", "amount": amt, "reason": reason, "date": str(datetime.now())})
    save_db('wallet.json', wallet)

def deduct_bal(uid, amt, reason=""):
    uid = str(uid)
    if get_bal(uid) >= amt:
        wallet[uid]["balance"] -= amt
        wallet[uid]["transactions"].append({"type": "deduct", "amount": amt, "reason": reason, "date": str(datetime.now())})
        save_db('wallet.json', wallet)
        return True
    return False

# ================= MAIN MENU =================
def main_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(InlineKeyboardButton("🛍️ SHOP", callback_data="shop"), InlineKeyboardButton("👤 PROFILE", callback_data="profile"))
    m.add(InlineKeyboardButton("💰 WALLET", callback_data="wallet"), InlineKeyboardButton("➕ ADD BALANCE", callback_data="add_balance"))
    m.add(InlineKeyboardButton("📦 ORDERS", callback_data="orders"), InlineKeyboardButton("🔑 CHECK KEY", callback_data="check_key"))
    m.add(InlineKeyboardButton("🔗 REFERRAL", callback_data="referral"), InlineKeyboardButton("🎁 DAILY", callback_data="daily"))
    m.add(InlineKeyboardButton("🎲 SPIN", callback_data="spin"), InlineKeyboardButton("💸 WITHDRAW", callback_data="withdraw"))
    m.add(InlineKeyboardButton("🎟️ COUPON", callback_data="coupon"), InlineKeyboardButton("📞 SUPPORT", url="https://t.me/PAPAJI_ANTO"))
    return m

@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.chat.id)
    if uid not in users:
        users[uid] = {"name": m.from_user.first_name, "joined": str(datetime.now()), "referrals": 0, "orders": []}
        save_db('users.json', users)
        add_bal(uid, 50, "signup_bonus")
    
    bal = get_bal(uid)
    bot.send_photo(m.chat.id, LOGO_URL, caption=f"✨ ANTO SHOP\nHello {m.from_user.first_name}!\n💰 Balance: ৳{bal}", reply_markup=main_menu())

# ================= SHOP =================
@bot.callback_query_handler(func=lambda c: c.data == "shop")
def shop(c):
    m = InlineKeyboardMarkup(row_width=1)
    for pid, p in products.items():
        m.add(InlineKeyboardButton(f"{p['name']} - ৳{p['price']}", callback_data=f"prod_{pid}"))
    m.add(InlineKeyboardButton("🏠 HOME", callback_data="home"))
    bot.edit_message_caption("🛍️ SELECT PRODUCT:", c.message.chat.id, c.message.message_id, reply_markup=m)

@bot.callback_query_handler(func=lambda c: c.data.startswith("prod_"))
def prod_detail(c):
    pid = c.data.split("_")[1]
    p = products.get(pid)
    if not p:
        return
    m = InlineKeyboardMarkup(row_width=2)
    for dur, price in p['durations'].items():
        m.add(InlineKeyboardButton(f"📅 {dur} - ৳{price}", callback_data=f"dur_{pid}_{dur}_{price}"))
    m.add(InlineKeyboardButton("🔙 BACK", callback_data="shop"))
    bot.edit_message_caption(f"📦 {p['name']}\n{p.get('desc', 'Premium Product')}\n\nSelect duration:", c.message.chat.id, c.message.message_id, reply_markup=m)

# ================= BUY =================
pending = {}
@bot.callback_query_handler(func=lambda c: c.data.startswith("dur_"))
def buy(c):
    _, pid, dur, price = c.data.split("_")
    p = products.get(pid)
    if not p or p['stock'] <= 0:
        bot.answer_callback_query(c.id, "Out of stock!")
        return
    pending[str(c.message.chat.id)] = {"pid": pid, "dur": dur, "price": int(price), "product": p}
    bal = get_bal(c.message.chat.id)
    m = InlineKeyboardMarkup(row_width=2)
    m.add(InlineKeyboardButton("💳 WALLET", callback_data="pay_wallet"), InlineKeyboardButton("📱 BKASH", callback_data="pay_bkash"))
    m.add(InlineKeyboardButton("🟢 NAGAD", callback_data="pay_nagad"), InlineKeyboardButton("❌ CANCEL", callback_data="home"))
    bot.edit_message_caption(f"💳 PAYMENT\n{p['name']}\n📅 {dur}\n💰 ৳{price}\n💵 Balance: ৳{bal}", c.message.chat.id, c.message.message_id, reply_markup=m)

# ================= WALLET PAYMENT =================
@bot.callback_query_handler(func=lambda c: c.data == "pay_wallet")
def pay_wallet(c):
    uid = str(c.message.chat.id)
    pend = pending.get(uid)
    if not pend:
        return
    if deduct_bal(uid, pend['price'], "purchase"):
        key = pend['product']['keys'].pop(0)
        pend['product']['stock'] -= 1
        save_db('products.json', products)
        users[uid]['orders'].append({"product": pend['product']['name'], "duration": pend['dur'], "price": pend['price'], "key": key, "date": str(datetime.now())})
        save_db('users.json', users)
        bot.edit_message_caption(f"✅ PURCHASE SUCCESSFUL!\n🔑 Key: `{key}`", c.message.chat.id, c.message.message_id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home")), parse_mode="Markdown")
        del pending[uid]
    else:
        bot.answer_callback_query(c.id, "Insufficient balance!")

# ================= BKASH/NAGAD PAYMENT =================
payment_pending = {}
@bot.callback_query_handler(func=lambda c: c.data in ["pay_bkash", "pay_nagad"])
def manual_pay(c):
    uid = str(c.message.chat.id)
    pend = pending.get(uid)
    if not pend:
        return
    method = "bKash" if c.data == "pay_bkash" else "Nagad"
    number = BKASH_NUMBER if c.data == "pay_bkash" else NAGAD_NUMBER
    ref = f"ANTO{random.randint(10000, 99999)}"
    payment_pending[uid] = {"pending": pend, "method": method, "ref": ref}
    bot.edit_message_caption(f"💳 {method} PAYMENT\n📦 {pend['product']['name']}\n💰 ৳{pend['price']}\n📱 {method}: {number}\n🔖 Ref: {ref}\n\nSend TRX ID after payment:", c.message.chat.id, c.message.message_id)
    bot.register_next_step_handler(c.message, process_trx)

def process_trx(m):
    if m.text.startswith('/'):
        return
    uid = str(m.chat.id)
    if uid in payment_pending:
        payment_pending[uid]['trx'] = m.text
        bot.reply_to(m, "✅ TRX Saved! Now send screenshot:")
        bot.register_next_step_handler(m, process_ss)

def process_ss(m):
    if m.content_type != 'photo':
        bot.reply_to(m, "Send screenshot!")
        bot.register_next_step_handler(m, process_ss)
        return
    uid = str(m.chat.id)
    pp = payment_pending.get(uid)
    if not pp:
        return
    pend = pp['pending']
    admin_txt = f"🆕 NEW ORDER ({pp['method']})\n👤 {m.chat.id}\n📦 {pend['product']['name']}\n💰 ৳{pend['price']}\n🔢 {pp['trx']}"
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("✅ APPROVE", callback_data=f"app_{uid}_{pend['pid']}"), InlineKeyboardButton("❌ REJECT", callback_data=f"rej_{uid}"))
    bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=admin_txt, reply_markup=markup)
    bot.send_message(m.chat.id, "✅ Order sent to admin!")
    del payment_pending[uid]

# ================= APPROVE =================
@bot.callback_query_handler(func=lambda c: c.data.startswith("app_"))
def approve(c):
    if c.from_user.id != ADMIN_ID:
        return
    _, uid, pid = c.data.split("_")
    p = products.get(pid)
    if not p or len(p['keys']) == 0:
        bot.send_message(ADMIN_ID, "No keys!")
        return
    key = p['keys'].pop(0)
    p['stock'] -= 1
    save_db('products.json', products)
    users[uid]['orders'].append({"product": p['name'], "price": p['price'], "key": key, "date": str(datetime.now())})
    save_db('users.json', users)
    bot.send_message(int(uid), f"✅ APPROVED!\n🔑 Key: {key}")
    bot.answer_callback_query(c.id, "Approved!")

@bot.callback_query_handler(func=lambda c: c.data.startswith("rej_"))
def reject(c):
    if c.from_user.id != ADMIN_ID:
        return
    uid = c.data.split("_")[1]
    bot.send_message(int(uid), "❌ REJECTED!")
    bot.answer_callback_query(c.id, "Rejected!")

# ================= DAILY BONUS =================
daily_cd = {}
@bot.callback_query_handler(func=lambda c: c.data == "daily")
def daily(c):
    uid = str(c.message.chat.id)
    if uid in daily_cd:
        last = datetime.fromisoformat(daily_cd[uid])
        if datetime.now() - last < timedelta(hours=24):
            rem = timedelta(hours=24) - (datetime.now() - last)
            bot.answer_callback_query(c.id, f"Come back in {rem.seconds//3600}h {rem.seconds%3600//60}m!")
            return
    amount = random.randint(10, 50)
    add_bal(uid, amount, "daily_bonus")
    daily_cd[uid] = str(datetime.now())
    bot.answer_callback_query(c.id, f"🎁 You got ৳{amount} daily bonus!")

# ================= LUCKY SPIN =================
spin_cd = {}
@bot.callback_query_handler(func=lambda c: c.data == "spin")
def spin(c):
    uid = str(c.message.chat.id)
    if uid in spin_cd:
        last = datetime.fromisoformat(spin_cd[uid])
        if datetime.now() - last < timedelta(hours=24):
            bot.answer_callback_query(c.id, "Come back tomorrow!")
            return
    prizes = [5, 10, 20, 50, 100, 0, 0, 5, 10, 20, 0]
    prize = random.choice(prizes)
    if prize > 0:
        add_bal(uid, prize, "lucky_spin")
        bot.answer_callback_query(c.id, f"🎉 You won ৳{prize}!")
    else:
        bot.answer_callback_query(c.id, "😢 Better luck next time!")
    spin_cd[uid] = str(datetime.now())

# ================= CHECK KEY =================
@bot.callback_query_handler(func=lambda c: c.data == "check_key")
def check_key_menu(c):
    bot.send_message(c.message.chat.id, "🔑 Enter your key:")
    bot.register_next_step_handler(c.message, check_key_proc)

def check_key_proc(m):
    key = m.text.strip().upper()
    for pid, p in products.items():
        if key in p['keys']:
            bot.reply_to(m, f"✅ VALID KEY!\n📦 {p['name']}")
            return
    bot.reply_to(m, "❌ INVALID KEY!")

# ================= PROFILE =================
@bot.callback_query_handler(func=lambda c: c.data == "profile")
def profile(c):
    u = users.get(str(c.message.chat.id), {})
    bal = get_bal(c.message.chat.id)
    bot.edit_message_caption(f"👤 PROFILE\n🆔 {c.message.chat.id}\n👤 {u.get('name')}\n💰 ৳{bal}\n📦 Orders: {len(u.get('orders', []))}\n👥 Referrals: {u.get('referrals', 0)}", c.message.chat.id, c.message.message_id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home")))

# ================= WALLET VIEW =================
@bot.callback_query_handler(func=lambda c: c.data == "wallet")
def wallet_view(c):
    bal = get_bal(c.message.chat.id)
    bot.edit_message_caption(f"💰 WALLET\nBalance: ৳{bal}", c.message.chat.id, c.message.message_id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home")))

# ================= ADD BALANCE =================
@bot.callback_query_handler(func=lambda c: c.data == "add_balance")
def add_bal_menu(c):
    bot.send_message(c.message.chat.id, "💰 ADD BALANCE\nSend: `500 8Y7X9K2M4N`\nMin: ৳100", parse_mode="Markdown")
    bot.register_next_step_handler(c.message, add_bal_proc)

def add_bal_proc(m):
    try:
        amt, trx = m.text.split()
        amt = int(amt)
        admin_txt = f"💰 BALANCE REQUEST\n👤 {m.chat.id}\n💰 ৳{amt}\n🔢 {trx}"
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("✅ APPROVE", callback_data=f"addbal_{m.chat.id}_{amt}"), InlineKeyboardButton("❌ REJECT", callback_data=f"rej_{m.chat.id}"))
        bot.send_message(ADMIN_ID, admin_txt, reply_markup=markup)
        bot.reply_to(m, "Request sent to admin!")
    except:
        bot.reply_to(m, "❌ Use: 500 8Y7X9K2M4N")

@bot.callback_query_handler(func=lambda c: c.data.startswith("addbal_"))
def approve_bal(c):
    if c.from_user.id != ADMIN_ID:
        return
    _, uid, amt = c.data.split("_")
    add_bal(int(uid), int(amt), "admin_add")
    bot.send_message(int(uid), f"✅ ৳{amt} added to wallet!")
    bot.answer_callback_query(c.id, "Added!")

# ================= REFERRAL =================
@bot.callback_query_handler(func=lambda c: c.data == "referral")
def referral(c):
    uname = bot.get_me().username
    bot.edit_message_caption(f"🔗 REFERRAL\nLink: `https://t.me/{uname}?start=ref_{c.message.chat.id}`\nEarn 10% commission!", c.message.chat.id, c.message.message_id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("📤 SHARE", url=f"https://t.me/share/url?url=https://t.me/{uname}?start=ref_{c.message.chat.id}"), InlineKeyboardButton("🏠 HOME", callback_data="home")), parse_mode="Markdown")

# ================= ORDERS =================
@bot.callback_query_handler(func=lambda c: c.data == "orders")
def orders(c):
    u = users.get(str(c.message.chat.id), {})
    ords = u.get('orders', [])
    if not ords:
        txt = "📭 No orders yet!"
    else:
        txt = "📦 YOUR ORDERS:\n\n"
        for o in ords[-5:]:
            txt += f"📦 {o['product']}\n💰 ৳{o['price']}\n🔑 `{o['key']}`\n📅 {o['date'][:10]}\n\n"
    bot.edit_message_caption(txt, c.message.chat.id, c.message.message_id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 HOME", callback_data="home")), parse_mode="Markdown")

# ================= COUPON =================
@bot.callback_query_handler(func=lambda c: c.data == "coupon")
def coupon_menu(c):
    bot.send_message(c.message.chat.id, "🎟️ Enter coupon code:")
    bot.register_next_step_handler(c.message, use_coupon)

def use_coupon(m):
    code = m.text.strip().upper()
    if code in coupons:
        cp = coupons[code]
        if cp.get('used'):
            bot.reply_to(m, "❌ Coupon already used!")
        elif datetime.now() > datetime.fromisoformat(cp['expiry']):
            bot.reply_to(m, "❌ Coupon expired!")
        else:
            add_bal(m.chat.id, cp['amount'], f"coupon_{code}")
            coupons[code]['used'] = True
            save_db('coupons.json', coupons)
            bot.reply_to(m, f"✅ Coupon applied! +৳{cp['amount']}")
    else:
        bot.reply_to(m, "❌ Invalid coupon!")

# ================= WITHDRAW =================
@bot.callback_query_handler(func=lambda c: c.data == "withdraw")
def withdraw_menu(c):
    bot.send_message(c.message.chat.id, "💸 WITHDRAW\nSend: `500 BKASH_NUMBER`\nMin: ৳200", parse_mode="Markdown")
    bot.register_next_step_handler(c.message, withdraw_proc)

def withdraw_proc(m):
    try:
        amt, method = m.text.split()
        amt = int(amt)
        if get_bal(m.chat.id) >= amt:
            deduct_bal(m.chat.id, amt, "withdraw_request")
            withdraws[str(m.chat.id)] = {"amount": amt, "method": method, "status": "pending", "date": str(datetime.now())}
            save_db('withdraws.json', withdraws)
            admin_txt = f"💸 WITHDRAW REQUEST\n👤 {m.chat.id}\n💰 ৳{amt}\n📱 {method}"
            markup = InlineKeyboardMarkup().add(InlineKeyboardButton("✅ PAY", callback_data=f"pay_{m.chat.id}_{amt}"), InlineKeyboardButton("❌ REJECT", callback_data=f"rej_{m.chat.id}"))
            bot.send_message(ADMIN_ID, admin_txt, reply_markup=markup)
            bot.reply_to(m, "Withdraw request sent to admin!")
        else:
            bot.reply_to(m, "❌ Insufficient balance!")
    except:
        bot.reply_to(m, "❌ Use: 500 019XXXXXXXX")

@bot.callback_query_handler(func=lambda c: c.data.startswith("pay_"))
def pay_withdraw(c):
    if c.from_user.id != ADMIN_ID:
        return
    _, uid, amt = c.data.split("_")
    bot.send_message(int(uid), f"✅ Withdraw ৳{amt} approved! Sent to your number.")
    bot.answer_callback_query(c.id, "Paid!")

# ================= ADMIN =================
@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.chat.id != ADMIN_ID:
        return
    bot.reply_to(m, "/addkey PID|KEY\n/addbalance UID AMOUNT\n/addcoupon CODE AMOUNT\n/products\n/users\n/stats\n/broadcast MSG\n/setbkash NUMBER\n/setnagad NUMBER")

@bot.message_handler(commands=['addkey'])
def addkey(m):
    if m.chat.id != ADMIN_ID:
        return
    try:
        _, pid, key = m.text.split("|")
        products[pid]['keys'].append(key.upper())
        products[pid]['stock'] += 1
        save_db('products.json', products)
        bot.reply_to(m, f"✅ Key added: {key}")
    except:
        bot.reply_to(m, "❌ /addkey PID|KEY")

@bot.message_handler(commands=['addbalance'])
def addbal_admin(m):
    if m.chat.id != ADMIN_ID:
        return
    try:
        _, uid, amt = m.text.split()
        add_bal(int(uid), int(amt), "admin_add")
        bot.send_message(int(uid), f"💰 ৳{amt} added by admin!")
        bot.reply_to(m, f"✅ Added ৳{amt} to {uid}")
    except:
        bot.reply_to(m, "❌ /addbalance UID AMOUNT")

@bot.message_handler(commands=['addcoupon'])
def add_coupon(m):
    if m.chat.id != ADMIN_ID:
        return
    try:
        _, code, amt = m.text.split()
        coupons[code.upper()] = {"amount": int(amt), "used": False, "expiry": str(datetime.now() + timedelta(days=7))}
        save_db('coupons.json', coupons)
        bot.reply_to(m, f"✅ Coupon {code} added! ৳{amt}")
    except:
        bot.reply_to(m, "❌ /addcoupon CODE AMOUNT")

@bot.message_handler(commands=['products'])
def list_prod(m):
    if m.chat.id != ADMIN_ID:
        return
    txt = "📦 PRODUCTS:\n"
    for pid, p in products.items():
        txt += f"{pid}. {p['name']} | Stock: {p['stock']} | Keys: {len(p['keys'])}\n"
    bot.reply_to(m, txt)

@bot.message_handler(commands=['users'])
def list_users(m):
    if m.chat.id != ADMIN_ID:
        return
    txt = "👥 USERS:\n"
    for uid, u in list(users.items())[:30]:
        txt += f"{uid} | {u.get('name')} | Orders: {len(u.get('orders', []))}\n"
    bot.reply_to(m, txt)

@bot.message_handler(commands=['stats'])
def stats(m):
    if m.chat.id != ADMIN_ID:
        return
    total_bal = sum(w['balance'] for w in wallet.values())
    bot.reply_to(m, f"📊 STATS\n👥 Users: {len(users)}\n🔑 Keys: {sum(len(p['keys']) for p in products.values())}\n💰 Total Balance: ৳{total_bal}")

@bot.message_handler(commands=['broadcast'])
def broadcast(m):
    if m.chat.id != ADMIN_ID:
        return
    msg = m.text.replace("/broadcast ", "")
    c = 0
    for uid in users:
        try:
            bot.send_message(int(uid), f"📢 ANNOUNCEMENT\n\n{msg}")
            c += 1
            time.sleep(0.05)
        except:
            pass
    bot.reply_to(m, f"✅ Sent to {c} users")

@bot.message_handler(commands=['setbkash'])
def set_bkash(m):
    if m.chat.id != ADMIN_ID:
        return
    global BKASH_NUMBER
    BKASH_NUMBER = m.text.split()[1]
    bot.reply_to(m, f"✅ bKash set to {BKASH_NUMBER}")

@bot.message_handler(commands=['setnagad'])
def set_nagad(m):
    if m.chat.id != ADMIN_ID:
        return
    global NAGAD_NUMBER
    NAGAD_NUMBER = m.text.split()[1]
    bot.reply_to(m, f"✅ Nagad set to {NAGAD_NUMBER}")

# ================= HOME =================
@bot.callback_query_handler(func=lambda c: c.data == "home")
def home(c):
    bal = get_bal(c.message.chat.id)
    bot.edit_message_caption(f"✨ Welcome back!\n💰 Balance: ৳{bal}", c.message.chat.id, c.message.message_id, reply_markup=main_menu())

# ================= RUN =================
if __name__ == "__main__":
    print("🔥 ANTO SHOP ULTIMATE BOT STARTED!")
    print(f"🤖 Bot: @{bot.get_me().username}")
    print(f"👑 Admin: {ADMIN_ID}")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)
