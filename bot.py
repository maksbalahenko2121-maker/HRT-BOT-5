import asyncio

import logging

import random

import sqlite3

import time

from datetime import datetime

from urllib.parse import quote

from aiogram import Bot, Dispatcher, F, types

from aiogram.filters import Command

from aiogram.types import (

    InlineKeyboardMarkup,

    InlineKeyboardButton,

    ReplyKeyboardMarkup,

    KeyboardButton,

    LabeledPrice,

    PreCheckoutQuery,

    BotCommand,

    InputMediaPhoto,

    FSInputFile,

)

 

logging.basicConfig(level=logging.INFO)

 

BOT_TOKEN = "9297074957:AAHH0SfGcccDMoJE0a4XuPRrAI1aa97UvGk"

ADMIN_ID = 6921885296

BOT_USERNAME = "AnimeEnergNFTBot"

COOLDOWN = 3 * 3600

 

BANNERS = {

    "welcome": "",

    "shop": "",

    "levels": "",

    "top": "",

}

 

LEVELS = {

    1: {"name": "Наруто (Генин на минималках)", "need": 250, "reward": "Мишка (15 ⭐)", "photo": "AgACAgIAAxkBAAMxavmpcpkyR321bXlTcO03f0kLewYAAjweaxuKkshLF3b_juZ9rVIBAAMCAAN4AAM9BA"},

    2: {"name": "Танджиро (Угольный барон)", "need": 1000, "reward": "Кольцо (100 ⭐)", "photo": "AgACAgIAAxkBAAMzavmpev7gL0gD-vQSk67j96d0wv0AAj0eaxuKkshL00Zu3USVDb8BAAMCAAN5AAM9BA"},

    3: {"name": "Годжо Сатору (Без повязки)", "need": 3000, "reward": "NFT Pet Snake", "photo": "AgACAgIAAxkBAAM1avmpfkYMtA3verNLxRV7Tzo7liwAAj4eaxuKkshLL-zRwHyaDIgBAAMCAAN5AAM9BA"},

    4: {"name": "Итачи Учиха (Мастер яичницы)", "need": 5000, "reward": "NFT Input Key", "photo": "AgACAgIAAxkBAAM3avmpg_3ZLkv5F-4cuC3KuHTe794AAj8eaxuKkshLnTXQ_6BWI3oBAAMCAAN5AAM9BA"},

    5: {"name": "Сейлор Мун (В поисках обеда)", "need": 7500, "reward": "NFT Moon Pendant", "photo": "AgACAgIAAxkBAAM5avmpiJYXaFcLGINflYIF8kJk4kAAAkAeaxuKkshLXfUwICm8tfQBAAMCAAN5AAM9BA"},

    6: {"name": "Аня Форджер (Агент Сумрак-младший)", "need": 11000, "reward": "NFT Spy Agaric", "photo": "AgACAgIAAxkBAAM7avmpi2Kb1l36v_sHCfmFpXno8kkAAkEeaxuKkshLp4-8UNuOrlABAAMCAAN5AAM9BA"},

    7: {"name": "Саске Учиха (Мститель на диете)", "need": 15000, "reward": "NFT Easter Egg", "photo": ""},

    8: {"name": "Зеницу (Спящий гром)", "need": 19000, "reward": "NFT Whip Cupcake", "photo": ""},

    9: {"name": "Иноске (Кабан без тормозов)", "need": 23000, "reward": "NFT Snoop Cigar", "photo": ""},

    10: {"name": "Какаши (Читатель 18+)", "need": 27500, "reward": "NFT Lunar Snake", "photo": ""},

    11: {"name": "Луффи (Резиновый обжора)", "need": 32500, "reward": "NFT Jolly Chimp", "photo": ""},

    12: {"name": "Зоро (Потерялся в меню)", "need": 37500, "reward": "NFT Homemade Cake", "photo": ""},

    13: {"name": "Санджи (Шеф-повар Конохи)", "need": 43000, "reward": "NFT Spicy Scroll", "photo": ""},

    14: {"name": "Ичиго (Рыжий жнец)", "need": 49000, "reward": "NFT Jingle Bells", "photo": ""},

    15: {"name": "Сайтама (Лысый со скидкой)", "need": 55000, "reward": "NFT Party Sparkler", "photo": ""},

    16: {"name": "Генос (Киборг-пылесос)", "need": 62500, "reward": "NFT Santa Hat", "photo": ""},

    17: {"name": "Леви Аккерман (Мистер Пропер)", "need": 70000, "reward": "NFT Ginger Cookie", "photo": ""},

    18: {"name": "Эрен Йегер (Любитель свободы)", "need": 77500, "reward": "NFT Candy Cane", "photo": ""},

    19: {"name": "Микаса (Хранительница шарфа)", "need": 85000, "reward": "NFT Berry Box", "photo": ""},

    20: {"name": "Кен Канеки (Любитель кофе)", "need": 95000, "reward": "NFT Vintage Cigar", "photo": ""},

    21: {"name": "Денджи (Бензопила за еду)", "need": 105000, "reward": "NFT Eternal Rose", "photo": ""},

    22: {"name": "Пауэр (Президент мира)", "need": 115000, "reward": "NFT Love Potion", "photo": ""},

    23: {"name": "Макима (Контроль бюджета)", "need": 127500, "reward": "NFT Crystal Ball", "photo": ""},

    24: {"name": "Мегуми (Призыватель теней)", "need": 140000, "reward": "NFT Witch Hat", "photo": ""},

    25: {"name": "Юджи Итадори (Сосуд Сукуны)", "need": 152500, "reward": "NFT Skull Flower", "photo": ""},

    26: {"name": "Сукуна (Король проклятий)", "need": 167500, "reward": "NFT Trapped Heart", "photo": ""},

    27: {"name": "Киллуа (Молния на скейте)", "need": 182500, "reward": "NFT Electric Skull", "photo": ""},

    28: {"name": "Гон Фрикс (Камень-ножницы)", "need": 197500, "reward": "NFT Star Notepad", "photo": ""},

    29: {"name": "Хисока (Фокусник с картами)", "need": 215000, "reward": "NFT Magic Potion", "photo": ""},

    30: {"name": "Эдвард Элрик (Не называй коротышкой)", "need": 232500, "reward": "NFT Signet Ring", "photo": ""},

    31: {"name": "Альфонс (Доспех с котиками)", "need": 250000, "reward": "NFT Toy Bear", "photo": ""},

    32: {"name": "Лайт Ягами (Писатель в тетради)", "need": 270000, "reward": "NFT Desk Calendar", "photo": ""},

    33: {"name": "L (Детектив на сладком)", "need": 290000, "reward": "NFT Lol Pop", "photo": ""},

    34: {"name": "Рюк (Яблочный маньяк)", "need": 310000, "reward": "NFT Evil Eye", "photo": ""},

    35: {"name": "Джотаро Куджо (Ярэ-ярэ дазэ)", "need": 332500, "reward": "NFT B-Day Candle", "photo": ""},

    36: {"name": "Дио Брандо (Остановил время)", "need": 355000, "reward": "NFT Swiss Watch", "photo": ""},

    37: {"name": "Джорно Джованна (У меня есть мечта)", "need": 380000, "reward": "NFT Perfume Bottle", "photo": ""},

    38: {"name": "Моб (100% спокойствия)", "need": 405000, "reward": "NFT Hypno Lollipop", "photo": ""},

    39: {"name": "Рейген (Великий экстрасенс)", "need": 430000, "reward": "NFT Top Hat", "photo": ""},

    40: {"name": "Сон Джин-Ву (Поднимитесь!)", "need": 460000, "reward": "NFT Astral Shard", "photo": ""},

    41: {"name": "Гатс (Чёрный мечник)", "need": 490000, "reward": "NFT Ion Gem", "photo": ""},

    42: {"name": "Спайк Шпигель (Космический ковбой)", "need": 520000, "reward": "NFT Loot Bag", "photo": ""},

    43: {"name": "Алукард (Ночной прогульщик)", "need": 550000, "reward": "NFT Scared Cat", "photo": ""},

    44: {"name": "Кирито (Чёрный мечник Айнкрада)", "need": 585000, "reward": "NFT Sharp Tongue", "photo": ""},

    45: {"name": "Асуна (Молния на кухне)", "need": 620000, "reward": "NFT Sakuras", "photo": ""},

    46: {"name": "Рем (Лучшая горничная)", "need": 655000, "reward": "NFT Snow Globe", "photo": ""},

    47: {"name": "Субару (Возвращение из смерти)", "need": 695000, "reward": "NFT Skull", "photo": ""},

    48: {"name": "Аинз Оал Гоун (Владыка склепа)", "need": 735000, "reward": "NFT Necromancer", "photo": ""},

    49: {"name": "Римуру Темпест (Слизь-император)", "need": 780000, "reward": "NFT Jelly Bunny", "photo": ""},

    50: {"name": "Вельдора (Дракон-отаку)", "need": 825000, "reward": "NFT Dragon", "photo": ""},

    51: {"name": "Итачи (Режим Сусаноо)", "need": 875000, "reward": "NFT Durov's Cap", "photo": ""},

    52: {"name": "Мадара Учиха (Танцор шиноби)", "need": 930000, "reward": "NFT Plush Pepe", "photo": ""},

    53: {"name": "Наруто (Режим Бариона)", "need": 990000, "reward": "NFT Precious Peach", "photo": ""},

    54: {"name": "Гоку (Ультра Инстинкт)", "need": 1060000, "reward": "NFT Heart Locket", "photo": ""},

    55: {"name": "Веджета (Принц саян)", "need": 1150000, "reward": "NFT Heroic Helmet", "photo": ""},

    56: {"name": "Бог Аниме (Абсолютный Сенсей)", "need": 1250000, "reward": "NFT Legendary Crown", "photo": ""},

}

 

FARM_TEXTS = [

    "🍜 Герой плотно поел рамена в Ичираку и выдал +{gain}⚡!",

    "🧘‍♂️ Час медитации под водопадом (правда, он проспал) принесли +{gain}⚡!",

    "🔥 Сенсей наорал так громко, что чакра подскочила на +{gain}⚡!",

    "🍙 Нашёл в кармане вчерашний онигири и зарядился на +{gain}⚡!",

    "⚡ Вспомнил грустный флешбэк из детства и превозмог на +{gain}⚡!",

    "🐱 Погладил уличного кота и словил дзен на +{gain}⚡!",

    "💪 Сделал 100 отжиманий (ладно, 3 отжимания и 97 приседаний на диван): +{gain}⚡!"

]

 

WAIT_TEXTS = [

    "😴 Герой дрыхнет без задних ног! Потерпи ещё {h}ч {m}м.",

    "🍜 Он сейчас на обеде в Ичираку, не мешай! Возвращайся через {h}ч {m}м.",

    "🪫 Чакра на нуле, батарейка села. Зарядка закончится через {h}ч {m}м.",

    "🚽 Герой отошёл по важным делам шиноби. Будет через {h}ч {m}м.",

    "🎮 Он залип в приставку и отказывается тренироваться! Жди {h}ч {m}м."

]

 

NOTIFY_TEXTS = [

    "🔔 <b>Твой герой выспался и доел рамен!</b>\nШкала чакры готова к новой тренировке. Залетай в качалку! ⚡",

    "🔥 <b>Перекур окончен, сенсей!</b>\nГерой бьёт копытом и требует влить в него новую порцию энергии! ⚡",

    "🍜 <b>Ау, сенсей!</b>\nПрошло 3 часа — пора снова отправлять подопечного на тренировку! ⚡"

]

 

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

admin_waiting_broadcast = set()

admin_waiting_group_broadcast = set()

admin_waiting_promo = set()

 

db = sqlite3.connect("game_v2.db")

cur = db.cursor()

 

 

def init_db():

    cur.execute("""

    CREATE TABLE IF NOT EXISTS users (

        user_id INTEGER PRIMARY KEY,

        username TEXT,

        level INTEGER DEFAULT 1,

        energy INTEGER DEFAULT 0,

        last_farm INTEGER DEFAULT 0,

        amulet_until INTEGER DEFAULT 0,

        stars_spent INTEGER DEFAULT 0,

        notified INTEGER DEFAULT 1

    )

    """)

    try:

        cur.execute("ALTER TABLE users ADD COLUMN notified INTEGER DEFAULT 1")

    except sqlite3.OperationalError:

        pass

    cur.execute("CREATE TABLE IF NOT EXISTS claims (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT, level INTEGER, reward TEXT, status TEXT DEFAULT 'pending')")

    cur.execute("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT, item TEXT, amount INTEGER, created_at INTEGER)")

    cur.execute("CREATE TABLE IF NOT EXISTS referrals (referred_id INTEGER PRIMARY KEY, referrer_id INTEGER, rewarded INTEGER DEFAULT 0)")
    
    try:

        cur.execute("ALTER TABLE referrals ADD COLUMN rewarded INTEGER DEFAULT 0")

    except sqlite3.OperationalError:

        pass

    cur.execute("CREATE TABLE IF NOT EXISTS promocodes (code TEXT PRIMARY KEY, reward INTEGER, uses_left INTEGER)")

    cur.execute("CREATE TABLE IF NOT EXISTS promo_used (user_id INTEGER, code TEXT, PRIMARY KEY (user_id, code))")

    cur.execute("CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER PRIMARY KEY, title TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS ramen_gift (sender_id INTEGER PRIMARY KEY, last_sent INTEGER)")

    db.commit()

 

 

init_db()

@dp.message.outer_middleware()

async def track_groups_middleware(handler, event: types.Message, data: dict):

    if event.chat and event.chat.type in ("group", "supergroup"):

        title = event.chat.title or "Группа без названия"

        cur.execute("INSERT OR REPLACE INTO groups (chat_id, title) VALUES (?, ?)", (event.chat.id, title))

        db.commit()

    return await handler(event, data)

 

 

def get_user(user_id, username=""):

    cur.execute(

        "SELECT user_id, username, level, energy, last_farm, amulet_until, stars_spent FROM users WHERE user_id = ?",

        (user_id,)

    )

    user = cur.fetchone()

    if not user:

        clean_name = username or "Без_ника"

        cur.execute("INSERT INTO users (user_id, username, notified) VALUES (?, ?, 1)", (user_id, clean_name))

        db.commit()

        return (user_id, clean_name, 1, 0, 0, 0, 0)

    _, old_uname, lvl, en, lf, am, st = user

    if username and old_uname != username:

        cur.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))

        db.commit()

        return (user_id, username, lvl, en, lf, am, st)

    return user

 

 

def process_referral_reward(referred_id: int):

    cur.execute("SELECT referrer_id, rewarded FROM referrals WHERE referred_id = ?", (referred_id,))

    row = cur.fetchone()

    if not row:

        return None

    referrer_id, rewarded = row

    if rewarded == 1:

        return None

 

    cur.execute("UPDATE referrals SET rewarded = 1 WHERE referred_id = ?", (referred_id,))

    ref_user = get_user(referrer_id)

    _, _, ref_lvl, ref_energy, _, _, _ = ref_user

    lvl_data = LEVELS.get(ref_lvl)

    if lvl_data:

        new_energy = min(ref_energy + 50, lvl_data.get("need"))

        cur.execute("UPDATE users SET energy = ? WHERE user_id = ?", (new_energy, referrer_id))

    db.commit()

    return referrer_id

 

 

def make_progress_bar(current: int, total: int, length: int = 10) -> str:

    if total <= 0:

        return "▓▓▓▓▓▓▓▓▓▓ 100%"

    ratio = min(max(current / total, 0.0), 1.0)

    filled = int(round(length * ratio))

    empty = length - filled

    percent = int(ratio * 100)

    bar = "▓" * filled + "░" * empty

    return f"[{bar}] {percent}%"

 

 

def bottom_menu_keyboard():

    return ReplyKeyboardMarkup(

        keyboard=[

            [KeyboardButton(text="🎴 Мой герой"), KeyboardButton(text="⚡ Впитать энергию")],

            [KeyboardButton(text="🛒 Лавка читера"), KeyboardButton(text="🗺 Дорога славы")],

            [KeyboardButton(text="🏆 Топ-10"), KeyboardButton(text="👥 Друзья (+50⚡)")]

        ],

        resize_keyboard=True,

        is_persistent=True

    )

 

 

def main_keyboard(user_id, level, energy, need):

    buttons = []

    if level in LEVELS:

        if energy >= need:

            buttons.append([InlineKeyboardButton(text="🎁 ЗАБРАТЬ ПОДАРОК (Оставить заявку)", callback_data=f"claim_{user_id}")])

        else:

            buttons.append([InlineKeyboardButton(text="⚡ Впитать энергию", callback_data=f"farm_{user_id}")])

        buttons.append([InlineKeyboardButton(text="🛒 Лавка читера (Бусты за Stars)", callback_data=f"shop_{user_id}")])

    buttons.append([

        InlineKeyboardButton(text="🗺 Дорога славы", callback_data=f"levels_{user_id}"),

        InlineKeyboardButton(text="🏆 Топ-10", callback_data=f"top_{user_id}")

    ])

    buttons.append([InlineKeyboardButton(text="👥 Пригласить друга (+50⚡)", callback_data=f"ref_{user_id}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

 

 

def shop_keyboard(user_id):

    return InlineKeyboardMarkup(inline_keyboard=[

        [InlineKeyboardButton(text="🔮 Амулет удачи 48ч (50-150⚡) — 40 ⭐", callback_data=f"buy_amulet_{user_id}")],

        [InlineKeyboardButton(text="📦 Кейс с удачей (1-100⚡) — 25 ⭐", callback_data=f"buy_case_{user_id}")],

        [InlineKeyboardButton(text="⚡ Попытка прорыва уровня — 100 ⭐", callback_data=f"buy_skip_{user_id}")],

        [InlineKeyboardButton(text="⬅️ Вернуться к герою", callback_data=f"back_{user_id}")]

    ])

def get_card_text(user):

    _, uname, level, energy, last_farm, amulet_until, _ = user

    now = int(time.time())

    max_lvl = len(LEVELS)

 

    lvl_data = LEVELS.get(level)

    if not lvl_data:

        return (

            f"╭── <b>АНИМЕ-КАЧАЛКА</b> ──╮\n"

            f"👤 Сенсей: <b>@{uname}</b>\n"

            f"🏆 Ранг: <b>Уровень {level} из {max_lvl}</b>\n"

            f"╰───────────────────╯\n\n"

            "🔒 Вы прошли все 56 уровней и стали Богом Аниме! Ждите нового сезона!"

        )

 

    need = lvl_data.get("need")

    p_bar = make_progress_bar(energy, need)

    amulet_status = "🔥 Активен (50–150⚡)" if amulet_until > now else "💤 Спит (1–50⚡)"

 

    wait_time = (last_farm + COOLDOWN) - now

    if wait_time <= 0:

        timer_text = "🟢 <b>Статус:</b> Герой выспался и готов качаться!"

    else:

        hours = wait_time // 3600

        mins = (wait_time % 3600) // 60

        timer_text = f"⏳ <b>Перекур:</b> ещё {hours}ч {mins}м"

 

    return (

        f"╭── 🎴 <b>УРОВЕНЬ {level} / {max_lvl}</b> ──╮\n"

        f"👤 Сенсей: <b>@{uname}</b>\n"

        f"🦸 Герой: <b>{lvl_data.get('name')}</b>\n"

        f"🎁 Награда: <b>{lvl_data.get('reward')}</b>\n"

        f"╰───────────────────╯\n\n"

        f"⚡ <b>Шкала чакры:</b>\n"

        f"<code>{p_bar}</code> (<b>{energy} / {need}</b>)\n\n"

        f"🔮 <b>Амулет удачи:</b> {amulet_status}\n"

        f"{timer_text}"

    )

 

 

def get_shop_text():

    return (

        "╭── 🛒 <b>ЛАВКА ЧИТЕРА</b> ──╮\n"

        "<i>Ускорь прокачку за Telegram Stars ⭐</i>\n"

        "╰───────────────────╯\n\n"

        "🔮 <b>Амулет удачи (40 ⭐)</b>\n"

        "└ На 48 часов отменяет лень героя — выпадает строго от <b>50 до 150⚡</b> за сбор!\n\n"

        "📦 <b>Кейс с удачей (25 ⭐)</b>\n"

        "└ Кот в мешке с энергией! Внутри от <b>1 до 100⚡</b> мгновенно и без таймера.\n\n"

        "⚡ <b>Попытка прорыва (100 ⭐)</b>\n"

        "└ Запрещённая техника сенсея! Даёт шанс мгновенно закрыть весь текущий уровень."

    )

 

 

def get_levels_text(current_level: int = 1):

    max_lvl = len(LEVELS)

    start_lvl = max(1, min(current_level, max_lvl - 11))

    end_lvl = min(max_lvl, start_lvl + 11)

 

    text = (

        f"╭── 🗺 <b>ДОРОГА СЛАВЫ (Ур. {start_lvl}–{end_lvl} из {max_lvl})</b> ──╮\n"

        f"<i>Твои ближайшие герои и награды</i>\n"

        f"╰──────────────────────────────╯\n\n"

    )

    for i in range(start_lvl, end_lvl + 1):

        lvl_data = LEVELS.get(i)

        mark = "👉" if i == current_level else ("✅" if i < current_level else "⬜️")

        text += f"{mark} <b>Ур. {i}:</b> {lvl_data.get('name')}\n   └ {lvl_data.get('need')}⚡ ➔ 🎁 <b>{lvl_data.get('reward')}</b>\n"

 

    if end_lvl < max_lvl:

        final_data = LEVELS.get(max_lvl)

        text += f"\n🏆 <b>Финал (Ур. {max_lvl}):</b> {final_data.get('name')} ➔ 🎁 <b>{final_data.get('reward')}</b>"

    return text

 

 

def get_top_text():

    cur.execute("SELECT username, level, energy FROM users ORDER BY level DESC, energy DESC LIMIT 10")

    rows = cur.fetchall()

    text = (

        "╭── 🏆 <b>ТОП-10 ЛУЧШИХ СЕНСЕЕВ</b> ──╮\n"

        "<i>Самые мощные игроки Аниме-Качалки</i>\n"

        "╰─────────────────────────╯\n\n"

    )

    if not rows:

        return text + "Пока тут пусто. Стань первым!"

 

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}

    for idx, (uname, lvl, en) in enumerate(rows, start=1):

        place = medals.get(idx, f"<b>{idx}.</b>")

        hero_data = LEVELS.get(lvl)

        if hero_data:

            hero_name, *_ = hero_data.get("name").split(" (")

        else:

            hero_name = "Легенда"

        text += f"{place} @{uname} — <b>Ур. {lvl}</b> ({hero_name}, {en}⚡)\n"

    return text

 

 

def get_ref_text(uid: int):

    clean_bot = BOT_USERNAME.replace("@", "").strip()

    ref_link = f"https://t.me{clean_bot}?start={uid}"

    cur.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND rewarded = 1", (uid,))

    (active_refs,) = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND rewarded = 0", (uid,))

    (pending_refs,) = cur.fetchone()

 

    text = (

        f"╭── 👥 <b>АКАДЕМИЯ СЕНСЕЯ</b> ──╮\n"

        f"<i>Приводи учеников и получай по +50⚡!</i>\n"

        f"╰───────────────────╯\n\n"

        f"✅ Активных учеников: <b>{active_refs} чел.</b> (+<b>{active_refs * 50}⚡</b>)\n"

        f"⏳ Ждут первой тренировки: <b>{pending_refs} чел.</b>\n\n"

        f"📜 <b>Как получить бонус:</b>\n"

        f"1. Отправь другу свою личную ссылку.\n"

        f"2. Когда он зайдёт и впервые нажмёт <b>«⚡ Впитать энергию»</b> — тебе автоматически упадут <b>+50⚡</b>!\n\n"

        f"🔗 <b>Твоя ссылка (нажми, чтобы скопировать):</b>\n"

        f"<code>{ref_link}</code>"

    )

    return text, ref_link






async def send_or_edit_screen(target, text: str, kb: InlineKeyboardMarkup, photo_id: str = "", is_edit: bool = False):

    if not is_edit:

        if photo_id:

            await target.answer_photo(photo=photo_id, caption=text, parse_mode="HTML", reply_markup=kb)

        else:

            await target.answer(text=text, parse_mode="HTML", reply_markup=kb)

        return

 

    if photo_id:

        if target.photo:

            await target.edit_media(media=InputMediaPhoto(media=photo_id, caption=text, parse_mode="HTML"), reply_markup=kb)

        else:

            await target.delete()

            await target.answer_photo(photo=photo_id, caption=text, parse_mode="HTML", reply_markup=kb)

    else:

        if target.photo:

            await target.delete()

            await target.answer(text=text, parse_mode="HTML", reply_markup=kb)

        else:

            await target.edit_text(text=text, parse_mode="HTML", reply_markup=kb)

 

 

async def send_or_edit_card(target, user, is_edit=False):

    uid, _, lvl, energy, _, _, _ = user

    lvl_data = LEVELS.get(lvl)

    need = lvl_data.get("need") if lvl_data else 0

    photo_id = lvl_data.get("photo") if lvl_data else ""

    text = get_card_text(user)

    kb = main_keyboard(uid, lvl, energy, need)

    await send_or_edit_screen(target, text, kb, photo_id=photo_id, is_edit=is_edit)

 

 

def check_owner(call: types.CallbackQuery, target_id: int):

    return call.from_user.id == target_id

 

 

@dp.message(Command("start"))

async def cmd_start(message: types.Message):

    uid = message.from_user.id

    parts = (message.text or "").split(maxsplit=1)

    if len(parts) == 2:

        _, raw_ref = parts

        ref_code = raw_ref.strip()

        if ref_code.isdigit():

            referrer_id = int(ref_code)

            if referrer_id != uid:

                cur.execute("SELECT 1 FROM users WHERE user_id = ?", (uid,))

                if not cur.fetchone():

                    cur.execute("INSERT OR IGNORE INTO referrals (referred_id, referrer_id, rewarded) VALUES (?, ?, 0)", (uid, referrer_id))

                    db.commit()

 

    user = get_user(uid, message.from_user.username)

    _, uname, _, _, _, _, _ = user

    welcome_text = (

        f"👋 <b>Йо, @{uname}! Добро пожаловать в Аниме-Качалку!</b>\n\n"

        "Здесь ты станешь великим сенсеем и будешь вливать энергию в легендарных героев — от голодного Наруто до Бога Аниме.\n\n"

        "📜 <b>Правила простые:</b>\n"

        "1️⃣ Раз в 3 часа жми <b>«Впитать энергию»</b> — герой пойдёт тренироваться и принесёт от 1 до 50⚡.\n"

        "2️⃣ Заполнишь шкалу — забирай реальные <b>подарки Telegram и редкие NFT</b>!\n"

        "3️⃣ Лень ждать? Загляни в <b>Лавку читера</b> за Звёздами.\n\n"

        "👇 <i>Используй кнопки снизу для быстрого управления!</i>"

    )

    kb_bottom = bottom_menu_keyboard() if message.chat.type == "private" else None

    welcome_banner = BANNERS.get("welcome")

    if welcome_banner:

        await message.answer_photo(photo=welcome_banner, caption=welcome_text, parse_mode="HTML", reply_markup=kb_bottom)

    else:

        await message.answer(welcome_text, parse_mode="HTML", reply_markup=kb_bottom)

    await send_or_edit_card(message, user, is_edit=False)

 

 

@dp.message(Command("card"))

@dp.message(F.text == "🎴 Мой герой")

async def cmd_card(message: types.Message):

    user = get_user(message.from_user.id, message.from_user.username)

    await send_or_edit_card(message, user, is_edit=False)

 

 

@dp.message(Command("farm"))

@dp.message(F.text == "⚡ Впитать энергию")

async def cmd_farm_text(message: types.Message):

    user = get_user(message.from_user.id, message.from_user.username)

    uid, uname, level, energy, last_farm, amulet_until, _ = user

    now = int(time.time())

 

    lvl_data = LEVELS.get(level)

    if not lvl_data:

        return await message.reply("🔒 Все доступные герои уже на пике формы, ждите обновления!")

    need = lvl_data.get("need")

    if energy >= need:

        return await message.reply("🎁 Шкала полная! Хватит качать, жми кнопку подарка в /card!")

    if now - last_farm < COOLDOWN:

        rem = (last_farm + COOLDOWN) - now

        msg = random.choice(WAIT_TEXTS).format(h=rem // 3600, m=(rem % 3600) // 60)

        return await message.reply(f"@{uname}, {msg}")

 

    gain = random.randint(50, 150) if amulet_until > now else random.randint(1, 50)

    new_energy = min(energy + gain, need)

 

    cur.execute("UPDATE users SET energy = ?, last_farm = ?, notified = 0 WHERE user_id = ?", (new_energy, now, uid))

    db.commit()

 

    referrer_id = process_referral_reward(uid)

    if referrer_id:

        try:

            await bot.send_message(referrer_id, f"🎉 <b>Твой ученик @{uname} прошёл первую тренировку!</b>\nТебе начислено <b>+50⚡</b> к текущему герою!", parse_mode="HTML")

        except Exception:

            pass

 

    phrase = random.choice(FARM_TEXTS).format(gain=gain)

    p_bar = make_progress_bar(new_energy, need)

    await message.reply(f"👤 @{uname}: {phrase}\n<code>{p_bar}</code> (<b>{new_energy}/{need}⚡</b>)", parse_mode="HTML")

@dp.message(Command("shop"))

@dp.message(F.text == "🛒 Лавка читера")

async def cmd_shop_text(message: types.Message):

    uid = message.from_user.id

    get_user(uid, message.from_user.username)

    await send_or_edit_screen(message, get_shop_text(), shop_keyboard(uid), photo_id=BANNERS.get("shop"), is_edit=False)

 

 

@dp.message(Command("levels"))

@dp.message(F.text == "🗺 Дорога славы")

async def cmd_levels_text(message: types.Message):

    uid = message.from_user.id

    user = get_user(uid, message.from_user.username)

    _, _, lvl, _, _, _, _ = user

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎴 Моя карточка", callback_data=f"back_{uid}")]])

    await send_or_edit_screen(message, get_levels_text(lvl), kb, photo_id=BANNERS.get("levels"), is_edit=False)

 

 

@dp.message(Command("top"))

@dp.message(F.text == "🏆 Топ-10")

async def cmd_top_text(message: types.Message):

    uid = message.from_user.id

    get_user(uid, message.from_user.username)

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎴 Моя карточка", callback_data=f"back_{uid}")]])

    await send_or_edit_screen(message, get_top_text(), kb, photo_id=BANNERS.get("top"), is_edit=False)

 

 

@dp.message(Command("ref"))

@dp.message(F.text == "👥 Друзья (+50⚡)")

async def cmd_ref_text(message: types.Message):

    uid = message.from_user.id

    get_user(uid, message.from_user.username)

    text, _ = get_ref_text(uid)

    kb = InlineKeyboardMarkup(inline_keyboard=[

        [InlineKeyboardButton(text="🎴 Моя карточка", callback_data=f"back_{uid}")]

    ])

    await message.answer(text, parse_mode="HTML", reply_markup=kb)

 

 

@dp.callback_query(F.data.startswith("ref_"))

async def cb_ref(call: types.CallbackQuery):

    _, target_str = call.data.split("_")

    target_id = int(target_str)

    if not check_owner(call, target_id):

        return await call.answer("Открой свою ссылку командой /ref", show_alert=True)

    text, _ = get_ref_text(target_id)

    kb = InlineKeyboardMarkup(inline_keyboard=[

        [InlineKeyboardButton(text="⬅️ Вернуться к герою", callback_data=f"back_{target_id}")]

    ])

    await send_or_edit_screen(call.message, text, kb, photo_id="", is_edit=True)

 

 

@dp.callback_query(F.data.startswith("ref_"))

async def cb_ref(call: types.CallbackQuery):

    _, target_str = call.data.split("_")

    target_id = int(target_str)

    if not check_owner(call, target_id):

        return await call.answer("Открой свою ссылку командой /ref", show_alert=True)

    text, ref_link = get_ref_text(target_id)

    share_url = f"https://t.me{quote(ref_link)}"

    kb = InlineKeyboardMarkup(inline_keyboard=[

        [InlineKeyboardButton(text="📤 Отправить ссылку другу", url=share_url)],

        [InlineKeyboardButton(text="⬅️ Вернуться к герою", callback_data=f"back_{target_id}")]

    ])

    await send_or_edit_screen(call.message, text, kb, photo_id="", is_edit=True)


 

 

@dp.message(Command("promo"))

async def cmd_use_promo(message: types.Message):

    raw_text = (message.text or "").strip()

    parts = raw_text.split(maxsplit=1)

    if len(parts) < 2:

        return await message.reply("🎟 <b>Как активировать промокод:</b>\nНапиши <code>/promo ТВОЙ_КОД</code>", parse_mode="HTML")

 

    _, code_part = parts

    code = code_part.strip().upper()

    uid = message.from_user.id

    user = get_user(uid, message.from_user.username)

    _, _, level, current_energy, _, _, _ = user

 

    cur.execute("SELECT reward, uses_left FROM promocodes WHERE code = ?", (code,))

    promo = cur.fetchone()

    if not promo:

        return await message.reply(f"❌ Промокод <b>{code}</b> не найден или уже закончился!", parse_mode="HTML")

 

    reward, uses_left = promo

    if uses_left <= 0:

        return await message.reply("😢 Все активации этого промокода уже разобрали!")

 

    cur.execute("SELECT 1 FROM promo_used WHERE user_id = ? AND code = ?", (uid, code))

    if cur.fetchone():

        return await message.reply("⚠️ Ты уже активировал этот промокод ранее!")

 

    lvl_data = LEVELS.get(level)

    need = lvl_data.get("need") if lvl_data else (current_energy + reward)

    if current_energy >= need:

        return await message.reply("🎁 У твоего героя шкала уже полная! Сначала забери подарок в /card, а потом вводи промокод!")

 

    new_energy = min(current_energy + reward, need)

    cur.execute("UPDATE users SET energy = ? WHERE user_id = ?", (new_energy, uid))

    cur.execute("UPDATE promocodes SET uses_left = uses_left - 1 WHERE code = ?", (code,))

    cur.execute("INSERT INTO promo_used (user_id, code) VALUES (?, ?)", (uid, code))

    db.commit()

 

    await message.reply(f"🎉 <b>Промокод {code} активирован!</b>\nНачислено <b>+{reward}⚡</b>! Проверить шкалу: /card", parse_mode="HTML")

@dp.message(F.photo, F.from_user.id == ADMIN_ID)

async def admin_get_photo_id(message: types.Message):

    if message.from_user.id in admin_waiting_broadcast or message.from_user.id in admin_waiting_group_broadcast:

        return

    *_, largest_photo = message.photo

    await message.reply(f"🖼 <b>Код картинки (file_id):</b>\n<code>{largest_photo.file_id}</code>", parse_mode="HTML")

 

 

def get_admin_dashboard():

    now = int(time.time())

    cur.execute("SELECT COUNT(*), SUM(stars_spent) FROM users")

    total_users, total_stars = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM users WHERE last_farm >= ?", (now - 86400,))

    (active_24h,) = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM users WHERE last_farm >= ?", (now - 7 * 86400,))

    (active_7d,) = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM groups")

    (groups_count,) = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM referrals WHERE rewarded = 1")

    (active_refs,) = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM claims WHERE status = 'pending'")

    (pending_claims,) = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM claims WHERE status = 'done'")

    (done_claims,) = cur.fetchone()

 

    text = (

        f"👑 <b>Админ-панель и Аналитика</b>\n\n"

        f"👥 <b>Аудитория:</b>\n"

        f"∙ Игроков в базе: <b>{total_users}</b>\n"

        f"∙ Активны за 24ч: <b>{active_24h}</b> | за 7д: <b>{active_7d}</b>\n"

        f"∙ Групповых чатов: <b>{groups_count}</b>\n"

        f"∙ Пришло по рефералкам: <b>{active_refs}</b>\n\n"

        f"💰 <b>Финансы и Призы:</b>\n"

        f"∙ Заработано всего: <b>{total_stars or 0} ⭐</b>\n"

        f"∙ Ожидают подарка: <b>{pending_claims} чел.</b> (выдано: {done_claims})"

    )

    kb = InlineKeyboardMarkup(inline_keyboard=[

        [InlineKeyboardButton(text=f"🎁 Заявки на подарки ({pending_claims})", callback_data="admin_claims")],

        [InlineKeyboardButton(text="🏆 Топ донатеров", callback_data="admin_top_donors"), InlineKeyboardButton(text="🧾 Платежи", callback_data="admin_payments")],

        [InlineKeyboardButton(text="🎟 Создать промокод", callback_data="admin_new_promo"), InlineKeyboardButton(text="📋 Промокоды", callback_data="admin_list_promo")],

        [InlineKeyboardButton(text="📢 Рассылка в ЛС", callback_data="admin_broadcast"), InlineKeyboardButton(text="📣 Рассылка в чаты", callback_data="admin_group_broadcast")],

        [InlineKeyboardButton(text="💾 Скачать базу", callback_data="admin_backup"), InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_refresh")]

    ])

    return text, kb

 

 

@dp.message(Command("admin"))

async def cmd_admin(message: types.Message):

    if message.from_user.id != ADMIN_ID:

        return

    admin_waiting_broadcast.discard(ADMIN_ID)

    admin_waiting_group_broadcast.discard(ADMIN_ID)

    admin_waiting_promo.discard(ADMIN_ID)

    text, kb = get_admin_dashboard()

    await message.answer(text, parse_mode="HTML", reply_markup=kb)

 

 

@dp.callback_query(F.data == "admin_refresh")

async def cb_admin_refresh(call: types.CallbackQuery):

    if call.from_user.id != ADMIN_ID:

        return

    admin_waiting_broadcast.discard(ADMIN_ID)

    admin_waiting_group_broadcast.discard(ADMIN_ID)

    admin_waiting_promo.discard(ADMIN_ID)

    text, kb = get_admin_dashboard()

    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

 

 

@dp.callback_query(F.data == "admin_new_promo")

async def cb_admin_new_promo(call: types.CallbackQuery):

    if call.from_user.id != ADMIN_ID:

        return

    admin_waiting_broadcast.discard(ADMIN_ID)

    admin_waiting_group_broadcast.discard(ADMIN_ID)

    admin_waiting_promo.add(ADMIN_ID)

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="admin_refresh")]])

    await call.message.edit_text(

        "🎟 <b>Создание нового промокода</b>\n\n"

        "Отправьте следующим сообщением 3 значения через пробел:\n"

        "<code>НАЗВАНИЕ ЭНЕРГИЯ КОЛИЧЕСТВО</code>\n\n"

        "<i>Пример:</i> <code>RAMEN777 200 30</code>",

        parse_mode="HTML",

        reply_markup=kb

    )

 

 

@dp.message(F.from_user.id == ADMIN_ID, lambda m: m.from_user.id in admin_waiting_promo)

async def process_new_promo(message: types.Message):

    admin_waiting_promo.discard(ADMIN_ID)

    parts = (message.text or "").split()

    if len(parts) != 3:

        return await message.reply("❌ Нужно ввести ровно 3 значения через пробел.\nПример: <code>RAMEN777 200 30</code>", parse_mode="HTML")

 

    raw_code, reward_str, uses_str = parts

    if not reward_str.isdigit() or not uses_str.isdigit():

        return await message.reply("❌ Энергия и количество активаций должны быть числами без плюсов.\nПример: <code>RAMEN777 200 30</code>", parse_mode="HTML")

 

    code = raw_code.strip().upper()

    reward = int(reward_str)

    uses = int(uses_str)

 

    cur.execute("INSERT OR REPLACE INTO promocodes (code, reward, uses_left) VALUES (?, ?, ?)", (code, reward, uses))

    db.commit()

    await message.reply(f"✅ <b>Промокод создан!</b>\n🎟 Код: <code>{code}</code>\n⚡ Награда: <b>+{reward}⚡</b>\n👥 Активаций: <b>{uses} шт.</b>", parse_mode="HTML")

 

 

@dp.callback_query(F.data == "admin_list_promo")

async def cb_admin_list_promo(call: types.CallbackQuery):

    if call.from_user.id != ADMIN_ID:

        return

    cur.execute("SELECT code, reward, uses_left FROM promocodes WHERE uses_left > 0")

    rows = cur.fetchall()

    if not rows:

        return await call.answer("Активных промокодов сейчас нет!", show_alert=True)

    text = "📋 <b>Активные промокоды:</b>\n\n"

    for code, reward, uses in rows:

        text += f"∙ <code>{code}</code> — <b>+{reward}⚡</b> (осталось {uses} шт.)\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_refresh")]])

    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

 

 

@dp.callback_query(F.data == "admin_backup")

async def cb_admin_backup(call: types.CallbackQuery):

    if call.from_user.id != ADMIN_ID:

        return

    db.commit()

    await call.message.answer_document(

        document=FSInputFile("game_v2.db"),

        caption="💾 <b>Резервная копия базы данных.</b>\nЧтобы восстановить прогресс после обновления, просто отправьте этот файл обратно боту в личку.",

        parse_mode="HTML"

    )

    await call.answer()

 

 

@dp.message(F.document, F.from_user.id == ADMIN_ID)

async def admin_restore_db(message: types.Message):

    global db, cur

    fname = (message.document.file_name or "").lower()

    if not fname.endswith(".db"):

        return await message.reply("⚠️ Отправьте файл базы данных с расширением <b>.db</b>.", parse_mode="HTML")

 

    try:

        db.commit()

        db.close()

 

        import os

        if os.path.exists("game_v2.db"):

            os.remove("game_v2.db")

 

        file_info = await bot.get_file(message.document.file_id)

        await bot.download_file(file_info.file_path, "game_v2.db")

 

        db = sqlite3.connect("game_v2.db")

        cur = db.cursor()

        cur.execute("DROP TABLE IF EXISTS referrals")

        db.commit()

        init_db()

 

        cur.execute("SELECT COUNT(*) FROM users")

        (users_count,) = cur.fetchone()

 

        await message.reply(

            f"✅ <b>База восстановлена, а реферальная система обновлена!</b>\n"

            f"👥 Загружено игроков: <b>{users_count} чел.</b>",

            parse_mode="HTML"

        )

    except Exception as e:

        db = sqlite3.connect("game_v2.db")

        cur = db.cursor()

        await message.reply(f"❌ <b>Ошибка при восстановлении:</b>\n<code>{e}</code>", parse_mode="HTML")

    await message.reply("✅ <b>База восстановлена, а таблицы промокодов обновлены!</b>", parse_mode="HTML")







@dp.callback_query(F.data == "admin_top_donors")

async def cb_admin_top_donors(call: types.CallbackQuery):

    if call.from_user.id != ADMIN_ID:

        return

    cur.execute("SELECT username, user_id, stars_spent, level FROM users WHERE stars_spent > 0 ORDER BY stars_spent DESC LIMIT 10")

    rows = cur.fetchall()

    if not rows:

        return await call.answer("Покупок за Stars пока не было!", show_alert=True)

    text = "🏆 <b>Топ-10 донатеров бота:</b>\n\n"

    for idx, (uname, uid, spent, lvl) in enumerate(rows, start=1):

        text += f"{idx}. @{uname} (ID: <code>{uid}</code>) — <b>{spent} ⭐</b> (Ур. {lvl})\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_refresh")]])

    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

 

 

@dp.callback_query(F.data == "admin_payments")

async def cb_admin_payments(call: types.CallbackQuery):

    if call.from_user.id != ADMIN_ID:

        return

    cur.execute("SELECT username, item, amount, created_at FROM payments ORDER BY id DESC LIMIT 10")

    rows = cur.fetchall()

    if not rows:

        return await call.answer("История платежей пока пуста!", show_alert=True)

    item_names = {"amulet": "🔮 Амулет", "case": "📦 Кейс", "skip": "⚡ Прорыв"}

    text = "🧾 <b>Последние 10 покупок Stars:</b>\n\n"

    for uname, item, amount, ts in rows:

        dt = datetime.fromtimestamp(ts).strftime("%d.%m %H:%M")

        text += f"∙ <code>{dt}</code> | @{uname} — {item_names.get(item, item)} (<b>{amount} ⭐</b>)\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_refresh")]])

    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

 

 

@dp.callback_query(F.data == "admin_broadcast")

async def cb_admin_broadcast(call: types.CallbackQuery):

    if call.from_user.id != ADMIN_ID:

        return

    admin_waiting_promo.discard(ADMIN_ID)

    admin_waiting_group_broadcast.discard(ADMIN_ID)

    admin_waiting_broadcast.add(ADMIN_ID)

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="admin_refresh")]])

    await call.message.edit_text("📢 <b>Рассылка в личку игрокам</b>\n\nОтправьте следующим сообщением текст или фото с подписью.", parse_mode="HTML", reply_markup=kb)

 

 

@dp.message(F.from_user.id == ADMIN_ID, lambda m: m.from_user.id in admin_waiting_broadcast)

async def process_broadcast(message: types.Message):

    admin_waiting_broadcast.discard(ADMIN_ID)

    cur.execute("SELECT user_id FROM users")

    users = cur.fetchall()

    sent = 0

    for (uid,) in users:

        try:

            await message.copy_to(chat_id=uid)

            sent += 1

            await asyncio.sleep(0.05)

        except Exception:

            pass

    await message.answer(f"✅ <b>Рассылка в ЛС завершена!</b>\nДоставлено: <b>{sent}</b> из {len(users)} игроков.", parse_mode="HTML")

 

 

@dp.callback_query(F.data == "admin_group_broadcast")

async def cb_admin_group_broadcast(call: types.CallbackQuery):

    if call.from_user.id != ADMIN_ID:

        return

    admin_waiting_promo.discard(ADMIN_ID)

    admin_waiting_broadcast.discard(ADMIN_ID)

    admin_waiting_group_broadcast.add(ADMIN_ID)

    cur.execute("SELECT COUNT(*) FROM groups")

    (groups_count,) = cur.fetchone()

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="admin_refresh")]])

    await call.message.edit_text(
          f"📣 <b>Рассылка по групповым чатам</b>\nВ базе чатов: <b>{groups_count}</b>\n\nОтправьте следующим сообщением текст или фото с подписью.",

        parse_mode="HTML",

        reply_markup=kb

    )

 

 

@dp.message(F.from_user.id == ADMIN_ID, lambda m: m.from_user.id in admin_waiting_group_broadcast)

async def process_group_broadcast(message: types.Message):

    admin_waiting_group_broadcast.discard(ADMIN_ID)

    cur.execute("SELECT chat_id FROM groups")

    chats = cur.fetchall()

    sent = 0

    for (cid,) in chats:

        try:

            await message.copy_to(chat_id=cid)

            sent += 1

            await asyncio.sleep(0.05)

        except Exception:

            cur.execute("DELETE FROM groups WHERE chat_id = ?", (cid,))

            db.commit()

    await message.answer(f"✅ <b>Рассылка по чатам завершена!</b>\nДоставлено в <b>{sent}</b> групп.", parse_mode="HTML")

 

 

@dp.callback_query(F.data == "admin_claims")

async def cb_admin_claims(call: types.CallbackQuery):

    if call.from_user.id != ADMIN_ID:

        return

    cur.execute("SELECT id, user_id, username, level, reward FROM claims WHERE status = 'pending' LIMIT 10")

    rows = cur.fetchall()

    if not rows:

        return await call.answer("Активных заявок нет!", show_alert=True)

    text = "🎁 <b>Невыданные подарки:</b>\n\n"

    buttons = []

    for cid, uid, uname, lvl, rew in rows:

        text += f"#{cid} | @{uname} (ID: <code>{uid}</code>) — Ур.{lvl} ({rew})\n"

        buttons.append([InlineKeyboardButton(text=f"✅ Выдано #{cid} (@{uname})", callback_data=f"done_claim_{cid}")])

    buttons.append([InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_refresh")])

    await call.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

 

 

@dp.callback_query(F.data.startswith("done_claim_"))

async def cb_done_claim(call: types.CallbackQuery):

    if call.from_user.id != ADMIN_ID:

        return

    _, _, cid_str = call.data.split("_")

    cur.execute("UPDATE claims SET status = 'done' WHERE id = ?", (int(cid_str),))

    db.commit()

    await call.answer("Заявка закрыта!", show_alert=True)

    await cb_admin_claims(call)

@dp.message(Command("rp"))

async def cmd_rp_help(message: types.Message):

    await message.reply(

        "🎭 <b>20 АНИМЕ РП-КОМАНД ДЛЯ ЧАТА</b>\n"

        "<i>Ответьте на сообщение друга одним из этих слов:</i>\n\n"

        "🫂 <b>Тёплые:</b> обнять, погладить, поцеловать, укусить, похвалить, дать пять, укрыть пледом, принести чай\n"

        "🍜 <b>Угощения:</b> угостить раменом (+5⚡ другу раз в сутки), накормить онигири\n"

        "⚔️ <b>Боевые и мемы:</b> ударить, подзатыльник, гендзюцу, расэнган, кинуть тапок, связать, вызвать на бой, запечатать, облить водой, спрятать в шкаф",

        parse_mode="HTML"

    )

 

 

@dp.message(F.reply_to_message, F.text)

async def handle_rp_commands(message: types.Message):

    if message.chat.type == "private" or message.reply_to_message.from_user.is_bot:

        return

 

    cmd = message.text.strip().lower()

    sender = message.from_user

    target = message.reply_to_message.from_user

 

    if sender.id == target.id:

        return

 

    s_name = f"<b>@{sender.username or sender.first_name}</b>"

    t_name = f"<b>@{target.username or target.first_name}</b>"

 

    if cmd == "угостить раменом":

        now = int(time.time())

        cur.execute("SELECT last_sent FROM ramen_gift WHERE sender_id = ?", (sender.id,))

        row = cur.fetchone()

        if row and (now - row[0] < 86400):

            return await message.answer(f"🍜 {s_name} дружески угостил(а) {t_name} горячим раменом в Ичираку!")

 

        cur.execute("INSERT OR REPLACE INTO ramen_gift (sender_id, last_sent) VALUES (?, ?)", (sender.id, now))

        t_user = get_user(target.id, target.username)

        _, _, t_lvl, t_en, _, _, _ = t_user

        lvl_data = LEVELS.get(t_lvl)

        need = lvl_data.get("need") if lvl_data else (t_en + 5)

        new_en = min(t_en + 5, need)

        cur.execute("UPDATE users SET energy = ? WHERE user_id = ?", (new_en, target.id))

        db.commit()

        return await message.answer(f"🍜 {s_name} угостил(а) {t_name} королевским раменом! Герой получил <b>+5⚡</b>!", parse_mode="HTML")

 

    rp_actions = {

        "обнять": f"🫂 {s_name} крепко-крепко обнял(а) {t_name} как Аня своего Пингвина!",

        "погладить": f"👋 {s_name} нежно погладил(а) {t_name} по голове. Хороший ученик!",

        "поцеловать": f"💋 {s_name} внезапно поцеловал(а) {t_name} в щёку! Весь чат покраснел!",

        "укусить": f"🧛‍♂️ {s_name} сделал(а) внезапный кусь за ушко {t_name} в стиле Незуко!",

        "похвалить": f"🌟 {s_name} похвалил(а) {t_name}: «Ты сражался как настоящий Хокаге!»",

        "дать пять": f"🙌 {s_name} и {t_name} звонко дали друг другу пять!",

        "укрыть пледом": f"🛌 {s_name} заботливо укутал(а) {t_name} в тёплый пледик после тяжёлой тренировки.",

        "принести чай": f"🍵 {s_name} заварил(а) и принёс(ла) {t_name} кружку ароматного зелёного чая.",

        "накормить онигири": f"🍙 {s_name} сунул(а) в рот {t_name} свежий рисовый онигири!",

        "ударить": f"👊 {s_name} вписал(а) мощный цундере-хук прямо в челюсть {t_name}!",

        "подзатыльник": f"💥 {s_name} отвесил(а) воспитательный подзатыльник {t_name} в стиле Сакуры!",

        "гендзюцу": f"👁 {s_name} активировал(а) Мангекё Шаринган и запер(ла) {t_name} в вечном гендзюцу!",

        "расэнган": f"🌀 {s_name} скрутил(а) в руке мощный Расэнган и отправил(а) {t_name} в полёт до соседнего чата!",

        "кинуть тапок": f"🩴 {s_name} снайперским броском запустил(а) тапок прямо в лоб {t_name}!",

        "связать": f"🪢 {s_name} применил(а) технику теневого связывания и обездвижил(а) {t_name}!",

        "вызвать на бой": f"⚔️ {s_name} пафосно бросил(а) перчатку в лицо {t_name} и вызвал(а) на поединок!",

        "запечатать": f"📜 {s_name} наклеил(а) взрывную печать на спину {t_name} и тихо отбежал(а) в сторону!",

        "облить водой": f"💦 {s_name} использовал(а) стиль воды и окатил(а) {t_name} ледяным душем из ведра!",

        "спрятать в шкаф": f"🚪 {s_name} затолкал(а) {t_name} в шкаф и подпёр(ла) дверь шваброй!",

    }

 

    if cmd in rp_actions:

        await message.answer(rp_actions[cmd], parse_mode="HTML")

@dp.callback_query(F.data.startswith("back_"))

async def cb_back(call: types.CallbackQuery):

    _, target_str = call.data.split("_")

    target_id = int(target_str)

    if not check_owner(call, target_id):

        return await call.answer("Вызови своего героя командой /card", show_alert=True)

    await send_or_edit_card(call.message, get_user(target_id), is_edit=True)

 

 

@dp.callback_query(F.data.startswith("levels_"))

async def cb_levels(call: types.CallbackQuery):

    _, target_str = call.data.split("_")

    target_id = int(target_str)

    if not check_owner(call, target_id):

        return await call.answer("Вызови своё меню командой /card", show_alert=True)

    user = get_user(target_id)

    _, _, lvl, _, _, _, _ = user

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Вернуться к герою", callback_data=f"back_{target_id}")]])

    await send_or_edit_screen(call.message, get_levels_text(lvl), kb, photo_id=BANNERS.get("levels"), is_edit=True)

 

 

@dp.callback_query(F.data.startswith("top_"))

async def cb_top(call: types.CallbackQuery):

    _, target_str = call.data.split("_")

    target_id = int(target_str)

    if not check_owner(call, target_id):

        return await call.answer("Открой свой топ командой /top", show_alert=True)

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Вернуться к герою", callback_data=f"back_{target_id}")]])

    await send_or_edit_screen(call.message, get_top_text(), kb, photo_id=BANNERS.get("top"), is_edit=True)

 

 

@dp.callback_query(F.data.startswith("ref_"))

async def cb_ref(call: types.CallbackQuery):

    _, target_str = call.data.split("_")

    target_id = int(target_str)

    if not check_owner(call, target_id):

        return await call.answer("Открой свою ссылку командой /ref", show_alert=True)

    try:

        bot_info = await bot.get_me()

        b_uname = bot_info.username

    except Exception:

        b_uname = ""

    text, ref_link = get_ref_text(target_id, b_uname)

    share_url = f"https://t.me{quote(ref_link)}"

    kb = InlineKeyboardMarkup(inline_keyboard=[

        [InlineKeyboardButton(text="📤 Отправить ссылку другу", url=share_url)],

        [InlineKeyboardButton(text="⬅️ Вернуться к герою", callback_data=f"back_{target_id}")]

    ])

    await send_or_edit_screen(call.message, text, kb, photo_id="", is_edit=True)

 

 

@dp.callback_query(F.data.startswith("farm_"))

async def cb_farm(call: types.CallbackQuery):

    _, target_str = call.data.split("_")

    target_id = int(target_str)

    if not check_owner(call, target_id):

        return await call.answer("Не трогай чужого персонажа! Напиши /card", show_alert=True)

 

    user = get_user(target_id)

    uid, uname, level, energy, last_farm, amulet_until, _ = user

    now = int(time.time())

    lvl_data = LEVELS.get(level)

    if not lvl_data:

        return await call.answer("Уровень в разработке!", show_alert=True)

 

    if now - last_farm < COOLDOWN:

        rem = (last_farm + COOLDOWN) - now

        msg = random.choice(WAIT_TEXTS).format(h=rem // 3600, m=(rem % 3600) // 60)

        return await call.answer(msg, show_alert=True)

 

    gain = random.randint(50, 150) if amulet_until > now else random.randint(1, 50)

    new_energy = min(energy + gain, lvl_data.get("need"))

    cur.execute("UPDATE users SET energy = ?, last_farm = ?, notified = 0 WHERE user_id = ?", (new_energy, now, uid))

    db.commit()

 

    referrer_id = process_referral_reward(uid)

    if referrer_id:

        try:

            await bot.send_message(referrer_id, f"🎉 <b>Твой ученик @{uname} прошёл первую тренировку!</b>\nТебе начислено <b>+50⚡</b> к текущему герою!", parse_mode="HTML")

        except Exception:

            pass

 

    await call.answer(random.choice(FARM_TEXTS).format(gain=gain), show_alert=True)

    await send_or_edit_card(call.message, get_user(uid), is_edit=True)

@dp.callback_query(F.data.startswith("claim_"))

async def cb_claim(call: types.CallbackQuery):

    _, target_str = call.data.split("_")

    target_id = int(target_str)

    if not check_owner(call, target_id):

        return await call.answer("Это чужой приз!", show_alert=True)

 

    user = get_user(target_id)

    uid, uname, level, energy, _, _, _ = user

    lvl_data = LEVELS.get(level)

    if not lvl_data or energy < lvl_data.get("need"):

        return await call.answer("Сначала докачай энергию до конца!", show_alert=True)

 

    reward_name = lvl_data.get("reward")

    cur.execute("INSERT INTO claims (user_id, username, level, reward) VALUES (?, ?, ?, ?)", (uid, uname, level, reward_name))

    cur.execute("UPDATE users SET level = ?, energy = 0, notified = 1 WHERE user_id = ?", (level + 1, uid))

    db.commit()

 

    await bot.send_message(ADMIN_ID, f"🎉 <b>НОВАЯ ЗАЯВКА НА ПОДАРОК!</b>\nИгрок: @{uname} (ID: <code>{uid}</code>)\nУровень: {level}\nПриз: <b>{reward_name}</b>\n\nУправление: /admin", parse_mode="HTML")

    await call.answer("🎉 Заявка на подарок отправлена админу!", show_alert=True)

    await send_or_edit_card(call.message, get_user(uid), is_edit=True)

 

 

@dp.callback_query(F.data.startswith("shop_"))

async def cb_shop(call: types.CallbackQuery):

    _, target_str = call.data.split("_")

    target_id = int(target_str)

    if not check_owner(call, target_id):

        return await call.answer("Открой свою лавку командой /shop", show_alert=True)

    await send_or_edit_screen(call.message, get_shop_text(), shop_keyboard(target_id), photo_id=BANNERS.get("shop"), is_edit=True)

 

 

@dp.callback_query(F.data.startswith("buy_"))

async def cb_buy(call: types.CallbackQuery):

    _, item, target_str = call.data.split("_")

    target_id = int(target_str)

    if not check_owner(call, target_id):

        return await call.answer("Это чужое меню!", show_alert=True)

 

    prices_map = {

        "amulet": ("Амулет удачи на 48ч", "Добыча 50-150 энергии без лени героя", 40),

        "case": ("Кейс с удачей", "Случайный бонус от 1 до 100 энергии прямо сейчас", 25),

        "skip": ("Попытка прорыва уровня", "Запрещённая техника мгновенного закрытия уровня", 100),

    }

    title, desc, amount = prices_map.get(item)

    await call.message.answer_invoice(title=title, description=desc, payload=item, currency="XTR", prices=[LabeledPrice(label=title, amount=amount)])

    await call.answer()

 

 

@dp.pre_checkout_query()

async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):

    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

 

 

@dp.message(F.successful_payment)

async def process_payment(message: types.Message):

    payload = message.successful_payment.invoice_payload

    paid_stars = message.successful_payment.total_amount

    uid = message.from_user.id

    user = get_user(uid, message.from_user.username)

    _, uname, level, energy, _, amulet_until, _ = user

    now = int(time.time())

 

    cur.execute("UPDATE users SET stars_spent = stars_spent + ? WHERE user_id = ?", (paid_stars, uid))

    cur.execute("INSERT INTO payments (user_id, username, item, amount, created_at) VALUES (?, ?, ?, ?, ?)", (uid, uname, payload, paid_stars, now))

    db.commit()

 

    lvl_data = LEVELS.get(level)

    if not lvl_data:

        return

    need = lvl_data.get("need")

 

    if payload == "amulet":

        new_until = max(amulet_until, now) + (48 * 3600)

        cur.execute("UPDATE users SET amulet_until = ? WHERE user_id = ?", (new_until, uid))

        db.commit()

        await message.answer("🔮 <b>Амулет удачи надет!</b> Ближайшие 48 часов герой пашет на максимум (50–150⚡)!", parse_mode="HTML")

    elif payload == "case":

        bonus = random.randint(1, 100)

        new_energy = min(energy + bonus, need)

        cur.execute("UPDATE users SET energy = ? WHERE user_id = ?", (new_energy, uid))

        db.commit()

        await message.answer(f"📦 <b>Ты вскрыл ящик и вытащил +{bonus}⚡!</b>", parse_mode="HTML")

    elif payload == "skip":

        if random.randint(1, 100) <= 5:

            cur.execute("UPDATE users SET energy = ? WHERE user_id = ?", (need, uid))

            db.commit()

            await message.answer("🔥 <b>БЕЗУМИЕ! Запрещённая техника сработала!</b> Уровень пройден! Забирай подарок в /card!", parse_mode="HTML")

        else:

            await message.answer("💨 <b>ПУФ! Техника пшикнула дымом...</b> Прорыв не удался. Попробуй ещё раз!", parse_mode="HTML")

async def notify_ready_users():

    while True:

        await asyncio.sleep(60)

        now = int(time.time())

        cur.execute("SELECT user_id, level, energy FROM users WHERE notified = 0 AND last_farm > 0 AND last_farm <= ?", (now - COOLDOWN,))

        rows = cur.fetchall()

        for uid, lvl, en in rows:

            cur.execute("UPDATE users SET notified = 1 WHERE user_id = ?", (uid,))

            db.commit()

            lvl_data = LEVELS.get(lvl)

            if not lvl_data or en >= lvl_data.get("need"):

                continue

            try:

                kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎴 Открыть карточку", callback_data=f"back_{uid}")]])

                await bot.send_message(uid, random.choice(NOTIFY_TEXTS), parse_mode="HTML", reply_markup=kb)

                await asyncio.sleep(0.05)

            except Exception:

                pass

 

 

async def auto_backup_db():

    while True:

        await asyncio.sleep(6 * 3600)

        try:

            db.commit()

            await bot.send_document(

                chat_id=ADMIN_ID,

                document=FSInputFile("game_v2.db"),

                caption="🔄 <b>Автосохранение базы данных (раз в 6 часов).</b>\nЕсли перезапустите сервер, просто перешлите этот файл обратно боту.",

                parse_mode="HTML"

            )

        except Exception:

            pass

 

 

async def set_bot_commands():

    commands = [

        BotCommand(command="card", description="🎴 Мой аниме-герой и энергия"),

        BotCommand(command="farm", description="⚡ Отправить героя на тренировку"),

        BotCommand(command="shop", description="🛒 Лавка читера (Бусты за Stars)"),

        BotCommand(command="levels", description="🗺 Дорога славы (Все 56 уровней)"),

        BotCommand(command="top", description="🏆 Топ-10 лучших Сенсеев"),

        BotCommand(command="ref", description="👥 Пригласить друга (+50⚡)"),

        BotCommand(command="promo", description="🎟 Ввести промокод"),

        BotCommand(command="rp", description="🎭 Список РП-команд для чата"),

    ]

    try:

        await bot.set_my_commands(commands)

    except Exception as e:

        logging.warning("set_bot_commands failed: %s", e)

 

 

async def main():

    await set_bot_commands()

    try:

        await bot.delete_webhook(drop_pending_updates=True)

    except Exception as e:

        logging.warning("delete_webhook failed: %s", e)

    asyncio.create_task(notify_ready_users())

    asyncio.create_task(auto_backup_db())

    await dp.start_polling(bot)

 

 

if __name__ == "__main__":

    asyncio.run(main())
