#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║     ANTO DEV — MEGA TELEGRAM SHOP BOT (Python Polling)         ║
║     aiogram 3.x | SQLite | RupantorPay | No Webhook Needed     ║
║     Deploy anywhere — Railway, VPS, Replit, Local              ║
╚══════════════════════════════════════════════════════════════════╝
pip install aiogram aiosqlite aiohttp
python shop_bot.py
"""

import asyncio, aiosqlite, aiohttp, logging, json, random, string, hashlib
from datetime import datetime
from typing import Optional
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import (Message, CallbackQuery,
                           InlineKeyboardMarkup, InlineKeyboardButton, BotCommand)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ══════════════════════════════════════════════
#  ⚙️  CONFIG — শুধু এখানে তোমার info দাও
# ══════════════════════════════════════════════
class C:
    TOKEN          = "8752679854:AAEtgiQ2q5DIb-3Q4cXzi_QqUJXQynBex0s"       # @BotFather থেকে
    ADMIN_IDS      = [8488177092]                  # তোমার Telegram ID
    OWNER_ID       = 8488177092
    SHOP_NAME      = "ANTO X SHOP"
    CURRENCY       = "৳"
    DB             = "shop.db"

    # RupantorPay
    RP_KEY         = "dqNYJl5w6x9d9cIAPP9ABIfegvM8EqB4c5L9p3gyGzxXAwn2YO"
    RP_CREATE      = "https://rupantorpay.com/api/create-payment"
    RP_VERIFY      = "https://rupantorpay.com/api/verify-payment"
    RP_SUCCESS_URL = "https://t.me/YourBotUsername"  # payment হলে redirect

    # Features
    VIP_BRONZE     = (500,  3)   # (min spend, discount%)
    VIP_SILVER     = (2000, 5)
    VIP_GOLD       = (5000, 8)
    VIP_DIAMOND    = (15000,12)
    REF_REFERRER   = 20.0
    REF_NEW_USER   = 10.0
    LOTTERY_PRICE  = 10.0
    LOTTERY_POOL   = 500.0
    MAX_ORDERS_DAY = 20

# ══════════════════════════════════════════════
#  📝  LOGGING
# ══════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("bot.log","a","utf-8"), logging.StreamHandler()]
)
log = logging.getLogger("ShopBot")

# ══════════════════════════════════════════════
#  🗄️  DATABASE
# ══════════════════════════════════════════════
class DB:
    _c: Optional[aiosqlite.Connection] = None

    @classmethod
    async def init(cls):
        cls._c = await aiosqlite.connect(C.DB)
        cls._c.row_factory = aiosqlite.Row
        await cls._c.execute("PRAGMA journal_mode=WAL")
        await cls._c.execute("PRAGMA foreign_keys=ON")
        await cls._c.commit()
        await cls._make_tables()
        await cls._seed()
        log.info("✅ Database ready")

    @classmethod
    async def _make_tables(cls):
        await cls._c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            last_name TEXT DEFAULT '',
            balance REAL DEFAULT 0,
            total_spent REAL DEFAULT 0,
            total_earned REAL DEFAULT 0,
            total_orders INTEGER DEFAULT 0,
            completed_orders INTEGER DEFAULT 0,
            referral_code TEXT UNIQUE,
            referred_by INTEGER DEFAULT 0,
            referral_count INTEGER DEFAULT 0,
            referral_earnings REAL DEFAULT 0,
            affiliate_code TEXT UNIQUE,
            affiliate_earnings REAL DEFAULT 0,
            vip_level TEXT DEFAULT 'none',
            lottery_wins INTEGER DEFAULT 0,
            lottery_tickets INTEGER DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            wishlist_count INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            ban_reason TEXT DEFAULT '',
            notifications INTEGER DEFAULT 1,
            login_count INTEGER DEFAULT 0,
            last_active INTEGER DEFAULT 0,
            joined_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            emoji TEXT DEFAULT '📦',
            description TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER DEFAULT 1,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            price REAL NOT NULL,
            stock_count INTEGER DEFAULT 0,
            sold_count INTEGER DEFAULT 0,
            view_count INTEGER DEFAULT 0,
            rating REAL DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            wishlist_count INTEGER DEFAULT 0,
            image_url TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            is_featured INTEGER DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            created_by INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS product_keys(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            key_value TEXT NOT NULL,
            status TEXT DEFAULT 'available',
            used_by INTEGER DEFAULT 0,
            order_id TEXT DEFAULT '',
            added_by INTEGER DEFAULT 0,
            added_at INTEGER DEFAULT(strftime('%s','now')),
            used_at INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS orders(
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            vip_discount REAL DEFAULT 0,
            coupon_code TEXT DEFAULT '',
            coupon_discount REAL DEFAULT 0,
            affiliate_code TEXT DEFAULT '',
            total_amount REAL NOT NULL,
            payment_method TEXT DEFAULT 'rupantorpay',
            payment_id TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            delivery_data TEXT DEFAULT '',
            admin_note TEXT DEFAULT '',
            user_note TEXT DEFAULT '',
            is_reviewed INTEGER DEFAULT 0,
            refund_amount REAL DEFAULT 0,
            refund_reason TEXT DEFAULT '',
            created_at INTEGER DEFAULT(strftime('%s','now')),
            updated_at INTEGER DEFAULT(strftime('%s','now')),
            completed_at INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS payments(
            id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            method TEXT NOT NULL,
            gateway_id TEXT DEFAULT '',
            gateway_url TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            verified INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS coupons(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            discount_type TEXT DEFAULT 'percent',
            discount_value REAL NOT NULL,
            min_order REAL DEFAULT 0,
            max_discount REAL DEFAULT 0,
            usage_limit INTEGER DEFAULT 0,
            used_count INTEGER DEFAULT 0,
            per_user_limit INTEGER DEFAULT 1,
            valid_until INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_by INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS coupon_usage(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coupon_id INTEGER,
            user_id INTEGER,
            order_id TEXT,
            discount REAL,
            used_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS reviews(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            order_id TEXT NOT NULL,
            rating INTEGER NOT NULL,
            body TEXT DEFAULT '',
            is_approved INTEGER DEFAULT 1,
            created_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS tickets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_no TEXT UNIQUE,
            user_id INTEGER NOT NULL,
            order_id TEXT DEFAULT '',
            subject TEXT NOT NULL,
            priority TEXT DEFAULT 'normal',
            status TEXT DEFAULT 'open',
            created_at INTEGER DEFAULT(strftime('%s','now')),
            updated_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS ticket_messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            is_admin INTEGER DEFAULT 0,
            message TEXT NOT NULL,
            created_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS wallet_txn(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            balance_before REAL DEFAULT 0,
            balance_after REAL DEFAULT 0,
            description TEXT DEFAULT '',
            order_id TEXT DEFAULT '',
            by_admin INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS referrals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            referred_id INTEGER NOT NULL,
            referral_code TEXT,
            status TEXT DEFAULT 'pending',
            first_order_id TEXT DEFAULT '',
            referrer_bonus REAL DEFAULT 0,
            created_at INTEGER DEFAULT(strftime('%s','now')),
            completed_at INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS lottery_draws(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draw_number INTEGER UNIQUE,
            prize_pool REAL DEFAULT 0,
            ticket_count INTEGER DEFAULT 0,
            winner_id INTEGER DEFAULT 0,
            winner_ticket TEXT DEFAULT '',
            status TEXT DEFAULT 'open',
            draw_at INTEGER DEFAULT 0,
            drawn_at INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS lottery_tickets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draw_id INTEGER,
            user_id INTEGER,
            ticket_no TEXT,
            price_paid REAL,
            is_winner INTEGER DEFAULT 0,
            prize_amount REAL DEFAULT 0,
            bought_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS flash_sales(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            sale_name TEXT DEFAULT '',
            original_price REAL NOT NULL,
            sale_price REAL NOT NULL,
            starts_at INTEGER NOT NULL,
            ends_at INTEGER NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_by INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS wishlists(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            added_at INTEGER DEFAULT(strftime('%s','now')),
            UNIQUE(user_id,product_id)
        );
        CREATE TABLE IF NOT EXISTS broadcasts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            target TEXT DEFAULT 'all',
            sent INTEGER DEFAULT 0,
            failed INTEGER DEFAULT 0,
            created_by INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS admin_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_type TEXT DEFAULT '',
            target_id TEXT DEFAULT '',
            data TEXT DEFAULT '{}',
            created_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS settings(
            k TEXT PRIMARY KEY,
            v TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS user_states(
            user_id INTEGER PRIMARY KEY,
            state TEXT NOT NULL,
            data TEXT DEFAULT '{}',
            updated_at INTEGER DEFAULT(strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS analytics(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            user_id INTEGER DEFAULT 0,
            product_id INTEGER DEFAULT 0,
            data TEXT DEFAULT '{}',
            created_at INTEGER DEFAULT(strftime('%s','now'))
        );
        """)
        await cls._c.commit()

    @classmethod
    async def _seed(cls):
        cats = [("Gaming","🎮","Gaming accounts"),("Streaming","📺","Netflix, Prime"),
                ("Social Media","📱","IG, FB, TikTok"),("VPN","🔒","VPN accounts"),
                ("Software","💻","Software keys"),("Gift Cards","🎁","Gift cards"),("Education","📚","Courses")]
        for name,emoji,desc in cats:
            await cls._c.execute("INSERT OR IGNORE INTO categories(name,emoji,description) VALUES(?,?,?)",(name,emoji,desc))
        defaults=[("welcome",f"🎉 Welcome to {C.SHOP_NAME}!\n\n💎 Premium Digital Products\n🔒 Instant Delivery\n⭐ 24/7 Support"),
                  ("maintenance","0"),("maint_msg","🔧 Under maintenance. Back soon!"),
                  ("support","@support"),("low_stock","5"),("affiliate_rate","5"),
                  ("review_reward","5"),("show_stock","1"),("auto_deliver","1")]
        for k,v in defaults:
            await cls._c.execute("INSERT OR IGNORE INTO settings(k,v) VALUES(?,?)",(k,v))
        await cls._c.commit()

    # ── Helpers ──────────────────────────────
    @classmethod
    async def one(cls,sql,p=()):
        async with cls._c.execute(sql,p) as cur:
            r=await cur.fetchone()
            return dict(r) if r else None
    @classmethod
    async def all(cls,sql,p=()):
        async with cls._c.execute(sql,p) as cur:
            return [dict(r) for r in await cur.fetchall()]
    @classmethod
    async def val(cls,sql,p=()):
        async with cls._c.execute(sql,p) as cur:
            r=await cur.fetchone()
            return r[0] if r else None
    @classmethod
    async def run(cls,sql,p=()):
        await cls._c.execute(sql,p)
        await cls._c.commit()
    @classmethod
    async def ins(cls,sql,p=()) -> int:
        async with cls._c.execute(sql,p) as cur:
            await cls._c.commit()
            return cur.lastrowid
    @classmethod
    async def cfg(cls,k,d="") -> str:
        v=await cls.val("SELECT v FROM settings WHERE k=?",(k,))
        return v if v is not None else d
    @classmethod
    async def set_cfg(cls,k,v):
        await cls.run("INSERT OR REPLACE INTO settings(k,v) VALUES(?,?)",(k,v))

# ══════════════════════════════════════════════
#  💰  RUPANTORPAY
# ══════════════════════════════════════════════
class RP:
    @staticmethod
    async def create(order_id,amount,uid,name=""):
        payload={"api_key":C.RP_KEY,"amount":str(amount),"order_id":order_id,
                 "customer_id":str(uid),"product_name":name or C.SHOP_NAME,
                 "currency":"BDT","description":f"{C.SHOP_NAME} #{order_id}",
                 "success_url":f"{C.RP_SUCCESS_URL}?order={order_id}&status=success",
                 "fail_url":f"{C.RP_SUCCESS_URL}?order={order_id}&status=fail",
                 "cancel_url":f"{C.RP_SUCCESS_URL}?order={order_id}&status=cancel",
                 "callback_url":C.RP_SUCCESS_URL}
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(C.RP_CREATE,json=payload,timeout=aiohttp.ClientTimeout(total=20)) as r:
                    return await r.json(content_type=None)
        except Exception as e:
            log.error(f"RP create: {e}")
            return {}

    @staticmethod
    async def verify(payment_id):
        url=f"{C.RP_VERIFY}?api_key={C.RP_KEY}&payment_id={payment_id}"
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url,timeout=aiohttp.ClientTimeout(total=15)) as r:
                    return await r.json(content_type=None)
        except Exception as e:
            log.error(f"RP verify: {e}")
            return {}

# ══════════════════════════════════════════════
#  🔧  HELPERS
# ══════════════════════════════════════════════
def kb(rows):
    """Build InlineKeyboardMarkup. rows = list of list of (text,data) or (text,url,'url')"""
    btns=[]
    for row in rows:
        r=[]
        for b in row:
            if len(b)==3 and b[2]=="url":
                r.append(InlineKeyboardButton(text=b[0],url=b[1]))
            else:
                r.append(InlineKeyboardButton(text=b[0],callback_data=b[1][:64]))
        btns.append(r)
    return InlineKeyboardMarkup(inline_keyboard=btns)

def vip_emoji(level):
    return {"bronze":"🥉","silver":"🥈","gold":"🥇","diamond":"💎"}.get(level,"")

def vip_disc(level):
    return {"bronze":C.VIP_BRONZE[1],"silver":C.VIP_SILVER[1],
            "gold":C.VIP_GOLD[1],"diamond":C.VIP_DIAMOND[1]}.get(level,0)

def order_emoji(status):
    return {"pending":"⏳","paid":"💳","delivered":"✅","cancelled":"❌",
            "refunded":"💸","failed":"🚫","pending_manual":"🔄"}.get(status,"❓")

def gen_code(prefix="",n=10):
    return prefix+"".join(random.choices(string.ascii_uppercase+string.digits,k=n))

def ts():
    return int(datetime.now().timestamp())

def fmt_date(t):
    return datetime.fromtimestamp(int(t)).strftime("%d/%m/%y %H:%M") if t else "—"

async def add_balance(uid,amount,type_,desc="",oid="",by=0):
    u=await DB.one("SELECT balance FROM users WHERE id=?",(uid,))
    if not u: return False
    before=float(u["balance"]); after=before+amount
    if after<0: return False
    await DB.run("UPDATE users SET balance=balance+? WHERE id=?",(amount,uid))
    await DB.run("INSERT INTO wallet_txn(user_id,type,amount,balance_before,balance_after,description,order_id,by_admin) VALUES(?,?,?,?,?,?,?,?)",
                 (uid,type_,amount,before,after,desc,oid,by))
    return True

async def update_vip(uid):
    u=await DB.one("SELECT total_spent,vip_level FROM users WHERE id=?",(uid,))
    if not u: return
    spent=float(u["total_spent"]); old=u["vip_level"]; new="none"
    if spent>=C.VIP_DIAMOND[0]:   new="diamond"
    elif spent>=C.VIP_GOLD[0]:    new="gold"
    elif spent>=C.VIP_SILVER[0]:  new="silver"
    elif spent>=C.VIP_BRONZE[0]:  new="bronze"
    if new!=old:
        await DB.run("UPDATE users SET vip_level=? WHERE id=?",(new,uid))
        if new!="none":
            await bot.send_message(uid,f"🎊 <b>VIP Level Up!</b>\n\n{vip_emoji(new)} <b>{new.upper()} VIP</b>!\nEnjoy {vip_disc(new)}% discount! 🎉")

async def reg_user(from_user):
    uid=from_user.id
    u=await DB.one("SELECT * FROM users WHERE id=?",(uid,))
    if not u:
        rc=gen_code("REF",8); ac=gen_code("AFF",8)
        await DB.run("INSERT INTO users(id,username,first_name,last_name,referral_code,affiliate_code,last_active) VALUES(?,?,?,?,?,?,?)",
                     (uid,from_user.username or "",from_user.first_name or "",from_user.last_name or "",rc,ac,ts()))
        u=await DB.one("SELECT * FROM users WHERE id=?",(uid,))
        await DB.run("INSERT INTO analytics(event,user_id) VALUES('register',?)",(uid,))
    else:
        await DB.run("UPDATE users SET username=?,first_name=?,last_name=?,last_active=?,login_count=login_count+1 WHERE id=?",
                     (from_user.username or "",from_user.first_name or "",from_user.last_name or "",ts(),uid))
        u=await DB.one("SELECT * FROM users WHERE id=?",(uid,))
    return u

async def send(event,text,keyboard=None,edit=True):
    opts={"reply_markup":keyboard} if keyboard else {}
    if isinstance(event,CallbackQuery) and edit:
        try: await event.message.edit_text(text,reply_markup=keyboard,parse_mode="HTML")
        except: await event.message.answer(text,parse_mode="HTML",**opts)
    elif isinstance(event,Message):
        await event.answer(text,parse_mode="HTML",**opts)
    elif isinstance(event,CallbackQuery):
        await event.message.answer(text,parse_mode="HTML",**opts)

# ══════════════════════════════════════════════
#  📦  ORDER MANAGER
# ══════════════════════════════════════════════
async def create_order(uid,pid,coupon=""):
    prod=await DB.one("SELECT p.*,c.name as cat_name,c.emoji FROM products p LEFT JOIN categories c ON p.category_id=c.id WHERE p.id=? AND p.is_active=1",(pid,))
    if not prod: return {"ok":False,"msg":"❌ Product not found."}
    avail=await DB.val("SELECT COUNT(*) FROM product_keys WHERE product_id=? AND status='available'",(pid,))
    if not avail: return {"ok":False,"msg":"❌ Out of stock!"}
    today=await DB.val("SELECT COUNT(*) FROM orders WHERE user_id=? AND date(created_at,'unixepoch')=date('now')",(uid,))
    if today>=C.MAX_ORDERS_DAY: return {"ok":False,"msg":f"❌ Daily limit ({C.MAX_ORDERS_DAY}) reached."}

    flash=await DB.one("SELECT * FROM flash_sales WHERE product_id=? AND is_active=1 AND starts_at<=? AND ends_at>=?",(pid,ts(),ts()))
    price=float(flash["sale_price"]) if flash else float(prod["price"])

    u=await DB.one("SELECT * FROM users WHERE id=?",(uid,))
    disc_pct=vip_disc(u["vip_level"]); vip_amt=price*disc_pct/100

    coup_amt=0.0
    if coupon:
        c=await DB.one("SELECT * FROM coupons WHERE code=? AND is_active=1",(coupon.upper(),))
        if c:
            used=await DB.val("SELECT COUNT(*) FROM coupon_usage WHERE coupon_id=? AND user_id=?",(c["id"],uid))
            if (not c["per_user_limit"] or used<c["per_user_limit"]) and (not c["usage_limit"] or c["used_count"]<c["usage_limit"]):
                if not c["min_order"] or price>=c["min_order"]:
                    coup_amt=price*c["discount_value"]/100 if c["discount_type"]=="percent" else min(c["discount_value"],price)
                    if c["max_discount"]: coup_amt=min(coup_amt,c["max_discount"])

    total=max(0,price-vip_amt-coup_amt)
    oid=gen_code("ANTO",10)
    await DB.run("INSERT INTO orders(id,user_id,product_id,unit_price,subtotal,vip_discount,coupon_code,coupon_discount,total_amount) VALUES(?,?,?,?,?,?,?,?,?)",
                 (oid,uid,pid,price,price,vip_amt,coupon,coup_amt,total))
    return {"ok":True,"oid":oid,"prod":prod,"price":price,"vip_amt":vip_amt,"coup_amt":coup_amt,"total":total,"flash":flash}

async def deliver_order(oid):
    order=await DB.one("SELECT o.*,p.name as pname FROM orders o LEFT JOIN products p ON o.product_id=p.id WHERE o.id=?",(oid,))
    if not order: return {"ok":False,"msg":"Not found"}
    if order["status"]=="delivered": return {"ok":False,"msg":"Already delivered"}
    key=await DB.one("SELECT * FROM product_keys WHERE product_id=? AND status='available' LIMIT 1",(order["product_id"],))
    if not key:
        await DB.run("UPDATE orders SET status='pending_manual' WHERE id=?",(oid,))
        for aid in C.ADMIN_IDS:
            await bot.send_message(aid,f"⚠️ <b>Out of Stock!</b>\n🆔 {oid}\n👤 {order['user_id']}\n📦 {order['pname']}",
                                   reply_markup=kb([[("📤 Deliver",f"adm_deliver:{oid}")]]))
        await bot.send_message(order["user_id"],f"✅ Payment confirmed!\n🆔 <code>{oid}</code>\n⏳ Delivery within 24h.")
        return {"ok":False,"msg":"out_of_stock"}

    await DB.run("UPDATE product_keys SET status='used',used_by=?,order_id=?,used_at=? WHERE id=?",(order["user_id"],oid,ts(),key["id"]))
    await DB.run("UPDATE products SET stock_count=MAX(0,stock_count-1),sold_count=sold_count+1 WHERE id=?",(order["product_id"],))
    await DB.run("UPDATE orders SET status='delivered',delivery_data=?,completed_at=?,updated_at=? WHERE id=?",(key["key_value"],ts(),ts(),oid))
    await DB.run("UPDATE users SET total_spent=total_spent+?,completed_orders=completed_orders+? WHERE id=?",(order["total_amount"],1,order["user_id"]))
    await update_vip(order["user_id"])

    # Referral complete
    ref=await DB.one("SELECT * FROM referrals WHERE referred_id=? AND status='pending'",(order["user_id"],))
    if ref:
        await DB.run("UPDATE referrals SET status='completed',first_order_id=?,referrer_bonus=?,completed_at=? WHERE id=?",
                     (oid,C.REF_REFERRER,ts(),ref["id"]))
        await DB.run("UPDATE users SET referral_count=referral_count+1,referral_earnings=referral_earnings+? WHERE id=?",(C.REF_REFERRER,ref["referrer_id"]))
        if C.REF_REFERRER>0:
            await add_balance(ref["referrer_id"],C.REF_REFERRER,"referral_comm",f"Referral commission #{oid}")
            await bot.send_message(ref["referrer_id"],f"💰 <b>Referral Commission!</b>\nYour friend made their first purchase!\n+{C.CURRENCY}{C.REF_REFERRER:.2f} added to wallet!")

    # Check low stock
    stk=await DB.val("SELECT COUNT(*) FROM product_keys WHERE product_id=? AND status='available'",(order["product_id"],))
    limit=int(await DB.cfg("low_stock","5"))
    if stk<=limit:
        prod=await DB.one("SELECT name FROM products WHERE id=?",(order["product_id"],))
        for aid in C.ADMIN_IDS:
            await bot.send_message(aid,f"⚠️ Low Stock!\n📦 {prod['name']}\n🔑 Remaining: {stk}",
                                   reply_markup=kb([[("📦 Add Stock",f"adm_stock:{order['product_id']}")]]))

    notify=f"""🎉 <b>Order Delivered!</b>

📦 Product: <b>{order['pname']}</b>
🆔 Order: <code>{oid}</code>
💰 Amount: <b>{C.CURRENCY}{float(order['total_amount']):.2f}</b>

━━━━━━━━━━━━━━━
🔑 <b>Your Delivery:</b>
<pre>{key['key_value']}</pre>
━━━━━━━━━━━━━━━
⭐ Please leave a review!
📞 Support: {await DB.cfg('support','@support')}"""
    await bot.send_message(order["user_id"],notify,
                           reply_markup=kb([[("⭐ Review",f"review:{oid}"),("📦 My Orders","my_orders")],
                                           [("🛒 Buy More","shop"),("💬 Support","support")]]))
    for aid in C.ADMIN_IDS:
        await bot.send_message(aid,f"✅ Delivered!\n🆔 {oid}\n👤 {order['user_id']}\n📦 {order['pname']}\n💰 {C.CURRENCY}{float(order['total_amount']):.2f}")
    return {"ok":True,"key":key["key_value"]}

# ══════════════════════════════════════════════
#  🤖  FSM STATES
# ══════════════════════════════════════════════
class S(StatesGroup):
    # User
    coupon=State(); search=State(); ticket_sub=State(); ticket_msg=State()
    ticket_reply=State(); review_rating=State(); review_text=State()
    # Admin
    a_prod_name=State(); a_prod_price=State(); a_prod_cat=State()
    a_prod_desc=State(); a_prod_stock=State()
    a_stock_keys=State(); a_broadcast=State(); a_bal_uid=State()
    a_bal_amt=State(); a_setting_val=State(); a_ticket_reply=State()
    a_flash_price=State(); a_flash_hrs=State(); a_coupon=State()
    a_manual_del=State(); a_ban_uid=State(); a_refund_amt=State()

# ══════════════════════════════════════════════
#  🤖  BOT + DISPATCHER
# ══════════════════════════════════════════════
bot=Bot(token=C.TOKEN,parse_mode="HTML")
dp=Dispatcher(storage=MemoryStorage())
r=Router(); dp.include_router(r)

# ══════════════════════════════════════════════
#  🏠  SCREENS
# ══════════════════════════════════════════════
async def main_menu(ev,user):
    bal=float(user["balance"]); vip=user["vip_level"]
    vs=f" {vip_emoji(vip)}" if vip!="none" else ""
    name=f"{user.get('first_name','')}".strip() or f"@{user.get('username','')}" or f"User#{user['id']}"
    welcome=await DB.cfg("welcome",f"Welcome to {C.SHOP_NAME}!")
    flash=await DB.val("SELECT COUNT(*) FROM flash_sales WHERE is_active=1 AND starts_at<=? AND ends_at>=?",(ts(),ts()))
    text=(f"👋 Hello <b>{name}</b>{vs}!\n\n{welcome}\n\n"
          f"💰 Wallet: <b>{C.CURRENCY}{bal:.2f}</b>\n"
          f"📦 Orders: <b>{user['total_orders']}</b>")
    if flash: text+=f"\n\n⚡ <b>{flash} FLASH SALES ACTIVE!</b>"
    rows=[[("🛒 Shop","shop"),("⚡ Flash Sales","flash")],
          [("📦 My Orders","my_orders"),("💰 Wallet","wallet")],
          [("🔗 Referral","referral"),("🎰 Lottery","lottery")],
          [("💬 Support","support"),("❤️ Wishlist","wishlist")],
          [("👤 Profile","profile"),("🔍 Search","search_start")]]
    if user["id"] in C.ADMIN_IDS: rows.append([("⚙️ Admin Panel","admin")])
    await send(ev,text,kb(rows))

async def show_shop(ev):
    cats=await DB.all("SELECT c.*,COUNT(p.id) as cnt FROM categories c LEFT JOIN products p ON p.category_id=c.id AND p.is_active=1 WHERE c.is_active=1 GROUP BY c.id ORDER BY c.sort_order,c.id")
    text=f"🛒 <b>{C.SHOP_NAME} — Shop</b>\n\nChoose a category:"
    rows=[]; row=[]
    for c in cats:
        row.append((f"{c['emoji']} {c['name']} ({c['cnt']})","cat:"+str(c["id"])))
        if len(row)==2: rows.append(row); row=[]
    if row: rows.append(row)
    rows+=[[("⚡ Flash Sales","flash"),("🔍 Search","search_start")],[("🔙 Back","menu")]]
    await send(ev,text,kb(rows))

async def show_cat(ev,cid,page=0):
    cat=await DB.one("SELECT * FROM categories WHERE id=?",(cid,))
    if not cat: await send(ev,"❌ Not found."); return
    offset=page*8
    prods=await DB.all(
        "SELECT p.*,COALESCE((SELECT sale_price FROM flash_sales WHERE product_id=p.id AND is_active=1 AND starts_at<=? AND ends_at>=? LIMIT 1),p.price) as cur FROM products p WHERE p.category_id=? AND p.is_active=1 ORDER BY p.sort_order DESC,p.id DESC LIMIT 8 OFFSET ?",
        (ts(),ts(),cid,offset))
    total=await DB.val("SELECT COUNT(*) FROM products WHERE category_id=? AND is_active=1",(cid,))
    text=f"{cat['emoji']} <b>{cat['name']}</b>\n{cat['description']}\n\n📦 <b>{total} products</b>"
    rows=[]
    for p in prods:
        stk=await DB.val("SELECT COUNT(*) FROM product_keys WHERE product_id=? AND status='available'",(p["id"],))
        s="✅"+str(stk) if stk else "❌OOS"; flash=" ⚡" if float(p["cur"])<float(p["price"]) else ""
        rows.append([(f"{p['name']} — {C.CURRENCY}{float(p['cur']):.2f} ({s}){flash}","prod:"+str(p["id"]))])
    pag=[]
    if page>0: pag.append(("◀️ Prev",f"cat_p:{cid}:{page-1}"))
    if (offset+8)<total: pag.append(("Next ▶️",f"cat_p:{cid}:{page+1}"))
    if pag: rows.append(pag)
    rows.append([("🔙 Shop","shop")]); await send(ev,text,kb(rows))

async def show_prod(ev,pid,user):
    p=await DB.one("SELECT p.*,c.name as cn,c.emoji as ce FROM products p LEFT JOIN categories c ON p.category_id=c.id WHERE p.id=? AND p.is_active=1",(pid,))
    if not p: await send(ev,"❌ Not found."); return
    await DB.run("UPDATE products SET view_count=view_count+1 WHERE id=?",(pid,))
    flash=await DB.one("SELECT * FROM flash_sales WHERE product_id=? AND is_active=1 AND starts_at<=? AND ends_at>=?",(pid,ts(),ts()))
    price=float(flash["sale_price"]) if flash else float(p["price"])
    stk=await DB.val("SELECT COUNT(*) FROM product_keys WHERE product_id=? AND status='available'",(pid,))
    rat=await DB.one("SELECT AVG(rating) as avg,COUNT(*) as cnt FROM reviews WHERE product_id=? AND is_approved=1",(pid,))
    vd=vip_disc(user["vip_level"]); fp=price*(1-vd/100)
    text=f"{p['ce']} <b>{p['name']}</b>\n<i>📁 {p['cn']}</i>\n\n{p['description']}\n\n━━━━━━━━━━━━\n"
    if flash:
        left=max(0,flash["ends_at"]-ts()); h,m=left//3600,(left%3600)//60
        text+=f"⚡ <b>FLASH!</b> {h}h{m}m left\n💰 <s>{C.CURRENCY}{p['price']:.2f}</s> → <b>{C.CURRENCY}{price:.2f}</b>\n"
    else:
        text+=f"💰 Price: <b>{C.CURRENCY}{price:.2f}</b>\n"
    if vd: text+=f"💎 Your VIP Price: <b>{C.CURRENCY}{fp:.2f}</b> (-{vd}%)\n"
    show_stk=await DB.cfg("show_stock","1")=="1"
    if show_stk: text+=f"📦 Stock: <b>{'✅ In Stock' if stk else '❌ Out of Stock'}</b>\n"
    text+=f"✅ Sold: <b>{p['sold_count']}</b> | 👀 <b>{p['view_count']}</b>\n"
    if rat and rat["cnt"]: text+=f"⭐ {float(rat['avg'] or 0):.1f}/5 ({rat['cnt']} reviews)\n"
    text+="━━━━━━━━━━━━"
    inwl=await DB.one("SELECT id FROM wishlists WHERE user_id=? AND product_id=?",(user["id"],pid))
    wl=("❤️ In Wishlist",f"rm_wl:{pid}") if inwl else ("🤍 Wishlist",f"add_wl:{pid}")
    rows=[]
    if stk: rows.append([(f"🛒 Buy — {C.CURRENCY}{fp:.2f}",f"checkout:{pid}")])
    else: rows.append([("❌ Out of Stock","noop")])
    rows+=[[wl,("⭐ Reviews",f"reviews:{pid}")],[("🔙 Back",f"cat:{p['category_id']}")]]
    await send(ev,text,kb(rows))

async def show_checkout(ev,pid,user,coupon=""):
    p=await DB.one("SELECT * FROM products WHERE id=? AND is_active=1",(pid,))
    if not p: await send(ev,"❌ Not found."); return
    flash=await DB.one("SELECT * FROM flash_sales WHERE product_id=? AND is_active=1 AND starts_at<=? AND ends_at>=?",(pid,ts(),ts()))
    price=float(flash["sale_price"]) if flash else float(p["price"])
    vd=vip_disc(user["vip_level"]); vip_a=price*vd/100
    coup_a=0.0
    if coupon:
        c=await DB.one("SELECT * FROM coupons WHERE code=? AND is_active=1",(coupon.upper(),))
        if c:
            used=await DB.val("SELECT COUNT(*) FROM coupon_usage WHERE coupon_id=? AND user_id=?",(c["id"],user["id"]))
            ok=(not c["per_user_limit"] or used<c["per_user_limit"]) and (not c["usage_limit"] or c["used_count"]<c["usage_limit"])
            if ok and (not c["min_order"] or price>=c["min_order"]):
                coup_a=price*c["discount_value"]/100 if c["discount_type"]=="percent" else min(c["discount_value"],price)
                if c["max_discount"]: coup_a=min(coup_a,c["max_discount"])
    total=max(0,price-vip_a-coup_a); bal=float(user["balance"])
    res=await create_order(user["id"],pid,coupon)
    if not res["ok"]: await send(ev,res["msg"]); return
    oid=res["oid"]
    text=(f"🛒 <b>Checkout</b>\n\n📦 {p['name']}\n💰 {C.CURRENCY}{price:.2f}\n"
          +(f"💎 VIP: -{C.CURRENCY}{vip_a:.2f}\n" if vip_a else "")
          +(f"🎫 Coupon: -{C.CURRENCY}{coup_a:.2f}\n" if coup_a else "")
          +f"━━━━━━━━━━━━\n💵 Total: <b>{C.CURRENCY}{total:.2f}</b>\n"
          +f"💼 Wallet: {C.CURRENCY}{bal:.2f}\n\n🆔 Order: <code>{oid}</code>\n\n📲 Choose payment:")
    rows=[[("💳 Pay with RupantorPay",f"pay_rp:{oid}")]]
    if bal>=total: rows.append([(f"💰 Pay from Wallet ({C.CURRENCY}{bal:.2f})",f"pay_wal:{oid}")])
    if not coupon: rows.append([("🎫 Apply Coupon",f"coupon:{oid}")])
    rows.append([("❌ Cancel",f"prod:{pid}")]); await send(ev,text,kb(rows))

async def show_my_orders(ev,uid,page=0):
    offset=page*10
    orders=await DB.all("SELECT o.*,p.name as pn FROM orders o LEFT JOIN products p ON o.product_id=p.id WHERE o.user_id=? ORDER BY o.created_at DESC LIMIT 10 OFFSET ?",(uid,offset))
    total=await DB.val("SELECT COUNT(*) FROM orders WHERE user_id=?",(uid,))
    text=f"📦 <b>My Orders</b> ({total} total)\n\n"; rows=[]
    if not orders: text+="No orders yet. Start shopping! 🛒"
    else:
        for o in orders:
            s=order_emoji(o["status"])
            text+=f"{s} <code>{o['id']}</code>\n   📦 {o['pn']}\n   {C.CURRENCY}{float(o['total_amount']):.2f} | {fmt_date(o['created_at'])}\n\n"
            if o["status"]=="delivered" and not o["is_reviewed"]:
                rows.append([(f"⭐ Review",f"review:{o['id']}")])
    pag=[]
    if page>0: pag.append(("◀️",f"ord_p:{page-1}"))
    if (offset+10)<total: pag.append(("▶️",f"ord_p:{page+1}"))
    if pag: rows.append(pag)
    rows.append([("🔙 Back","menu")]); await send(ev,text,kb(rows))

async def show_wallet(ev,user):
    txns=await DB.all("SELECT * FROM wallet_txn WHERE user_id=? ORDER BY created_at DESC LIMIT 10",(user["id"],))
    text=(f"💰 <b>My Wallet</b>\n\n💵 Balance: <b>{C.CURRENCY}{float(user['balance']):.2f}</b>\n"
          f"💳 Spent: <b>{C.CURRENCY}{float(user['total_spent']):.2f}</b>\n"
          f"📦 Orders: <b>{user['total_orders']}</b> | ✅ <b>{user['completed_orders']}</b>\n\n"
          "━━━━━━━━━━━━\n📋 <b>Transactions:</b>\n\n")
    for t in txns:
        sign="+" if float(t["amount"])>0 else ""
        emoji="📈" if float(t["amount"])>0 else "📉"
        text+=f"{emoji} {sign}{C.CURRENCY}{abs(float(t['amount'])):.2f} — <i>{t['description']}</i>\n   {fmt_date(t['created_at'])}\n"
    await send(ev,text,kb([[("🔙 Back","menu")]]))

async def show_profile(ev,user):
    vip=user["vip_level"]
    vs=f"{vip_emoji(vip)} {vip.upper()}" if vip!="none" else "Standard"
    name=f"{user.get('first_name','')} {user.get('last_name','')}".strip() or f"@{user.get('username','')}"
    date=datetime.fromtimestamp(user["joined_at"]).strftime("%d %b %Y")
    text=(f"👤 <b>Profile</b>\n\n🪪 {name}\n🆔 <code>{user['id']}</code>\n"
          f"📅 Joined: {date}\n\n━━━━━━━━━━━━\n"
          f"💰 Balance: <b>{C.CURRENCY}{float(user['balance']):.2f}</b>\n"
          f"💳 Spent: <b>{C.CURRENCY}{float(user['total_spent']):.2f}</b>\n"
          f"📦 Orders: <b>{user['total_orders']}</b> | ✅ <b>{user['completed_orders']}</b>\n\n"
          f"━━━━━━━━━━━━\n💎 VIP: <b>{vs}</b>\n")
    if vip!="none": text+=f"🎁 Discount: <b>{vip_disc(vip)}%</b>\n"
    text+=(f"\n🔗 Referrals: <b>{user['referral_count']}</b>\n"
           f"💰 Ref Earnings: <b>{C.CURRENCY}{float(user['referral_earnings']):.2f}</b>\n"
           f"🎰 Lottery Wins: <b>{user['lottery_wins']}</b>")
    await send(ev,text,kb([[("📦 Orders","my_orders"),("💰 Wallet","wallet")],[("🔗 Referral","referral"),("🎫 Tickets","my_tickets")],[("🔙 Back","menu")]]))

async def show_referral(ev,user):
    link=f"https://t.me/{C.TOKEN.split(':')[0]}?start=ref_{user['referral_code']}"
    text=(f"🔗 <b>Referral Program</b>\n\n"
          f"💰 You earn: <b>{C.CURRENCY}{C.REF_REFERRER:.2f}</b> per referral\n"
          f"🎁 Friend gets: <b>{C.CURRENCY}{C.REF_NEW_USER:.2f}</b> bonus\n\n"
          f"━━━━━━━━━━━━\n👥 Referrals: <b>{user['referral_count']}</b>\n"
          f"💰 Earned: <b>{C.CURRENCY}{float(user['referral_earnings']):.2f}</b>\n\n"
          f"🔗 Your Link:\n<code>{link}</code>\n\n"
          f"📋 Your Code: <code>{user['referral_code']}</code>")
    await send(ev,text,kb([[("🔙 Back","menu")]]))

async def show_lottery(ev,user):
    draw=await DB.one("SELECT * FROM lottery_draws WHERE status='open' ORDER BY id DESC LIMIT 1")
    if not draw:
        num=(await DB.val("SELECT MAX(draw_number) FROM lottery_draws") or 0)+1
        await DB.run("INSERT INTO lottery_draws(draw_number,prize_pool,draw_at) VALUES(?,?,?)",(num,C.LOTTERY_POOL,ts()+86400))
        draw=await DB.one("SELECT * FROM lottery_draws WHERE status='open' ORDER BY id DESC LIMIT 1")
    my_tkts=await DB.all("SELECT * FROM lottery_tickets WHERE user_id=? AND draw_id=?",(user["id"],draw["id"]))
    draw_at=fmt_date(draw["draw_at"])
    text=(f"🎰 <b>Lottery</b>\n\n🎟️ Ticket: <b>{C.CURRENCY}{C.LOTTERY_PRICE}</b>\n"
          f"🏆 Prize Pool: <b>{C.CURRENCY}{float(draw['prize_pool']):.2f}</b>\n"
          f"🎫 Tickets Sold: <b>{draw['ticket_count']}</b>\n📅 Draw #{draw['draw_number']} — {draw_at}\n\n"
          f"━━━━━━━━━━━━\n💰 Your Balance: <b>{C.CURRENCY}{float(user['balance']):.2f}</b>\n"
          f"🎟️ Your Tickets: <b>{len(my_tkts)}</b>\n")
    if my_tkts:
        text+="\n📋 Tickets:\n"+"".join(f"🎫 <code>{t['ticket_no']}</code>\n" for t in my_tkts)
    rows=[]
    if float(user["balance"])>=C.LOTTERY_PRICE: rows.append([(f"🎟️ Buy Ticket — {C.CURRENCY}{C.LOTTERY_PRICE}","buy_ticket")])
    else: rows.append([("❌ Insufficient Balance","noop")])
    rows.append([("🔙 Back","menu")]); await send(ev,text,kb(rows))

async def show_wishlist(ev,uid):
    items=await DB.all("SELECT w.*,p.name,p.price,p.is_active FROM wishlists w JOIN products p ON w.product_id=p.id WHERE w.user_id=? ORDER BY w.added_at DESC",(uid,))
    text=f"❤️ <b>Wishlist</b> ({len(items)} items)\n\n"; rows=[]
    if not items: text+="Empty. Browse products and add favorites!"
    else:
        for item in items:
            a="✅" if item["is_active"] else "❌"
            text+=f"{a} <b>{item['name']}</b> — {C.CURRENCY}{float(item['price']):.2f}\n"
            rows.append([(f"🛒 {item['name'][:20]}",f"prod:{item['product_id']}"),(f"🗑️ Remove",f"rm_wl:{item['product_id']}")])
    rows.append([("🛒 Shop","shop"),("🔙 Back","menu")]); await send(ev,text,kb(rows))

async def show_flash(ev):
    sales=await DB.all("SELECT fs.*,p.name FROM flash_sales fs JOIN products p ON fs.product_id=p.id WHERE fs.is_active=1 AND fs.starts_at<=? AND fs.ends_at>=? ORDER BY fs.ends_at ASC",(ts(),ts()))
    text="⚡ <b>Flash Sales</b>\n\n"; rows=[]
    if not sales: text+="No flash sales right now. Check back soon!"
    else:
        for s in sales:
            left=max(0,s["ends_at"]-ts()); h,m=left//3600,(left%3600)//60
            disc=round((1-float(s["sale_price"])/float(s["original_price"]))*100)
            text+=f"🔥 <b>{s['name']}</b>\n   {C.CURRENCY}<s>{s['original_price']:.2f}</s> → <b>{C.CURRENCY}{s['sale_price']:.2f}</b> (-{disc}%)\n   ⏰ {h}h {m}m left\n\n"
            rows.append([(f"🛒 Buy {s['name'][:20]}",f"checkout:{s['product_id']}")])
    rows.append([("🔙 Back","menu")]); await send(ev,text,kb(rows))

async def show_support(ev):
    sup=await DB.cfg("support","@support")
    text=f"💬 <b>Support Center</b>\n\nWe're here 24/7!\n\n📞 Contact: {sup}\n\nChoose an option:"
    rows=[[("🆕 New Ticket","open_ticket"),("📋 My Tickets","my_tickets")],
          [(f"📞 Contact Support",f"https://t.me/{sup.lstrip('@')}","url")],
          [("🔙 Back","menu")]]
    await send(ev,text,kb(rows))

async def show_help(ev):
    sup=await DB.cfg("support","@support")
    text=(f"❓ <b>Help & FAQ</b>\n\n"
          f"<b>Commands:</b>\n/start — Main menu\n/shop — Products\n"
          f"/myorders — My orders\n/balance — Wallet\n/referral — Referral\n"
          f"/lottery — Lottery\n/support — Support\n/profile — Profile\n\n"
          f"<b>How to buy?</b>\nShop → Select product → Pay → Auto delivery!\n\n"
          f"📞 Support: {sup}")
    await send(ev,text,kb([[("💬 Support","open_ticket"),("🔙 Back","menu")]]))

async def show_my_tickets(ev,uid):
    tkts=await DB.all("SELECT * FROM tickets WHERE user_id=? ORDER BY updated_at DESC LIMIT 10",(uid,))
    text="🎫 <b>My Tickets</b>\n\n"; rows=[]
    if not tkts: text+="No tickets yet."
    else:
        for t in tkts:
            s={"open":"🔵","resolved":"✅","closed":"⚫"}.get(t["status"],"🟡")
            text+=f"{s} <code>{t['ticket_no']}</code> — {t['subject']}\n   {fmt_date(t['updated_at'])}\n\n"
            rows.append([(f"{s} {t['ticket_no']}",f"view_tkt:{t['id']}")])
    rows.append([("🆕 New Ticket","open_ticket"),("🔙 Back","support")]); await send(ev,text,kb(rows))

# ══════════════════════════════════════════════
#  ⚙️  ADMIN SCREENS
# ══════════════════════════════════════════════
async def adm_panel(ev):
    us=await DB.val("SELECT COUNT(*) FROM users") or 0
    rev=await DB.val("SELECT SUM(total_amount) FROM orders WHERE status='delivered'") or 0
    ords=await DB.val("SELECT COUNT(*) FROM orders") or 0
    pen=await DB.val("SELECT COUNT(*) FROM orders WHERE status IN ('pending','pending_manual')") or 0
    stk=await DB.val("SELECT COUNT(*) FROM product_keys WHERE status='available'") or 0
    text=(f"⚙️ <b>Admin — {C.SHOP_NAME}</b>\n\n👥 Users: <b>{us}</b>\n"
          f"📦 Orders: <b>{ords}</b> | ⏳ Pending: <b>{pen}</b>\n"
          f"💰 Revenue: <b>{C.CURRENCY}{float(rev):.2f}</b>\n🔑 Stock: <b>{stk}</b>")
    rows=[[("📦 Products","adm_prods"),("📋 Orders","adm_ords")],
          [("👥 Users","adm_users"),("📊 Stats","adm_stats")],
          [("🎫 Coupons","adm_coupons"),("⚡ Flash Sales","adm_flash")],
          [("📢 Broadcast","adm_bcast"),("🎰 Lottery","adm_lottery")],
          [("🎫 Tickets","adm_tickets"),("⚙️ Settings","adm_settings")],
          [("📤 Manual Deliver","adm_man_del"),("🔧 Maintenance","adm_maint")],
          [("🔙 Menu","menu")]]
    await send(ev,text,kb(rows))

async def adm_prods(ev):
    prods=await DB.all("SELECT p.*,(SELECT COUNT(*) FROM product_keys WHERE product_id=p.id AND status='available') as stk FROM products WHERE is_active=1 ORDER BY id DESC LIMIT 20")
    text="📦 <b>Products</b>\n\n"; rows=[[("➕ Add Product","adm_add_prod")]]
    for p in prods:
        text+=f"🔹 [{p['id']}] <b>{p['name']}</b> — {C.CURRENCY}{p['price']} | 📦{p['stk']} | ✅{p['sold_count']}\n"
        rows.append([(f"📦 +Stock #{p['id']}",f"adm_stock:{p['id']}"),(f"🔁",f"adm_tog:{p['id']}"),(f"🗑️",f"adm_delprod:{p['id']}")])
    rows.append([("🔙 Back","admin")]); await send(ev,text,kb(rows))

async def adm_users(ev):
    users=await DB.all("SELECT * FROM users ORDER BY total_spent DESC LIMIT 20")
    total=await DB.val("SELECT COUNT(*) FROM users")
    text=f"👥 <b>Users</b> ({total} total)\n\n"; rows=[]
    for u in users:
        ban=" 🚫" if u["is_banned"] else ""; v=f" {vip_emoji(u['vip_level'])}" if u["vip_level"]!="none" else ""
        text+=f"👤 <code>{u['id']}</code> @{u['username']}{v}{ban}\n   {C.CURRENCY}{float(u['balance']):.2f} | 📦{u['total_orders']}\n"
        rows.append([(f"👤 #{u['id']} {(u['username'] or u['first_name'])[:15]}",f"adm_user:{u['id']}")])
    rows.append([("🔙 Back","admin")]); await send(ev,text,kb(rows))

async def adm_ords(ev):
    ords=await DB.all("SELECT o.*,p.name as pn,u.username as un FROM orders o LEFT JOIN products p ON o.product_id=p.id LEFT JOIN users u ON o.user_id=u.id ORDER BY o.created_at DESC LIMIT 20")
    text="📋 <b>Orders</b>\n\n"; rows=[]
    for o in ords:
        s=order_emoji(o["status"])
        text+=f"{s} <code>{o['id'][:12]}</code> @{o['un']}\n   📦 {o['pn']} | {C.CURRENCY}{float(o['total_amount']):.2f}\n\n"
        rows.append([(f"{s} {o['id'][:12]}",f"adm_ord:{o['id']}")])
    rows.append([("🔙 Back","admin")]); await send(ev,text,kb(rows))

async def adm_stats(ev):
    us=await DB.val("SELECT COUNT(*) FROM users") or 0
    t_u=await DB.val("SELECT COUNT(*) FROM users WHERE date(joined_at,'unixepoch')=date('now')") or 0
    w_u=await DB.val("SELECT COUNT(*) FROM users WHERE joined_at>?-604800",(ts(),)) or 0
    rev=await DB.val("SELECT SUM(total_amount) FROM orders WHERE status='delivered'") or 0
    r_d=await DB.val("SELECT SUM(total_amount) FROM orders WHERE status='delivered' AND date(created_at,'unixepoch')=date('now')") or 0
    r_w=await DB.val("SELECT SUM(total_amount) FROM orders WHERE status='delivered' AND created_at>?-604800",(ts(),)) or 0
    ords=await DB.val("SELECT COUNT(*) FROM orders") or 0
    o_d=await DB.val("SELECT COUNT(*) FROM orders WHERE date(created_at,'unixepoch')=date('now')") or 0
    stk=await DB.val("SELECT COUNT(*) FROM product_keys WHERE status='available'") or 0
    top=await DB.all("SELECT p.name,COUNT(o.id) as cnt FROM orders o JOIN products p ON o.product_id=p.id WHERE o.status='delivered' GROUP BY o.product_id ORDER BY cnt DESC LIMIT 5")
    text=(f"📊 <b>Statistics</b>\n\n👥 <b>Users</b>\nTotal: {us} | Today: +{t_u} | Week: +{w_u}\n\n"
          f"📦 <b>Orders</b>\nTotal: {ords} | Today: {o_d}\n\n"
          f"💰 <b>Revenue</b>\nToday: {C.CURRENCY}{float(r_d):.2f}\nWeek: {C.CURRENCY}{float(r_w):.2f}\nAll Time: {C.CURRENCY}{float(rev):.2f}\n\n"
          f"🔑 Stock Available: {stk}\n\n🏆 <b>Top Products:</b>\n")
    for i,p in enumerate(top): text+=f"{i+1}. {p['name']} ({p['cnt']} sold)\n"
    await send(ev,text,kb([[("🔙 Back","admin")]]))

# ══════════════════════════════════════════════
#  📨  COMMAND HANDLERS
# ══════════════════════════════════════════════
@r.message(CommandStart())
async def cmd_start(msg:Message,state:FSMContext):
    await state.clear()
    user=await reg_user(msg.from_user)
    if user["is_banned"]: await msg.answer("🚫 You are banned."); return
    if await DB.cfg("maintenance","0")=="1" and msg.from_user.id not in C.ADMIN_IDS:
        await msg.answer(await DB.cfg("maint_msg","🔧 Maintenance.")); return
    args=msg.text.split(maxsplit=1)[1] if " " in msg.text else ""
    if args.startswith("ref_"):
        rc=args[4:]; ref=await DB.one("SELECT * FROM users WHERE referral_code=?",(rc,))
        if ref and ref["id"]!=user["id"]:
            ex=await DB.one("SELECT id FROM referrals WHERE referred_id=?",(user["id"],))
            if not ex:
                await DB.run("INSERT INTO referrals(referrer_id,referred_id,referral_code) VALUES(?,?,?)",(ref["id"],user["id"],rc))
                await DB.run("UPDATE users SET referred_by=? WHERE id=?",(ref["id"],user["id"]))
                if C.REF_NEW_USER>0:
                    await add_balance(user["id"],C.REF_NEW_USER,"referral_bonus","Welcome bonus!")
                    await msg.answer(f"🎉 Welcome bonus! +{C.CURRENCY}{C.REF_NEW_USER:.2f} added to wallet!")
    elif args.startswith("prod_"):
        pid=int(args[5:])
        user=await DB.one("SELECT * FROM users WHERE id=?",(user["id"],))
        await show_prod(msg,pid,user); return
    user=await DB.one("SELECT * FROM users WHERE id=?",(user["id"],))
    await main_menu(msg,user)

@r.message(Command("menu")) 
async def cmd_menu(msg,state:FSMContext):
    await state.clear(); user=await reg_user(msg.from_user)
    await main_menu(msg,user)
@r.message(Command("shop"))
async def cmd_shop(msg:Message): await show_shop(msg)
@r.message(Command("myorders"))
async def cmd_myorders(msg:Message):
    user=await reg_user(msg.from_user); await show_my_orders(msg,user["id"])
@r.message(Command("balance"))
async def cmd_bal(msg:Message):
    user=await reg_user(msg.from_user); await show_wallet(msg,user)
@r.message(Command("referral"))
async def cmd_ref(msg:Message):
    user=await reg_user(msg.from_user); await show_referral(msg,user)
@r.message(Command("lottery"))
async def cmd_lot(msg:Message):
    user=await reg_user(msg.from_user); await show_lottery(msg,user)
@r.message(Command("support"))
async def cmd_sup(msg:Message): await show_support(msg)
@r.message(Command("profile"))
async def cmd_prof(msg:Message):
    user=await reg_user(msg.from_user); await show_profile(msg,user)
@r.message(Command("wishlist"))
async def cmd_wl(msg:Message):
    user=await reg_user(msg.from_user); await show_wishlist(msg,user["id"])
@r.message(Command("help"))
async def cmd_help(msg:Message): await show_help(msg)
@r.message(Command("admin"))
async def cmd_admin(msg:Message):
    if msg.from_user.id not in C.ADMIN_IDS: return
    await adm_panel(msg)

# ══════════════════════════════════════════════
#  📱  CALLBACK HANDLER
# ══════════════════════════════════════════════
@r.callback_query()
async def on_cb(cb:CallbackQuery,state:FSMContext):
    data=cb.data or ""; parts=data.split(":",1); a=parts[0]; arg=parts[1] if len(parts)>1 else ""
    uid=cb.from_user.id; user=await reg_user(cb.from_user)
    is_adm=uid in C.ADMIN_IDS
    if user["is_banned"] and not is_adm:
        await cb.answer("🚫 You are banned.",show_alert=True); return
    await cb.answer()

    # ── User navigation ────────────────────────────────────────
    if a=="menu": await main_menu(cb,user)
    elif a=="shop": await show_shop(cb)
    elif a=="my_orders": await show_my_orders(cb,uid)
    elif a=="wallet": user=await DB.one("SELECT * FROM users WHERE id=?",(uid,)); await show_wallet(cb,user)
    elif a=="referral": await show_referral(cb,user)
    elif a=="lottery": await show_lottery(cb,user)
    elif a=="wishlist": await show_wishlist(cb,uid)
    elif a=="flash": await show_flash(cb)
    elif a=="support": await show_support(cb)
    elif a=="my_tickets": await show_my_tickets(cb,uid)
    elif a=="profile": await show_profile(cb,user)
    elif a=="help": await show_help(cb)
    elif a=="search_start":
        await state.set_state(S.search)
        await cb.message.answer("🔍 Send a keyword to search:")
    elif a=="noop": pass

    # ── Shop ───────────────────────────────────────────────────
    elif a=="cat": await show_cat(cb,int(arg))
    elif a=="cat_p": cid,pg=arg.split(":"); await show_cat(cb,int(cid),int(pg))
    elif a=="prod": await show_prod(cb,int(arg),user)
    elif a=="checkout": await show_checkout(cb,int(arg),user)
    elif a=="ord_p": await show_my_orders(cb,uid,int(arg))

    # ── Wishlist ───────────────────────────────────────────────
    elif a=="add_wl":
        pid=int(arg)
        ex=await DB.one("SELECT id FROM wishlists WHERE user_id=? AND product_id=?",(uid,pid))
        if not ex:
            await DB.run("INSERT INTO wishlists(user_id,product_id) VALUES(?,?)",(uid,pid))
            await DB.run("UPDATE products SET wishlist_count=wishlist_count+1 WHERE id=?",(pid,))
        await cb.answer("❤️ Added to wishlist!")
        await show_prod(cb,pid,user)
    elif a=="rm_wl":
        pid=int(arg)
        await DB.run("DELETE FROM wishlists WHERE user_id=? AND product_id=?",(uid,pid))
        await DB.run("UPDATE products SET wishlist_count=MAX(0,wishlist_count-1) WHERE id=?",(pid,))
        await cb.answer("💔 Removed"); await show_wishlist(cb,uid)

    # ── Coupon ─────────────────────────────────────────────────
    elif a=="coupon":
        await state.set_state(S.coupon); await state.update_data(oid=arg)
        await cb.message.answer("🎫 Send your coupon code:")

    # ── Payment ────────────────────────────────────────────────
    elif a=="pay_rp":
        oid=arg; order=await DB.one("SELECT * FROM orders WHERE id=?",(oid,))
        if not order: await send(cb,"❌ Order not found."); return
        res=await RP.create(oid,float(order["total_amount"]),uid,order.get("pname",""))
        if not res.get("payment_url"):
            await send(cb,"❌ Payment gateway error. Try again later.\n\nContact: "+await DB.cfg("support","@support")); return
        await DB.run("INSERT OR REPLACE INTO payments(id,order_id,user_id,amount,method,gateway_id,gateway_url,status) VALUES(?,?,?,?,'rupantorpay',?,?,'pending')",
                     (res.get("payment_id",oid),oid,uid,float(order["total_amount"]),res.get("payment_id",""),res["payment_url"]))
        await DB.run("UPDATE orders SET payment_id=? WHERE id=?",(res.get("payment_id",""),oid))
        await send(cb,f"💳 <b>RupantorPay</b>\n\n🆔 <code>{oid}</code>\n💰 <b>{C.CURRENCY}{float(order['total_amount']):.2f}</b>\n\n⬇️ Click to pay:",
                   kb([[("💳 Pay Now",res["payment_url"],"url")],[("✅ I Paid — Check",f"chk_pay:{oid}")],[("❌ Cancel",f"cancel_ord:{oid}")]]))

    elif a=="pay_wal":
        oid=arg; order=await DB.one("SELECT * FROM orders WHERE id=? AND status='pending'",(oid,))
        if not order: await cb.answer("❌ Order not found.",show_alert=True); return
        bal=float(user["balance"])
        if bal<float(order["total_amount"]): await cb.answer(f"❌ Insufficient balance!",show_alert=True); return
        await add_balance(uid,-float(order["total_amount"]),"purchase",f"Order {oid}",oid)
        await DB.run("UPDATE orders SET status='paid',payment_method='wallet' WHERE id=?",(oid,))
        await DB.run("INSERT INTO payments(id,order_id,user_id,amount,method,status,verified) VALUES(?,?,?,?,'wallet','paid',1)",
                     (f"WAL{oid}",oid,uid,float(order["total_amount"])))
        await deliver_order(oid)

    elif a=="chk_pay":
        oid=arg; order=await DB.one("SELECT * FROM orders WHERE id=?",(oid,))
        pay=await DB.one("SELECT * FROM payments WHERE order_id=? ORDER BY created_at DESC LIMIT 1",(oid,))
        if not pay: await send(cb,"❌ No payment found."); return
        verify=await RP.verify(pay["gateway_id"] or oid)
        status=verify.get("status") or (verify.get("data") or {}).get("status","")
        if status in ("paid","success","completed"):
            if order["status"]=="pending":
                await DB.run("UPDATE orders SET status='paid' WHERE id=?",(oid,))
                await deliver_order(oid)
                await send(cb,"✅ <b>Payment Confirmed! Delivering...</b>")
            else:
                await send(cb,f"✅ Order already {order['status']}.")
        else:
            await send(cb,f"⏳ <b>Payment Pending</b>\n🆔 <code>{oid}</code>\nStatus: {status or 'pending'}\n\nWait and check again.",
                       kb([[("🔄 Check Again",f"chk_pay:{oid}"),("💬 Support","open_ticket")]]))

    elif a=="cancel_ord":
        oid=arg; order=await DB.one("SELECT * FROM orders WHERE id=? AND user_id=? AND status='pending'",(oid,uid))
        if order:
            await DB.run("UPDATE orders SET status='cancelled' WHERE id=?",(oid,))
            await send(cb,f"❌ Order <code>{oid}</code> cancelled.",kb([[("🛒 Shop","shop")]]))

    # ── Lottery ────────────────────────────────────────────────
    elif a=="buy_ticket":
        draw=await DB.one("SELECT * FROM lottery_draws WHERE status='open' ORDER BY id DESC LIMIT 1")
        if not draw: await cb.answer("No active draw.",show_alert=True); return
        if float(user["balance"])<C.LOTTERY_PRICE: await cb.answer("❌ Insufficient balance.",show_alert=True); return
        tno=gen_code("",8)
        await add_balance(uid,-C.LOTTERY_PRICE,"lottery_ticket",f"Lottery ticket #{tno}")
        await DB.run("INSERT INTO lottery_tickets(draw_id,user_id,ticket_no,price_paid) VALUES(?,?,?,?)",(draw["id"],uid,tno,C.LOTTERY_PRICE))
        await DB.run("UPDATE lottery_draws SET prize_pool=prize_pool+?,ticket_count=ticket_count+1 WHERE id=?",(C.LOTTERY_PRICE*0.8,draw["id"]))
        await DB.run("UPDATE users SET lottery_tickets=lottery_tickets+1 WHERE id=?",(uid,))
        await cb.answer(f"🎫 Ticket #{tno} bought! Good luck! 🍀",show_alert=True)
        user=await DB.one("SELECT * FROM users WHERE id=?",(uid,)); await show_lottery(cb,user)

    # ── Review ─────────────────────────────────────────────────
    elif a=="review":
        oid=arg; order=await DB.one("SELECT * FROM orders WHERE id=? AND user_id=? AND status='delivered'",(oid,uid))
        if not order or order["is_reviewed"]: await cb.answer("❌ Cannot review.",show_alert=True); return
        await state.set_state(S.review_rating); await state.update_data(oid=oid,pid=order["product_id"])
        await cb.message.answer("⭐ Rate your purchase:",
                                reply_markup=kb([[("⭐1","rate:1"),("⭐⭐2","rate:2"),("⭐⭐⭐3","rate:3"),("⭐⭐⭐⭐4","rate:4"),("⭐⭐⭐⭐⭐5","rate:5")]]))

    elif a=="rate":
        await state.update_data(rating=int(arg)); await state.set_state(S.review_text)
        await cb.message.edit_text(f"{'⭐'*int(arg)} Rating saved!\n\nWrite your review:")

    elif a=="reviews":
        pid=int(arg)
        revs=await DB.all("SELECT r.*,u.first_name FROM reviews r LEFT JOIN users u ON r.user_id=u.id WHERE r.product_id=? AND r.is_approved=1 ORDER BY r.created_at DESC LIMIT 10",(pid,))
        prod=await DB.one("SELECT name FROM products WHERE id=?",(pid,))
        text=f"⭐ <b>Reviews — {prod['name']}</b>\n\n"
        if not revs: text+="No reviews yet. Be the first!"
        else:
            for rv in revs:
                stars="⭐"*rv["rating"]
                text+=f"{stars} <b>{rv['first_name'] or 'User'}</b>\n{rv['body']}\n{fmt_date(rv['created_at'])}\n\n"
        await send(cb,text,kb([[("🔙 Back",f"prod:{pid}")]]))

    # ── Tickets ────────────────────────────────────────────────
    elif a=="open_ticket":
        await state.set_state(S.ticket_sub)
        await cb.message.answer("🎫 <b>New Ticket</b>\n\nWhat is your issue? (Subject):")
    elif a=="view_tkt":
        tkt=await DB.one("SELECT * FROM tickets WHERE id=? AND user_id=?",(int(arg),uid))
        if not tkt: await send(cb,"❌ Not found."); return
        msgs=await DB.all("SELECT * FROM ticket_messages WHERE ticket_id=? ORDER BY created_at ASC LIMIT 20",(int(arg),))
        text=f"🎫 <b>{tkt['ticket_no']}</b>\n📌 {tkt['subject']}\n🚦 {tkt['status']}\n\n━━━━━━━━━━━━\n"
        for m in msgs:
            who="🔧 Support" if m["is_admin"] else "👤 You"
            text+=f"\n{who} ({fmt_date(m['created_at'])}):\n{m['message']}\n"
        rows=[]
        if tkt["status"]!="closed": rows.append([("💬 Reply",f"tkt_reply:{tkt['id']}")])
        rows.append([("🔙 Back","my_tickets")]); await send(cb,text,kb(rows))
    elif a=="tkt_reply":
        await state.set_state(S.ticket_reply); await state.update_data(tid=int(arg))
        await cb.message.answer("💬 Send your reply:")

    # ── Admin ───────────────────────────────────────────────────
    elif a=="admin" and is_adm: await adm_panel(cb)
    elif a=="adm_prods" and is_adm: await adm_prods(cb)
    elif a=="adm_ords" and is_adm: await adm_ords(cb)
    elif a=="adm_users" and is_adm: await adm_users(cb)
    elif a=="adm_stats" and is_adm: await adm_stats(cb)

    elif a=="adm_add_prod" and is_adm:
        await state.set_state(S.a_prod_name)
        await cb.message.answer("➕ <b>Add Product</b>\n\nProduct name:")

    elif a=="adm_stock" and is_adm:
        pid=int(arg); await state.set_state(S.a_stock_keys); await state.update_data(pid=pid)
        prod=await DB.one("SELECT name FROM products WHERE id=?",(pid,))
        await cb.message.answer(f"📦 Add stock to <b>{prod['name']}</b>\n\nSend keys, one per line:")

    elif a=="adm_delprod" and is_adm:
        await DB.run("UPDATE products SET is_active=0 WHERE id=?",(int(arg),))
        await cb.answer("🗑️ Deleted",show_alert=True); await adm_prods(cb)

    elif a=="adm_tog" and is_adm:
        p=await DB.one("SELECT is_active FROM products WHERE id=?",(int(arg),))
        await DB.run("UPDATE products SET is_active=? WHERE id=?",(1-p["is_active"],int(arg)))
        await cb.answer("✅ Toggled"); await adm_prods(cb)

    elif a=="adm_user" and is_adm:
        u=await DB.one("SELECT * FROM users WHERE id=?",(int(arg),))
        if not u: await send(cb,"❌ Not found."); return
        text=(f"👤 <b>User #{u['id']}</b>\n🆔 <code>{u['id']}</code> @{u['username']}\n"
              f"💰 {C.CURRENCY}{float(u['balance']):.2f} | 💳 {C.CURRENCY}{float(u['total_spent']):.2f}\n"
              f"📦 {u['total_orders']} orders | 💎 {u['vip_level']}\n"
              f"🚫 Banned: {'Yes — '+u['ban_reason'] if u['is_banned'] else 'No'}")
        bb=("✅ Unban",f"adm_unban:{u['id']}") if u["is_banned"] else ("🚫 Ban",f"adm_ban:{u['id']}")
        await send(cb,text,kb([[("💰 Add Balance",f"adm_addbal:{u['id']}")],[bb],[("🔙 Users","adm_users")]]))

    elif a=="adm_ban" and is_adm:
        await DB.run("UPDATE users SET is_banned=1,ban_reason='Banned by admin' WHERE id=?",(int(arg),))
        await bot.send_message(int(arg),"🚫 You have been banned. Contact support.")
        await cb.answer("🚫 Banned",show_alert=True); await adm_users(cb)

    elif a=="adm_unban" and is_adm:
        await DB.run("UPDATE users SET is_banned=0,ban_reason='' WHERE id=?",(int(arg),))
        await bot.send_message(int(arg),"✅ Your ban has been lifted. Welcome back!")
        await cb.answer("✅ Unbanned",show_alert=True)

    elif a=="adm_addbal" and is_adm:
        await state.set_state(S.a_bal_uid); await state.update_data(uid=int(arg))
        await cb.message.answer(f"💰 Add balance to #{arg}\n\nSend amount:")

    elif a=="adm_ord" and is_adm:
        oid=arg; o=await DB.one("SELECT o.*,p.name as pn FROM orders o LEFT JOIN products p ON o.product_id=p.id WHERE o.id=?",(oid,))
        u=await DB.one("SELECT username FROM users WHERE id=?",(o["user_id"],))
        text=(f"📋 <b>Order {oid}</b>\n\n👤 @{u['username']} ({o['user_id']})\n"
              f"📦 {o['pn']}\n💰 {C.CURRENCY}{float(o['total_amount']):.2f}\n"
              f"📲 {o['payment_method']}\n🚦 {o['status']}\n📅 {fmt_date(o['created_at'])}")
        if o["delivery_data"]: text+=f"\n\n🔑 <pre>{o['delivery_data']}</pre>"
        rows=[]
        if o["status"] in ("pending","pending_manual","paid"): rows.append([("📤 Deliver Now",f"adm_deliver:{oid}")])
        if o["status"]=="delivered": rows.append([("💸 Refund",f"adm_refund:{oid}")])
        rows.append([("🔙 Orders","adm_ords")]); await send(cb,text,kb(rows))

    elif a=="adm_deliver" and is_adm:
        await deliver_order(arg); await cb.answer("✅ Delivering...",show_alert=False)
        o=await DB.one("SELECT status FROM orders WHERE id=?",(arg,))
        await send(cb,f"📋 Order {arg}\n🚦 Status: {o['status']}",kb([[("🔙 Orders","adm_ords")]]))

    elif a=="adm_refund" and is_adm:
        await state.set_state(S.a_refund_amt); await state.update_data(oid=arg)
        o=await DB.one("SELECT total_amount FROM orders WHERE id=?",(arg,))
        await cb.message.answer(f"💸 Refund order {arg}\nTotal: {C.CURRENCY}{float(o['total_amount']):.2f}\n\nSend amount (or 'all'):")

    elif a=="adm_bcast" and is_adm:
        await send(cb,"📢 <b>Broadcast</b>\n\nChoose target:",
                   kb([[("👥 All Users","bc_all"),("💎 VIP Only","bc_vip")],[("❌ Cancel","admin")]]))
    elif a=="bc_all" and is_adm:
        cnt=await DB.val("SELECT COUNT(*) FROM users WHERE is_banned=0")
        await state.set_state(S.a_broadcast); await state.update_data(target="all")
        await cb.message.answer(f"📢 Send message to <b>{cnt}</b> users:")
    elif a=="bc_vip" and is_adm:
        cnt=await DB.val("SELECT COUNT(*) FROM users WHERE is_banned=0 AND vip_level!='none'")
        await state.set_state(S.a_broadcast); await state.update_data(target="vip")
        await cb.message.answer(f"📢 Send message to <b>{cnt}</b> VIP users:")

    elif a=="adm_coupons" and is_adm:
        cps=await DB.all("SELECT * FROM coupons ORDER BY id DESC LIMIT 20")
        text="🎫 <b>Coupons</b>\n\n"; rows=[[("➕ Add Coupon","adm_add_coupon")]]
        for c in cps:
            s="✅" if c["is_active"] else "❌"
            d=f"{c['discount_value']}%" if c["discount_type"]=="percent" else f"{C.CURRENCY}{c['discount_value']}"
            text+=f"{s} <code>{c['code']}</code> — {d} | Used:{c['used_count']}\n"
            rows.append([(f"🗑️ {c['code']}",f"adm_delcoup:{c['id']}")])
        rows.append([("🔙 Back","admin")]); await send(cb,text,kb(rows))
    elif a=="adm_add_coupon" and is_adm:
        await state.set_state(S.a_coupon)
        await cb.message.answer("🎫 Format: <code>CODE VALUE [percent|fixed]</code>\nExample: <code>SAVE20 20 percent</code>")
    elif a=="adm_delcoup" and is_adm:
        await DB.run("UPDATE coupons SET is_active=0 WHERE id=?",(int(arg),))
        await cb.answer("🗑️ Deleted")

    elif a=="adm_flash" and is_adm:
        sales=await DB.all("SELECT fs.*,p.name FROM flash_sales fs JOIN products p ON fs.product_id=p.id ORDER BY id DESC LIMIT 10")
        text="⚡ <b>Flash Sales</b>\n\n"; rows=[[("➕ Add Flash Sale","adm_add_flash")]]
        for s in sales:
            active="⚡" if s["is_active"] and s["ends_at"]>ts() else "❌"
            disc=round((1-float(s["sale_price"])/float(s["original_price"]))*100)
            text+=f"{active} {s['name']} — {disc}% off | Ends:{fmt_date(s['ends_at'])}\n"
        rows.append([("🔙 Back","admin")]); await send(cb,text,kb(rows))
    elif a=="adm_add_flash" and is_adm:
        prods=await DB.all("SELECT id,name,price FROM products WHERE is_active=1 LIMIT 20")
        rows=[[( f"{p['name']} ({C.CURRENCY}{p['price']})",f"flash_pick:{p['id']}:{p['price']}")] for p in prods]
        rows.append([("❌ Cancel","adm_flash")]); await send(cb,"⚡ Select product:",kb(rows))
    elif a=="flash_pick" and is_adm:
        pid,op=arg.split(":")
        await state.set_state(S.a_flash_price); await state.update_data(fpid=int(pid),forig=float(op))
        await cb.message.answer(f"⚡ Original: {C.CURRENCY}{op}\n\nEnter SALE price:")

    elif a=="adm_lottery" and is_adm:
        draw=await DB.one("SELECT * FROM lottery_draws WHERE status='open' ORDER BY id DESC LIMIT 1")
        if not draw:
            num=(await DB.val("SELECT MAX(draw_number) FROM lottery_draws") or 0)+1
            await DB.run("INSERT INTO lottery_draws(draw_number,prize_pool,draw_at) VALUES(?,?,?)",(num,C.LOTTERY_POOL,ts()+86400))
            draw=await DB.one("SELECT * FROM lottery_draws WHERE status='open' ORDER BY id DESC LIMIT 1")
        await send(cb,f"🎰 <b>Lottery Admin</b>\n\nDraw #{draw['draw_number']}\nPrize: {C.CURRENCY}{float(draw['prize_pool']):.2f}\nTickets: {draw['ticket_count']}",
                   kb([[("🎰 Draw Winner Now",f"adm_draw:{draw['id']}")],[("🔙 Back","admin")]]))
    elif a=="adm_draw" and is_adm:
        draw=await DB.one("SELECT * FROM lottery_draws WHERE id=? AND status='open'",(int(arg),))
        if not draw: await send(cb,"❌ Draw not found."); return
        tkts=await DB.all("SELECT * FROM lottery_tickets WHERE draw_id=?",(int(arg),))
        if not tkts: await send(cb,"❌ No tickets sold."); return
        winner=random.choice(tkts); prize=float(draw["prize_pool"])
        await DB.run("UPDATE lottery_draws SET status='drawn',winner_id=?,winner_ticket=?,drawn_at=? WHERE id=?",(winner["user_id"],winner["ticket_no"],ts(),int(arg)))
        await DB.run("UPDATE lottery_tickets SET is_winner=1,prize_amount=? WHERE id=?",(prize,winner["id"]))
        await add_balance(winner["user_id"],prize,"lottery_win",f"Lottery #{draw['draw_number']} winner!")
        await DB.run("UPDATE users SET lottery_wins=lottery_wins+1 WHERE id=?",(winner["user_id"],))
        await bot.send_message(winner["user_id"],f"🎰🎉 <b>YOU WON THE LOTTERY!</b>\n\nDraw #{draw['draw_number']}\nTicket: <code>{winner['ticket_no']}</code>\nPrize: <b>{C.CURRENCY}{prize:.2f}</b> added to wallet!")
        await send(cb,f"🎰 <b>Draw Done!</b>\n\n🏆 Winner: <code>{winner['user_id']}</code>\n🎫 {winner['ticket_no']}\n💰 {C.CURRENCY}{prize:.2f}",kb([[("🔙 Back","admin")]]))

    elif a=="adm_tickets" and is_adm:
        tkts=await DB.all("SELECT t.*,u.username FROM tickets t JOIN users u ON t.user_id=u.id WHERE t.status!='closed' ORDER BY t.created_at DESC LIMIT 15")
        text="🎫 <b>Open Tickets</b>\n\n"; rows=[]
        for t in tkts:
            p={"high":"🔴","normal":"🟡"}.get(t["priority"],"🟢")
            text+=f"{p} <code>{t['ticket_no']}</code> @{t['username']} — {t['subject']}\n"
            rows.append([(f"💬 Reply {t['ticket_no']}",f"adm_tkt_reply:{t['id']}"),(f"✅ Close",f"adm_tkt_close:{t['id']}")])
        if not tkts: text+="No open tickets! 🎉"
        rows.append([("🔙 Back","admin")]); await send(cb,text,kb(rows))
    elif a=="adm_tkt_reply" and is_adm:
        await state.set_state(S.a_ticket_reply); await state.update_data(tid=int(arg))
        await cb.message.answer("💬 Send your reply:")
    elif a=="adm_tkt_close" and is_adm:
        tkt=await DB.one("SELECT * FROM tickets WHERE id=?",(int(arg),))
        await DB.run("UPDATE tickets SET status='closed' WHERE id=?",(int(arg),))
        await bot.send_message(tkt["user_id"],f"✅ Ticket {tkt['ticket_no']} closed. Thank you!")
        await cb.answer("✅ Closed"); await adm_panel(cb)

    elif a=="adm_settings" and is_adm:
        keys=[("welcome","Welcome Msg"),("support","Support Username"),("low_stock","Low Stock Alert"),
              ("maintenance","Maintenance (0/1)"),("maint_msg","Maintenance Msg"),("affiliate_rate","Affiliate %"),
              ("review_reward","Review Reward"),("auto_deliver","Auto Deliver (0/1)"),("show_stock","Show Stock (0/1)")]
        text="⚙️ <b>Settings</b>\n\n"; rows=[]
        for k,label in keys:
            v=await DB.cfg(k,"—"); short=v[:25]+"..." if len(v)>25 else v
            text+=f"🔹 <b>{label}</b>: <code>{short}</code>\n"
            rows.append([(f"✏️ {label}",f"adm_set:{k}")])
        rows.append([("🔙 Back","admin")]); await send(cb,text,kb(rows))
    elif a=="adm_set" and is_adm:
        await state.set_state(S.a_setting_val); await state.update_data(skey=arg)
        cur=await DB.cfg(arg,""); await cb.message.answer(f"⚙️ <b>Edit: {arg}</b>\nCurrent: <code>{cur}</code>\n\nSend new value:")

    elif a=="adm_man_del" and is_adm:
        await state.set_state(S.a_manual_del)
        await cb.message.answer("📤 Send order ID to deliver:")

    elif a=="adm_maint" and is_adm:
        cur=await DB.cfg("maintenance","0"); new="0" if cur=="1" else "1"
        await DB.set_cfg("maintenance",new)
        await cb.answer(f"{'🔧 Maintenance ON' if new=='1' else '✅ Maintenance OFF'}",show_alert=True)
        await adm_panel(cb)

    # ── Pick category during add product ──────────────────────
    elif a=="pick_cat" and is_adm:
        await state.update_data(pcat=int(arg)); await state.set_state(S.a_prod_desc)
        await cb.message.edit_text("📝 Product description:")

# ══════════════════════════════════════════════
#  📨  FSM HANDLERS
# ══════════════════════════════════════════════
# User FSM
@r.message(S.search)
async def fsm_search(msg:Message,state:FSMContext):
    await state.clear(); q=msg.text.strip()
    prods=await DB.all("SELECT * FROM products WHERE is_active=1 AND (name LIKE ? OR description LIKE ?) LIMIT 20",(f"%{q}%",f"%{q}%"))
    text=f"🔍 <b>Results for \"{q}\"</b>\n\n"; rows=[]
    if not prods: text+="No products found."
    else:
        for p in prods:
            stk=await DB.val("SELECT COUNT(*) FROM product_keys WHERE product_id=? AND status='available'",(p["id"],))
            rows.append([(f"{p['name']} — {C.CURRENCY}{p['price']:.2f} (Stock:{stk})",f"prod:{p['id']}")])
    rows.append([("🔍 Search Again","search_start"),("🛒 Shop","shop")])
    await msg.answer(text,reply_markup=kb(rows),parse_mode="HTML")

@r.message(S.coupon)
async def fsm_coupon(msg:Message,state:FSMContext):
    d=await state.get_data(); await state.clear()
    oid=d.get("oid",""); order=await DB.one("SELECT * FROM orders WHERE id=?",(oid,))
    if not order: await msg.answer("❌ Order not found."); return
    c=await DB.one("SELECT * FROM coupons WHERE code=? AND is_active=1",(msg.text.strip().upper(),))
    if not c: await msg.answer("❌ Invalid coupon."); return
    used=await DB.val("SELECT COUNT(*) FROM coupon_usage WHERE coupon_id=? AND user_id=?",(c["id"],msg.from_user.id))
    ok=(not c["per_user_limit"] or used<c["per_user_limit"]) and (not c["usage_limit"] or c["used_count"]<c["usage_limit"])
    if not ok: await msg.answer("❌ Coupon limit reached."); return
    discount=float(order["total_amount"])*c["discount_value"]/100 if c["discount_type"]=="percent" else min(c["discount_value"],float(order["total_amount"]))
    await msg.answer(f"✅ Coupon applied! Saved {C.CURRENCY}{discount:.2f}")
    user=await DB.one("SELECT * FROM users WHERE id=?",(msg.from_user.id,))
    await show_checkout(msg,order["product_id"],user,msg.text.strip().upper())

@r.message(S.ticket_sub)
async def fsm_tkt_sub(msg:Message,state:FSMContext):
    await state.update_data(tsub=msg.text); await state.set_state(S.ticket_msg)
    await msg.answer("📝 Describe your issue in detail:")

@r.message(S.ticket_msg)
async def fsm_tkt_msg(msg:Message,state:FSMContext):
    d=await state.get_data(); await state.clear()
    sub=d.get("tsub","Support Request")
    no="TKT"+gen_code("",8)
    await DB.run("INSERT INTO tickets(ticket_no,user_id,subject) VALUES(?,?,?)",(no,msg.from_user.id,sub))
    tid=await DB.val("SELECT id FROM tickets WHERE ticket_no=?",(no,))
    await DB.run("INSERT INTO ticket_messages(ticket_id,sender_id,message) VALUES(?,?,?)",(tid,msg.from_user.id,msg.text))
    for aid in C.ADMIN_IDS:
        await bot.send_message(aid,f"🎫 <b>New Ticket!</b>\n\n🔖 {no}\n👤 {msg.from_user.id} @{msg.from_user.username}\n📌 {sub}\n\n{msg.text}",
                               reply_markup=kb([[("💬 Reply",f"adm_tkt_reply:{tid}"),("✅ Close",f"adm_tkt_close:{tid}")]]))
    await msg.answer(f"✅ <b>Ticket Created!</b>\n🔖 <code>{no}</code>\n\nWe'll reply soon!",
                     reply_markup=kb([[("📋 My Tickets","my_tickets"),("🔙 Menu","menu")]]))

@r.message(S.ticket_reply)
async def fsm_tkt_reply(msg:Message,state:FSMContext):
    d=await state.get_data(); await state.clear(); tid=d.get("tid",0)
    tkt=await DB.one("SELECT * FROM tickets WHERE id=?",(tid,))
    if not tkt: await msg.answer("❌ Ticket not found."); return
    await DB.run("INSERT INTO ticket_messages(ticket_id,sender_id,message) VALUES(?,?,?)",(tid,msg.from_user.id,msg.text))
    await DB.run("UPDATE tickets SET updated_at=? WHERE id=?",(ts(),tid))
    for aid in C.ADMIN_IDS:
        await bot.send_message(aid,f"💬 User reply on {tkt['ticket_no']}:\n\n{msg.text}",
                               reply_markup=kb([[("💬 Reply",f"adm_tkt_reply:{tid}")]]))
    await msg.answer("✅ Reply sent!")

@r.message(S.review_text)
async def fsm_review(msg:Message,state:FSMContext):
    d=await state.get_data(); await state.clear()
    oid=d.get("oid",""); pid=d.get("pid",0); rating=d.get("rating",5)
    await DB.run("INSERT INTO reviews(product_id,user_id,order_id,rating,body) VALUES(?,?,?,?,?)",(pid,msg.from_user.id,oid,rating,msg.text))
    avg=await DB.val("SELECT AVG(rating) FROM reviews WHERE product_id=? AND is_approved=1",(pid,))
    cnt=await DB.val("SELECT COUNT(*) FROM reviews WHERE product_id=? AND is_approved=1",(pid,))
    await DB.run("UPDATE products SET rating=?,review_count=? WHERE id=?",(avg or 0,cnt or 0,pid))
    await DB.run("UPDATE orders SET is_reviewed=1 WHERE id=?",(oid,))
    reward=float(await DB.cfg("review_reward","0"))
    if reward>0:
        await add_balance(msg.from_user.id,reward,"review_reward",f"Review reward")
        await msg.answer(f"✅ Review submitted!\n🎁 Reward: +{C.CURRENCY}{reward:.2f}")
    else:
        await msg.answer(f"✅ Review submitted! {'⭐'*rating}\nThank you!")

# Admin FSM
@r.message(S.a_prod_name)
async def fsm_pname(msg:Message,state:FSMContext):
    await state.update_data(pname=msg.text); await state.set_state(S.a_prod_price)
    await msg.answer("💰 Price (BDT):")

@r.message(S.a_prod_price)
async def fsm_pprice(msg:Message,state:FSMContext):
    if not msg.text.replace(".","").isdigit(): await msg.answer("❌ Invalid price."); return
    await state.update_data(pprice=float(msg.text)); await state.set_state(S.a_prod_cat)
    cats=await DB.all("SELECT * FROM categories WHERE is_active=1")
    rows=[[( f"{c['emoji']} {c['name']}",f"pick_cat:{c['id']}")] for c in cats]
    await msg.answer("📁 Choose category:",reply_markup=kb(rows))

@r.message(S.a_prod_desc)
async def fsm_pdesc(msg:Message,state:FSMContext):
    await state.update_data(pdesc=msg.text); await state.set_state(S.a_prod_stock)
    await msg.answer("📦 Add stock keys (one per line) or type SKIP:")

@r.message(S.a_prod_stock)
async def fsm_pstock(msg:Message,state:FSMContext):
    d=await state.get_data(); await state.clear()
    keys=[] if msg.text=="SKIP" else [k.strip() for k in msg.text.split("\n") if k.strip()]
    pid=await DB.ins("INSERT INTO products(name,description,price,category_id,stock_count,is_active,created_by) VALUES(?,?,?,?,?,1,?)",
                     (d["pname"],d.get("pdesc",""),d["pprice"],d.get("pcat",1),len(keys),msg.from_user.id))
    for k in keys:
        await DB.run("INSERT INTO product_keys(product_id,key_value,added_by) VALUES(?,?,?)",(pid,k,msg.from_user.id))
    await msg.answer(f"✅ <b>Product Created!</b>\n\n🔹 {d['pname']}\n💰 {C.CURRENCY}{d['pprice']}\n📦 {len(keys)} keys\n🆔 #{pid}")

@r.message(S.a_stock_keys)
async def fsm_skeys(msg:Message,state:FSMContext):
    d=await state.get_data(); await state.clear(); pid=d.get("pid",0)
    keys=[k.strip() for k in msg.text.split("\n") if k.strip()]
    for k in keys:
        await DB.run("INSERT INTO product_keys(product_id,key_value,added_by) VALUES(?,?,?)",(pid,k,msg.from_user.id))
    await DB.run("UPDATE products SET stock_count=stock_count+? WHERE id=?",(len(keys),pid))
    stk=await DB.val("SELECT stock_count FROM products WHERE id=?",(pid,))
    await msg.answer(f"✅ Added <b>{len(keys)}</b> keys!\nTotal stock: <b>{stk}</b>")

@r.message(S.a_broadcast)
async def fsm_bc(msg:Message,state:FSMContext):
    d=await state.get_data(); await state.clear(); target=d.get("target","all")
    cond="AND vip_level!='none'" if target=="vip" else ""
    users=await DB.all(f"SELECT id FROM users WHERE is_banned=0 {cond}")
    sent=0; failed=0
    for u in users:
        try:
            await bot.send_message(u["id"],msg.text,parse_mode="HTML")
            sent+=1; await asyncio.sleep(0.04)
        except: failed+=1
    await DB.run("INSERT INTO broadcasts(message,target,sent,failed,created_by) VALUES(?,?,?,?,?)",
                 (msg.text,target,sent,failed,msg.from_user.id))
    await msg.answer(f"📢 <b>Broadcast Done!</b>\n✅ Sent: {sent}\n❌ Failed: {failed}\n👥 Total: {len(users)}")

@r.message(S.a_bal_uid)
async def fsm_bal(msg:Message,state:FSMContext):
    d=await state.get_data(); uid=d.get("uid",0)
    try: amt=float(msg.text)
    except: await msg.answer("❌ Invalid amount."); return
    await state.clear()
    await add_balance(uid,amt,"admin_credit","Added by admin","",msg.from_user.id)
    await bot.send_message(uid,f"💰 Admin added {C.CURRENCY}{amt:.2f} to your wallet!")
    await msg.answer(f"✅ Added {C.CURRENCY}{amt:.2f} to user #{uid}")

@r.message(S.a_setting_val)
async def fsm_sval(msg:Message,state:FSMContext):
    d=await state.get_data(); await state.clear()
    await DB.set_cfg(d.get("skey",""),msg.text)
    await msg.answer(f"✅ Setting updated!")

@r.message(S.a_ticket_reply)
async def fsm_atkt(msg:Message,state:FSMContext):
    d=await state.get_data(); await state.clear(); tid=d.get("tid",0)
    tkt=await DB.one("SELECT * FROM tickets WHERE id=?",(tid,))
    if not tkt: await msg.answer("❌ Not found."); return
    await DB.run("INSERT INTO ticket_messages(ticket_id,sender_id,is_admin,message) VALUES(?,?,1,?)",(tid,msg.from_user.id,msg.text))
    await DB.run("UPDATE tickets SET updated_at=? WHERE id=?",(ts(),tid))
    await bot.send_message(tkt["user_id"],f"💬 <b>Support Reply</b>\n\n🔖 {tkt['ticket_no']}\n\n{msg.text}",
                           reply_markup=kb([[("💬 Reply",f"tkt_reply:{tid}")]]))
    await msg.answer("✅ Reply sent!")

@r.message(S.a_flash_price)
async def fsm_fprice(msg:Message,state:FSMContext):
    if not msg.text.replace(".","").isdigit(): await msg.answer("❌ Invalid price."); return
    await state.update_data(fprice=float(msg.text)); await state.set_state(S.a_flash_hrs)
    await msg.answer("⏰ Duration in hours (e.g. 24):")

@r.message(S.a_flash_hrs)
async def fsm_fhrs(msg:Message,state:FSMContext):
    if not msg.text.isdigit(): await msg.answer("❌ Invalid hours."); return
    d=await state.get_data(); await state.clear()
    pid=d["fpid"]; orig=d["forig"]; sale=d["fprice"]; hrs=int(msg.text)
    ends=ts()+hrs*3600; prod=await DB.one("SELECT name FROM products WHERE id=?",(pid,))
    await DB.run("INSERT INTO flash_sales(product_id,sale_name,original_price,sale_price,starts_at,ends_at,is_active,created_by) VALUES(?,?,?,?,?,?,1,?)",
                 (pid,f"Flash — {prod['name']}",orig,sale,ts(),ends,msg.from_user.id))
    disc=round((1-sale/orig)*100)
    await msg.answer(f"✅ Flash sale!\n⚡ {prod['name']}\n{C.CURRENCY}{sale} (-{disc}%)\n⏰ {hrs} hours")

@r.message(S.a_coupon)
async def fsm_coup(msg:Message,state:FSMContext):
    await state.clear(); parts=msg.text.strip().split()
    if len(parts)<2: await msg.answer("❌ Format: CODE VALUE [percent|fixed]"); return
    code=parts[0].upper(); value=float(parts[1]); type_=parts[2] if len(parts)>2 else "percent"
    if type_ not in ("percent","fixed"): type_="percent"
    await DB.run("INSERT OR IGNORE INTO coupons(code,discount_type,discount_value,per_user_limit,is_active,created_by) VALUES(?,?,?,1,1,?)",
                 (code,type_,value,msg.from_user.id))
    await msg.answer(f"✅ Coupon <code>{code}</code> created!\nType: {type_} | Value: {value}")

@r.message(S.a_manual_del)
async def fsm_mandel(msg:Message,state:FSMContext):
    await state.clear(); oid=msg.text.strip()
    await deliver_order(oid); await msg.answer(f"✅ Delivering order {oid}...")

@r.message(S.a_refund_amt)
async def fsm_refund(msg:Message,state:FSMContext):
    d=await state.get_data(); await state.clear(); oid=d.get("oid","")
    order=await DB.one("SELECT * FROM orders WHERE id=?",(oid,))
    if not order: await msg.answer("❌ Not found."); return
    amt=float(order["total_amount"]) if msg.text.lower()=="all" else float(msg.text)
    await add_balance(order["user_id"],amt,"refund",f"Refund for {oid}",oid,msg.from_user.id)
    await DB.run("UPDATE orders SET status='refunded',refund_amount=? WHERE id=?",(amt,oid))
    await bot.send_message(order["user_id"],f"💸 <b>Refund!</b>\n🆔 {oid}\n{C.CURRENCY}{amt:.2f} added to wallet!")
    await msg.answer(f"✅ Refunded {C.CURRENCY}{amt:.2f} for order {oid}")

# Default
@r.message()
async def fallback(msg:Message,state:FSMContext):
    user=await reg_user(msg.from_user)
    if user["is_banned"]: await msg.answer("🚫 You are banned."); return
    if await DB.cfg("maintenance","0")=="1" and msg.from_user.id not in C.ADMIN_IDS:
        await msg.answer(await DB.cfg("maint_msg","🔧 Maintenance.")); return
    user=await DB.one("SELECT * FROM users WHERE id=?",(user["id"],))
    await main_menu(msg,user)

# ══════════════════════════════════════════════
#  🚀  MAIN
# ══════════════════════════════════════════════
async def main():
    await DB.init()
    await bot.set_my_commands([
        BotCommand(command="start",    description="Main menu"),
        BotCommand(command="shop",     description="Browse products"),
        BotCommand(command="myorders", description="My orders"),
        BotCommand(command="balance",  description="My wallet"),
        BotCommand(command="referral", description="Referral program"),
        BotCommand(command="lottery",  description="Lottery"),
        BotCommand(command="support",  description="Support"),
        BotCommand(command="profile",  description="My profile"),
        BotCommand(command="wishlist", description="My wishlist"),
        BotCommand(command="help",     description="Help & FAQ"),
    ])
    log.info(f"🚀 {C.SHOP_NAME} Bot Started! Polling...")
    await dp.start_polling(bot, allowed_updates=["message","callback_query"])

if __name__=="__main__":
    asyncio.run(main())
