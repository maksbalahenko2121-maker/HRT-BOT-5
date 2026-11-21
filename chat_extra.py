import sqlite3

import time

from datetime import datetime

from aiogram import Bot, Dispatcher, F, types

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

 

INFO_URL = "https://telegra.ph/Oznakomlenie-11-20"

 

RANK_NAMES = {

    1: "🔰 Стажёр",

    2: "🛡️ Модер",

    3: "⚔️ Старший модератор",

    4: "👑 Заместитель",

    5: "🔱 Создатель",

}

 

PERSONAL_DOSSIER_QUOTES = [

    "Хмф, ну подумаешь, зашёл в профиль… Не зазнавайся, до Хокаге тебе ещё далеко, бака!",

    "Я-я не собирал на тебя досье специально! Просто само в базу записалось, дурак!",

    "Пф, цифры как цифры… Но если уйдёшь из чата, я, может быть, чуть-чуть соскучусь!",

    "Б-бака! Не пялься так гордо на свою статистику, тренируйся давай!",

    "Н-ну, для такого неуклюжего шиноби показатели вполне терпимые… но не расслабляйся!",

    "Ой, всё! Не смотри на меня так, будто ждёшь похвалы за эти цифры!",

    "Я запомнил(а) тебя с первого сообщения… но не думай, что ты особенный(ая), дурак!",

    "Хм! Будь благодарен(на), что я вообще веду учёт твоих похождений в этой беседе!",

    "Т-ты всё равно без моих подсказок пропадёшь, так что держись поближе к чату!",

    "Не вздумай улыбаться! Это чистая случайность, что у тебя такое неплохое досье!",

    "М-мне абсолютно всё равно, на каком ты месте в рейтинге! Понятно?!",

    "С такими темпами, может, когда-нибудь и станешь нормальным сенсеем… наверное!",

    "Б-бесишь! Почему я вечно должен(на) следить за твоей статистикой?!",

    "Хмф! Можешь считать, что тебе повезло попасть в этот чат, бака!",

    "Я вовсе не ждал(а), когда ты проверишь свой профиль! Просто держу в курсе!",

]

 

DOSSIER_CMDS = {"профиль", "кто я", "кто ты", "статус"}

VIEW_RULES_CMDS = {"правила", "/rules"}

DEL_RULES_CMDS = {"-правила", "удалить правила"}

INFO_CMDS = {"информация", "инфо", "гайд", "помощь", "/help"}

WHO_ADMIN_CMDS = {"кто админ", "кто тут админ", "админы", "состав", "администрация"}

RANKS_INFO_CMDS = {"ранги", "права", "права рангов", "полномочия"}

 

 

def ensure_extra_tables(c):

    c.execute("""

    CREATE TABLE IF NOT EXISTS chat_rules (

        chat_id INTEGER PRIMARY KEY,

        rules_text TEXT,

        updated_by TEXT,

        updated_at INTEGER

    )

    """)

    c.execute("""

    CREATE TABLE IF NOT EXISTS chat_ranks (

        chat_id INTEGER,

        user_id INTEGER,

        user_name TEXT,

        rank INTEGER DEFAULT 0,

        PRIMARY KEY (chat_id, user_id)

    )

    """)

    c.execute("""

    CREATE TABLE IF NOT EXISTS chat_warns (

        chat_id INTEGER,

        user_id INTEGER,

        user_name TEXT,

        warns_count INTEGER DEFAULT 0,

        last_reason TEXT,

        PRIMARY KEY (chat_id, user_id)

    )

    """)

    c.execute("""

    CREATE TABLE IF NOT EXISTS chat_punishments (

        chat_id INTEGER,

        user_id INTEGER,

        user_name TEXT,

        p_type TEXT,

        until_ts INTEGER,

        PRIMARY KEY (chat_id, user_id, p_type)

    )

    """)

    for col_sql in [

        "ALTER TABLE chat_members ADD COLUMN quiz_wins INTEGER DEFAULT 0",

        "ALTER TABLE chat_members ADD COLUMN first_seen_ts INTEGER DEFAULT 0",

    ]:

        try:

            c.execute(col_sql)

        except sqlite3.OperationalError:

            pass

 

 

def parse_mod_duration(args_str: str) -> tuple[int, str]:

    tokens = args_str.strip().lower().split()

    if not tokens:

        return 0, "навсегда"

    num_str = ""

    unit_str = ""

    for item in tokens:

        digits = "".join(ch for ch in item if ch.isdigit())

        letters = "".join(ch for ch in item if ch.isalpha())

        if digits and not num_str:

            num_str = digits

        if letters and not unit_str:

            unit_str = letters

    if not num_str:

        return 0, "навсегда"

    val = int(num_str)

    if val <= 0:

        return 0, "навсегда"

    if unit_str.startswith("с") or unit_str.startswith("s"):

        return max(val, 35), f"{val} сек."

    if unit_str.startswith("ч") or unit_str.startswith("h"):

        return val * 3600, f"{val} ч."

    if unit_str.startswith("д") or unit_str.startswith("d"):

        return val * 86400, f"{val} дн."

    if unit_str.startswith("н") or unit_str.startswith("w"):

        return val * 604800, f"{val} нед."

    if unit_str.startswith("мес") or unit_str.startswith("mo"):

        return val * 2592000, f"{val} мес."

    return val * 60, f"{val} мин."

def setup_chat_extra(dp: Dispatcher, bot: Bot, cur, db, admin_id: int, levels: dict, get_user_fn, active_quiz_dict: dict = None, start_fn=None, road_fn=None, top_fn=None, promo_fn=None):

    if active_quiz_dict is None:

        active_quiz_dict = {}

 

    admin_waiting_find = set()

 

    async def get_member_rank(chat_id: int, user_id: int) -> int:

        if user_id == admin_id:

            return 5

        try:

            member = await bot.get_chat_member(chat_id, user_id)

            if member.status == "creator":

                return 5

        except Exception:

            member = None

 

        with sqlite3.connect("game_v2.db") as conn:

            c = conn.cursor()

            ensure_extra_tables(c)

            c.execute("SELECT rank FROM chat_ranks WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))

            row = c.fetchone()

            if row is not None:

                return int(row[0])

 

        if member and member.status == "administrator":

            return 3

        return 0

 

    async def is_boss_user(chat_id: int, user_id: int, min_rank: int = 3) -> bool:

        rank = await get_member_rank(chat_id, user_id)

        return rank >= min_rank

 

    async def resolve_target_user(message: types.Message, arg_text: str):

        cid = message.chat.id

        if message.reply_to_message and message.reply_to_message.from_user:

            u = message.reply_to_message.from_user

            clean_n = (u.full_name or u.username or "Шиноби").replace("<", "").replace(">", "")

            return u.id, clean_n, arg_text.strip()

 

        tokens = arg_text.strip().split()

        if not tokens:

            return None, "", ""

 

        if message.entities:

            for ent in message.entities:

                if ent.type == "text_mention" and ent.user:

                    u = ent.user

                    clean_n = (u.full_name or u.username or "Шиноби").replace("<", "").replace(">", "")

                    rest = " ".join(tokens[1:]) if len(tokens) > 1 else ""

                    return u.id, clean_n, rest

 

        target_token = tokens[0].replace("<", "").replace(">", "")

        rest_str = " ".join(tokens[1:]) if len(tokens) > 1 else ""

 

        if target_token.startswith("@"):

            uname_clean = target_token[1:].lower()

            with sqlite3.connect("game_v2.db") as conn:

                c = conn.cursor()

                ensure_extra_tables(c)

                c.execute("SELECT user_id, username FROM users WHERE LOWER(username) = ?", (uname_clean,))

                row = c.fetchone()

                if not row:

                    c.execute("SELECT user_id, user_name FROM chat_members WHERE chat_id = ? AND LOWER(user_name) = ?", (cid, uname_clean))

                    row = c.fetchone()

                if not row:

                    c.execute("SELECT user_id, user_name FROM chat_ranks WHERE chat_id = ? AND LOWER(user_name) = ?", (cid, uname_clean))

                    row = c.fetchone()

            if row:

                return int(row[0]), str(row[1]).replace("<", "").replace(">", ""), rest_str

 

        if target_token.isdigit():

            uid_int = int(target_token)

            try:

                m = await bot.get_chat_member(cid, uid_int)

                clean_n = (m.user.full_name or m.user.username or "Шиноби").replace("<", "").replace(">", "")

                return uid_int, clean_n, rest_str

            except Exception:

                return uid_int, f"ID {uid_int}", rest_str

 

        return None, "", arg_text

 

    async def handle_ranks_info(message: types.Message):

        info_msg = (

            "🎖 <b>ИЕРАРХИЯ И ПРАВА РАНГОВ В ЧАТЕ</b>\n"

            "━━━━━━━━━━━━━━\n"

            "<b>1 ранг — 🔰 Стажёр:</b>\n"

            "• Может выдавать <b>только варны</b> (<code>варн [причина]</code>)\n\n"

            "<b>2 ранг — 🛡️ Модер:</b>\n"

            "• Выдача варнов и мутов (<code>варн</code>, <code>мут [время]</code>)\n\n"

            "<b>3 ранг — ⚔️ Старший модератор:</b>\n"

            "• Выдача и <b>снятие</b> варнов и мутов (<code>варн</code>, <code>снять варн</code>, <code>мут</code>, <code>размут</code>) + правила (<code>+правила</code>)\n\n"

            "<b>4 ранг — 👑 Заместитель:</b>\n"

            "• Всё выше + выдача и снятие банов (<code>бан</code>, <code>разбан</code>) + удаление правил (<code>-правила</code>)\n\n"

            "<b>5 ранг — 🔱 Создатель:</b>\n"

            "• Полный доступ ко всему + <b>назначение, повышение и снятие любых рангов (1–4)</b>\n"

            "━━━━━━━━━━━━━━\n"

            "<i>Посмотреть состав: <code>кто админ</code></i>"

        )

        await message.reply(info_msg, parse_mode="HTML")

 

    async def handle_rank_change(message: types.Message, mode: str, arg_text: str):

        cid = message.chat.id

        sender_id = message.from_user.id

        sender_rank = await get_member_rank(cid, sender_id)

 

        if sender_rank < 5:

            return await message.reply("⛔ <b>Выдавать, повышать и понижать ранги может ТОЛЬКО Создатель беседы (5 ранг)!</b>", parse_mode="HTML")

 

        target_id, target_name, rest = await resolve_target_user(message, arg_text)

        if not target_id:

            return await message.reply(

                "👑 <b>Управление рангами (только Создатель):</b>\n"

                "Ответь на сообщение игрока или укажи <code>@ник</code>:\n"

                "• <code>повысить</code> (или <code>повысить 1-4</code>)\n"

                "• <code>понизить</code> / <code>снять админа</code>",

                parse_mode="HTML"

            )

 

        if target_id == bot.id:

            return await message.reply("😤 Я и так главный Цундере-бот этой беседы, бака!")

        if target_id == sender_id:

            return await message.reply("😒 Ты и так Создатель этой беседы, дурак!")

 

        target_rank = await get_member_rank(cid, target_id)

        if target_rank >= 5:

            return await message.reply("🛡 Нельзя изменить ранг Создателю!")

 

        if mode == "remove":

            new_rank = 0

        elif mode == "promote":

            if rest.isdigit() and 1 <= int(rest) <= 4:

                new_rank = int(rest)

            else:

                new_rank = min(4, target_rank + 1)

        else:

            if rest.isdigit() and 0 <= int(rest) <= 3:

                new_rank = int(rest)

            else:

                new_rank = max(0, target_rank - 1)

 

        with sqlite3.connect("game_v2.db") as conn:

            conn.execute("PRAGMA busy_timeout=5000;")

            c = conn.cursor()

            ensure_extra_tables(c)

            if new_rank == 0:

                c.execute("INSERT OR REPLACE INTO chat_ranks (chat_id, user_id, user_name, rank) VALUES (?, ?, ?, 0)", (cid, target_id, target_name))

            else:

                c.execute(

                    "INSERT OR REPLACE INTO chat_ranks (chat_id, user_id, user_name, rank) VALUES (?, ?, ?, ?)",

                    (cid, target_id, target_name, new_rank)

                )

            conn.commit()

 

        t_link = f'<a href="tg://user?id={target_id}"><b>{target_name}</b></a>'

        if new_rank == 0:

            await message.reply(f"📉 {t_link} разжалован(а) до обычного <b>Участника беседы</b>!", parse_mode="HTML")

        else:

            r_title = RANK_NAMES.get(new_rank, f"{new_rank} ранг")

            arrow = "📈" if new_rank > target_rank else "📉"

            await message.reply(

                f"{arrow} <b>Ранг обновлён Создателем!</b>\n"

                f"👤 Игрок: {t_link}\n"

                f"🎖 Новая должность: <b>{r_title} ({new_rank} ранг)</b>",

                parse_mode="HTML"

            )

    async def handle_warn_action(message: types.Message, mode: str, arg_text: str):

        cid = message.chat.id

        sender_id = message.from_user.id

        sender_rank = await get_member_rank(cid, sender_id)

 

        if mode == "unwarn" and sender_rank < 3:

            return await message.reply("⛔ <b>Снимать варны могут модераторы от 3 ранга (⚔️ Старший модератор) и выше!</b>", parse_mode="HTML")

        if mode == "warn" and sender_rank < 1:

            return await message.reply("⛔ <b>Выдавать варны могут модераторы от 1 ранга (🔰 Стажёр) и выше!</b>", parse_mode="HTML")

 

        target_id, target_name, rest = await resolve_target_user(message, arg_text)

        if not target_id:

            return await message.reply(

                "⚠️ <b>Система предупреждений (варнов):</b>\n"

                "Ответь на сообщение нарушителя или укажи <code>@ник</code>:\n"

                "• <code>варн [причина]</code> (от 1 ранга, 3 варна = мут на 24ч)\n"

                "• <code>снять варн</code> (от 3 ранга) / <code>варны @ник</code>",

                parse_mode="HTML"

            )

 

        if target_id == bot.id:

            return await message.reply("😤 Б-бака! Не смей выписывать варн великому боту!")

        if target_id == sender_id:

            return await message.reply("😒 Нельзя выдать или снять варн самому себе!")

 

        target_rank = await get_member_rank(cid, target_id)

        if target_rank >= sender_rank:

            return await message.reply("🛡 <b>Нельзя применить это действие к тому, кто равен тебе или старше по рангу!</b>", parse_mode="HTML")

 

        t_link = f'<a href="tg://user?id={target_id}"><b>{target_name}</b></a>'

 

        with sqlite3.connect("game_v2.db") as conn:

            conn.execute("PRAGMA busy_timeout=5000;")

            c = conn.cursor()

            ensure_extra_tables(c)

            c.execute("SELECT warns_count FROM chat_warns WHERE chat_id = ? AND user_id = ?", (cid, target_id))

            row = c.fetchone()

            cur_warns = int(row[0]) if row else 0

 

            if mode == "unwarn":

                if cur_warns <= 0:

                    return await message.reply(f"🟢 У игрока {t_link} и так <b>0 / 3 варнов</b>!", parse_mode="HTML")

                new_w = cur_warns - 1

                if new_w == 0:

                    c.execute("DELETE FROM chat_warns WHERE chat_id = ? AND user_id = ?", (cid, target_id))

                else:

                    c.execute("UPDATE chat_warns SET warns_count = ? WHERE chat_id = ? AND user_id = ?", (new_w, cid, target_id))

                conn.commit()

                return await message.reply(

                    f"✅ С игрока {t_link} снято 1 предупреждение!\n"

                    f"⚠️ Активные варны: <b>{new_w} / 3</b>",

                    parse_mode="HTML"

                )

 

            reason = rest.replace("<", "").replace(">", "").strip() or "Нарушение правил чата"

            new_w = cur_warns + 1

 

            if new_w >= 3:

                c.execute("DELETE FROM chat_warns WHERE chat_id = ? AND user_id = ?", (cid, target_id))

                until_ts = int(time.time()) + 86400

                try:

                    perms = types.ChatPermissions(can_send_messages=False)

                    await bot.restrict_chat_member(cid, target_id, permissions=perms, until_date=until_ts)

                    c.execute(

                        "INSERT OR REPLACE INTO chat_punishments (chat_id, user_id, user_name, p_type, until_ts) VALUES (?, ?, ?, 'mute', ?)",

                        (cid, target_id, target_name, until_ts)

                    )

                    punish_note = "🔇 Нарушитель автоматически отправлен в <b>мут на 24 часа</b>, счётчик варнов обнулён!"

                except Exception as e:

                    punish_note = f"⚠️ Не удалось выдать авто-мут (проверь права админа у бота): <code>{e}</code>"

                conn.commit()

 

                return await message.reply(

                    f"🚨 <b>ПОСЛЕДНЕЕ ПРЕДУПРЕЖДЕНИЕ (3 / 3)!</b>\n"

                    f"👤 Нарушитель: {t_link}\n"

                    f"📝 Причина: <i>{reason}</i>\n\n"

                    f"{punish_note}",

                    parse_mode="HTML"

                )

 

            c.execute(

                "INSERT OR REPLACE INTO chat_warns (chat_id, user_id, user_name, warns_count, last_reason) VALUES (?, ?, ?, ?, ?)",

                (cid, target_id, target_name, new_w, reason)

            )

            conn.commit()

 

        await message.reply(

            f"⚠️ <b>ВЫДАНО ПРЕДУПРЕЖДЕНИЕ ({new_w} / 3)!</b>\n"

            f"👤 Нарушитель: {t_link}\n"

            f"📝 Причина: <i>{reason}</i>\n"

            f"<i>При 3 из 3 варнов последует авто-мут на 24ч!</i>",

            parse_mode="HTML"

        )

 

    async def handle_warns_query(message: types.Message, arg_text: str):

        cid = message.chat.id

        target_id, target_name, _ = await resolve_target_user(message, arg_text)

 

        with sqlite3.connect("game_v2.db") as conn:

            c = conn.cursor()

            ensure_extra_tables(c)

 

            if target_id:

                c.execute("SELECT warns_count, last_reason FROM chat_warns WHERE chat_id = ? AND user_id = ?", (cid, target_id))

                row = c.fetchone()

                t_link = f'<a href="tg://user?id={target_id}"><b>{target_name}</b></a>'

                if not row or int(row[0]) <= 0:

                    return await message.reply(f"🟢 У игрока {t_link} сейчас <b>0 / 3 варнов</b>!", parse_mode="HTML")

                w_cnt, rsn = row

                safe_r = str(rsn or "—").replace("<", "").replace(">", "")

                return await message.reply(

                    f"⚠️ <b>ПРЕДУПРЕЖДЕНИЯ ИГРОКА</b>\n"

                    f"👤 Игрок: {t_link}\n"

                    f"📊 Варны: <b>{w_cnt} / 3</b>\n"

                    f"📝 Последняя причина: <i>{safe_r}</i>",

                    parse_mode="HTML"

                )

 

            c.execute("SELECT user_id, user_name, warns_count, last_reason FROM chat_warns WHERE chat_id = ? AND warns_count > 0 ORDER BY warns_count DESC", (cid,))

            rows = c.fetchall()

 

        if not rows:

            return await message.reply("🟢 <b>В этом чате сейчас ни у кого нет предупреждений (варнов)!</b>", parse_mode="HTML")

 

        lines = ["⚠️ <b>СПИСОК НАРУШИТЕЛЕЙ С ВАРНАМИ</b>", "━━━━━━━━━━━━━━"]

        for idx, (uid, uname, w_cnt, rsn) in enumerate(rows, 1):

            safe_n = str(uname).replace("<", "").replace(">", "")

            safe_r = str(rsn or "—").replace("<", "").replace(">", "")

            lines.append(f"{idx}. <a href=\"tg://user?id={uid}\"><b>{safe_n}</b></a> — <b>{w_cnt}/3</b> <i>({safe_r})</i>")

 

        await message.reply("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)

    async def handle_ranked_moderation(message: types.Message, cmd: str, arg_text: str):

        cid = message.chat.id

        sender_id = message.from_user.id

        sender_rank = await get_member_rank(cid, sender_id)

 

        req_ranks = {

            "мут": (2, "🛡️ Модер (2 ранг)"),

            "размут": (3, "⚔️ Старший модератор (3 ранг)"),

            "бан": (4, "👑 Заместитель (4 ранг)"),

            "разбан": (4, "👑 Заместитель (4 ранг)"),

        }

        min_r, r_label = req_ranks[cmd]

        if sender_rank < min_r:

            return await message.reply(f"⛔ <b>Команда <code>{cmd}</code> доступна только с ранга: {r_label} и выше!</b>", parse_mode="HTML")

 

        target_id, target_name, rest = await resolve_target_user(message, arg_text)

        if not target_id:

            return await message.reply(f"📌 Ответь на сообщение игрока или укажи <code>@ник</code> после команды <code>{cmd}</code>!", parse_mode="HTML")

 

        if target_id == bot.id:

            return await message.reply("😤 Б-бака! Я сам себя наказывать не буду!")

        if target_id == sender_id:

            return await message.reply("😒 Нельзя применить это действие к самому себе!")

 

        target_rank = await get_member_rank(cid, target_id)

        if target_rank >= sender_rank:

            return await message.reply("🛡 <b>Нельзя применить это действие к тому, кто равен тебе или старше по рангу!</b>", parse_mode="HTML")

 

        u_link=f'<b>{safe_n}</b>"

        now = int(time.time())

 

        try:

            with sqlite3.connect("game_v2.db") as conn:

                conn.execute("PRAGMA busy_timeout=5000;")

                c = conn.cursor()

                ensure_extra_tables(c)

 

                if cmd == "мут":

                    seconds, label = parse_mod_duration(rest)

                    if seconds == 0:

                        seconds, label = 3600, "60 мин."

                    until = now + seconds

                    perms = types.ChatPermissions(can_send_messages=False)

                    await bot.restrict_chat_member(cid, target_id, permissions=perms, until_date=until)

                    c.execute("INSERT OR REPLACE INTO chat_punishments (chat_id, user_id, user_name, p_type, until_ts) VALUES (?, ?, ?, 'mute', ?)", (cid, target_id, target_name, until))

                    conn.commit()

                    await message.reply(f"🔇 <b>Техника теневого молчания!</b> {t_link} запечатал(а) рот <b>на {label}</b>!", parse_mode="HTML")

 

                elif cmd == "размут":

                    perms = types.ChatPermissions(can_send_messages=True, can_send_audios=True, can_send_documents=True, can_send_photos=True, can_send_videos=True, can_send_video_notes=True, can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True)

                    await bot.restrict_chat_member(cid, target_id, permissions=perms)

                    c.execute("DELETE FROM chat_punishments WHERE chat_id = ? AND user_id = ? AND p_type = 'mute'", (cid, target_id))

                    conn.commit()

                    await message.reply(f"🔊 <b>Кай! Гендзюцу рассеяно!</b> С {t_link} снят мут, снова можно болтать!", parse_mode="HTML")

 

                elif cmd == "бан":

                    seconds, label = parse_mod_duration(rest)

                    until = (now + seconds) if seconds > 0 else 0

                    dur_text = f"на {label}" if seconds > 0 else "навсегда"

                    if seconds > 0:

                        await bot.ban_chat_member(cid, target_id, until_date=until)

                    else:

                        await bot.ban_chat_member(cid, target_id)

                    c.execute("INSERT OR REPLACE INTO chat_punishments (chat_id, user_id, user_name, p_type, until_ts) VALUES (?, ?, ?, 'ban', ?)", (cid, target_id, target_name, until))

                    conn.commit()

                    await message.reply(f"🔨 <b>Техника запечатывания Шинигами!</b> {t_link} изгнан(а) из беседы <b>{dur_text}</b>!", parse_mode="HTML")

 

                elif cmd == "разбан":

                    await bot.unban_chat_member(cid, target_id, only_if_banned=True)

                    c.execute("DELETE FROM chat_punishments WHERE chat_id = ? AND user_id = ? AND p_type = 'ban'", (cid, target_id))

                    conn.commit()

                    await message.reply(f"🕊 <b>Эдо Тенсей!</b> {t_link} разбанен(а) и снова может вернуться в беседу!", parse_mode="HTML")

        except Exception as e:

            await message.reply(f"⚠️ <b>Не удалось выполнить технику!</b>\nПроверь права админа у бота. Причина: <code>{e}</code>", parse_mode="HTML")

 

    async def handle_punishments_list_extra(message: types.Message, p_type: str):

        cid = message.chat.id

        now = int(time.time())

        with sqlite3.connect("game_v2.db") as conn:

            c = conn.cursor()

            ensure_extra_tables(c)

            c.execute("DELETE FROM chat_punishments WHERE chat_id = ? AND until_ts > 0 AND until_ts <= ?", (cid, now))

            conn.commit()

            c.execute("SELECT user_id, user_name, until_ts FROM chat_punishments WHERE chat_id = ? AND p_type = ?", (cid, p_type))

            rows = c.fetchall()

 

        if not rows:

            empty_msg = "🟢 <b>В этом чате сейчас никто не сидит в муте!</b>" if p_type == "mute" else "🟢 <b>Список забаненных в этом чате пуст!</b>"

            return await message.reply(empty_msg, parse_mode="HTML")

 

        header = "🔇 <b>СПИСОК ЗАМУЧЕННЫХ В ЧАТЕ:</b>\n━━━━━━━━━━━━━━\n" if p_type == "mute" else "🔨 <b>СПИСОК ЗАБАНЕННЫХ В ЧАТЕ:</b>\n━━━━━━━━━━━━━━\n"

        lines = [header]

        for idx, (uid, uname, until_ts) in enumerate(rows, 1):

            safe_n = str(uname).replace("<", "").replace(">", "")

            time_left = "навсегда" if until_ts == 0 else f"до <code>{datetime.fromtimestamp(until_ts).strftime('%d.%m в %H:%M')}</code>"

            lines.append(f"{idx}. <a href=\"tg://user?id={uid}\"><b>{safe_n}</b></a> — {time_left}")

 

        await message.reply("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)

 

    async def handle_who_admin(message: types.Message):

        cid = message.chat.id

        admins_by_rank = {5: [], 4: [], 3: [], 2: [], 1: []}

        seen_ids = set()

 

        with sqlite3.connect("game_v2.db") as conn:

            c = conn.cursor()

            ensure_extra_tables(c)

            c.execute("SELECT user_id, user_name, rank FROM chat_ranks WHERE chat_id = ? AND rank > 0", (cid,))

            for uid, uname, rnk in c.fetchall():

                if rnk in admins_by_rank:

                    safe_n = str(uname).replace("<", "").replace(">", "")

                    admins_by_rank[rnk].append(f"• <a href=\"tg://user?id={uid}\"><b>{safe_n}</b></a>")

                    seen_ids.add(uid)

 

        try:

            tg_admins = await bot.get_chat_administrators(cid)

            for m in tg_admins:

                u = m.user

                if u.is_bot or u.id in seen_ids:

                    continue

                safe_n = (u.full_name or u.username or "Админ").replace("<", "").replace(">", "")

                if m.status == "creator" or u.id == admin_id:

                    admins_by_rank[5].append(f"• <a href=\"tg://user?id={u.id}\"><b>{safe_n}</b></a>")

                else:

                    admins_by_rank[3].append(f"• <a href=\"tg://user?id={u.id}\"><b>{safe_n}</b></a>")

                seen_ids.add(u.id)

        except Exception:

            pass

 

        lines = ["👑 <b>АДМИНИСТРАЦИЯ БЕСЕДЫ</b>", "━━━━━━━━━━━━━━"]

        has_any = False

        for rnk in (5, 4, 3, 2, 1):

            if admins_by_rank[rnk]:

                has_any = True

                lines.append(f"\n<b>{RANK_NAMES[rnk]} ({rnk} ранг):</b>")

                lines.extend(admins_by_rank[rnk])

 

        if not has_any:

            lines.append("Список администрации пока пуст!")

        lines.append("\n━━━━━━━━━━━━━━")

        lines.append("<i>Посмотреть права рангов: <code>ранги</code></i>")

 

        await message.reply("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)

    def build_stat_users_text() -> str:

        now = int(time.time())

        with sqlite3.connect("game_v2.db") as conn:

            c = conn.cursor()

            c.execute("SELECT level, COUNT(*) FROM users GROUP BY level ORDER BY level ASC LIMIT 15")

            lvl_rows = c.fetchall()

            c.execute("SELECT COUNT(*) FROM users WHERE amulet_until > ?", (now,))

            (active_amulets,) = c.fetchone()

            c.execute("SELECT COUNT(*), SUM(CASE WHEN rewarded = 1 THEN 1 ELSE 0 END) FROM referrals")

            tot_refs, act_refs = c.fetchone()

 

            c.execute("SELECT username, level, energy FROM users")

            almost_ready = []

            for u_name, u_lvl, u_en in c.fetchall():

                l_data = levels.get(u_lvl)

                if l_data and u_en >= l_data.get("need") * 0.8:

                    almost_ready.append(f"∙ @{u_name} (Ур.{u_lvl}: {u_en}/{l_data.get('need')}⚡)")

 

        lvl_text = "\n".join(f"∙ Ур. {l}: <b>{cnt} чел.</b>" for l, cnt in lvl_rows) or "Пусто"

        ready_text = "\n".join(almost_ready[:10]) if almost_ready else "Пока никого"

        conv = int(((act_refs or 0) / tot_refs) * 100) if tot_refs else 0

 

        return (

            f"📊 <b>АНАЛИТИКА ИГРОКОВ</b>\n"

            f"━━━━━━━━━━━━━━\n"

            f"🔮 Активных амулетов: <b>{active_amulets}</b>\n"

            f"🤝 Рефералы: <b>{act_refs or 0}</b> из <b>{tot_refs or 0}</b> (конверсия <b>{conv}%</b>)\n\n"

            f"🪜 <b>Распределение по уровням:</b>\n{lvl_text}\n\n"

            f"🔥 <b>Почти закрыли уровень (80%+):</b>\n{ready_text}"

        )

 

    def build_stat_chats_text() -> str:

        with sqlite3.connect("game_v2.db") as conn:

            c = conn.cursor()

            ensure_extra_tables(c)

            c.execute("SELECT COALESCE(SUM(msg_total), 0), COALESCE(SUM(msg_today), 0), COALESCE(SUM(quiz_wins), 0) FROM chat_members")

            m_tot, m_tod, q_tot = c.fetchone()

            c.execute("""

                SELECT g.title, g.members_count, COALESCE(SUM(cm.msg_today), 0), COALESCE(SUM(cm.msg_total), 0)

                FROM groups g

                LEFT JOIN chat_members cm ON g.chat_id = cm.chat_id

                GROUP BY g.chat_id

                ORDER BY SUM(cm.msg_today) DESC, SUM(cm.msg_total) DESC LIMIT 10

            """)

            top_chats = c.fetchall()

            c.execute("SELECT user_name, SUM(msg_total) as s FROM chat_members GROUP BY user_id ORDER BY s DESC LIMIT 5")

            top_talkers = c.fetchall()

 

        chats_list = "\n".join(

            f"{i}. <b>{(t or 'Чат')[:20]}</b> (👥{mc}): +{td} сег. / {tt} всего"

            for i, (t, mc, td, tt) in enumerate(top_chats, 1)

        ) or "Нет данных"

        talkers_list = "\n".join(

            f"{i}. <b>{un}</b> — {ms} сообщ."

            for i, (un, ms) in enumerate(top_talkers, 1)

        ) or "Нет данных"

 

        return (

            f"💬 <b>ДЕТАЛЬНАЯ СТАТИСТИКА ЧАТОВ</b>\n"

            f"━━━━━━━━━━━━━━\n"

            f"📨 Сообщений сегодня: <b>+{m_tod}</b> (всего: <b>{m_tot}</b>)\n"

            f"🧠 Угадано в викторинах: <b>{q_tot} аниме</b>\n\n"

            f"🏆 <b>Топ-10 активных бесед:</b>\n{chats_list}\n\n"

            f"👑 <b>Главные болтуны по всем чатам:</b>\n{talkers_list}"

        )

 

    def build_admin_player_card(target_uid: int):

        with sqlite3.connect("game_v2.db") as conn:

            c = conn.cursor()

            ensure_extra_tables(c)

            c.execute("SELECT user_id, username, level, energy, amulet_until, stars_spent FROM users WHERE user_id = ?", (target_uid,))

            u_row = c.fetchone()

            if not u_row:

                return None, None

 

            f_uid, f_uname, f_lvl, f_en, f_am, f_stars = u_row

            c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND rewarded = 1", (f_uid,))

            (f_refs,) = c.fetchone()

            c.execute("""

                SELECT g.title, cm.msg_total, cm.quiz_wins

                FROM chat_members cm

                LEFT JOIN groups g ON cm.chat_id = g.chat_id

                WHERE cm.user_id = ?

                ORDER BY cm.msg_total DESC LIMIT 5

            """, (f_uid,))

            u_chats = c.fetchall()

 

        now = int(time.time())

        am_str = "🔥 Активен" if f_am > now else "Нет"

        lvl_data = levels.get(f_lvl)

        need_str = f"/{lvl_data.get('need')}⚡" if lvl_data else "⚡"

        chats_str = "\n".join(

            f"∙ <b>{(gt or 'Чат')[:22]}</b>: {mt} сообщ., {qw} викт."

            for gt, mt, qw in u_chats

        ) if u_chats else "Не замечен в беседах"

 

        text = (

            f"🕵️ <b>РЕДАКТОР ИГРОКА (АДМИН)</b>\n"

            f"━━━━━━━━━━━━━━\n"

            f"👤 @{f_uname} (ID: <code>{f_uid}</code>)\n"

            f"🦸 Уровень: <b>{f_lvl}</b> ({f_en}{need_str})\n"

            f"🔮 Амулет: {am_str} | ⭐ Потрачено: <b>{f_stars} ⭐</b>\n"

            f"🤝 Привёл друзей: <b>{f_refs} чел.</b>\n\n"

            f"💬 <b>Активность в беседах:</b>\n{chats_str}"

        )

        kb = InlineKeyboardMarkup(inline_keyboard=[

            [

                InlineKeyboardButton(text="➕ 50⚡", callback_data=f"adm_ed:en50:{f_uid}"),

                InlineKeyboardButton(text="➖ 50⚡", callback_data=f"adm_ed:en_50:{f_uid}"),

                InlineKeyboardButton(text="➕ 500⚡", callback_data=f"adm_ed:en500:{f_uid}"),

            ],

            [

                InlineKeyboardButton(text="⬆️ +1 Ур.", callback_data=f"adm_ed:lvl1:{f_uid}"),

                InlineKeyboardButton(text="⬇️ -1 Ур.", callback_data=f"adm_ed:lvl_1:{f_uid}"),

                InlineKeyboardButton(text="🔮 Амулет 48ч", callback_data=f"adm_ed:am48:{f_uid}"),

            ],

            [

                InlineKeyboardButton(text="🔄 Обнулить игрока", callback_data=f"adm_ed:reset:{f_uid}"),

            ]

        ])

        return text, kb

    @dp.callback_query(F.data == "adm_extra_find")

    async def cb_adm_extra_find(call: types.CallbackQuery):

        if call.from_user.id != admin_id:

            return

        admin_waiting_find.add(admin_id)

        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="adm_extra_cancel")]])

        await call.message.edit_text(

            "🕵️ <b>Поиск и изменение игрока</b>\n\n"

            "Отправь следующим сообщением <code>@ник</code> или <code>ID</code> игрока:",

            parse_mode="HTML",

            reply_markup=kb

        )

 

    @dp.callback_query(F.data == "adm_extra_cancel")

    async def cb_adm_extra_cancel(call: types.CallbackQuery):

        admin_waiting_find.discard(admin_id)

        await call.message.edit_text("❌ Поиск отменён. Вернуться в меню: /admin")

 

    @dp.callback_query(F.data == "adm_extra_users")

    async def cb_adm_extra_users(call: types.CallbackQuery):

        if call.from_user.id != admin_id:

            return

        await call.message.answer(build_stat_users_text(), parse_mode="HTML")

        await call.answer()

 

    @dp.callback_query(F.data == "adm_extra_chats")

    async def cb_adm_extra_chats(call: types.CallbackQuery):

        if call.from_user.id != admin_id:

            return

        await call.message.answer(build_stat_chats_text(), parse_mode="HTML")

        await call.answer()

 

    @dp.callback_query(F.data.startswith("adm_ed:"))

    async def cb_admin_edit_player(call: types.CallbackQuery):

        if call.from_user.id != admin_id:

            return

        _, action, uid_str = call.data.split(":")

        t_uid = int(uid_str)

        now = int(time.time())

 

        with sqlite3.connect("game_v2.db") as conn:

            conn.execute("PRAGMA busy_timeout=5000;")

            c = conn.cursor()

            c.execute("SELECT level, energy, amulet_until FROM users WHERE user_id = ?", (t_uid,))

            row = c.fetchone()

            if not row:

                return await call.answer("Игрок не найден!", show_alert=True)

            lvl, en, am_until = row

            max_lvl = len(levels)

 

            if action == "en50":

                c.execute("UPDATE users SET energy = ? WHERE user_id = ?", (en + 50, t_uid))

                note = "Начислено +50⚡"

            elif action == "en_50":

                c.execute("UPDATE users SET energy = ? WHERE user_id = ?", (max(0, en - 50), t_uid))

                note = "Снято -50⚡"

            elif action == "en500":

                c.execute("UPDATE users SET energy = ? WHERE user_id = ?", (en + 500, t_uid))

                note = "Начислено +500⚡"

            elif action == "lvl1":

                c.execute("UPDATE users SET level = ?, energy = 0 WHERE user_id = ?", (min(max_lvl, lvl + 1), t_uid))

                note = "Уровень повышен (+1)"

            elif action == "lvl_1":

                c.execute("UPDATE users SET level = ?, energy = 0 WHERE user_id = ?", (max(1, lvl - 1), t_uid))

                note = "Уровень понижен (-1)"

            elif action == "am48":

                new_am = max(am_until, now) + (48 * 3600)

                c.execute("UPDATE users SET amulet_until = ? WHERE user_id = ?", (new_am, t_uid))

                note = "Выдан Амулет на 48ч"

            elif action == "reset":

                c.execute("UPDATE users SET level = 1, energy = 0, amulet_until = 0 WHERE user_id = ?", (t_uid,))

                note = "Прогресс обнулён (Ур. 1, 0⚡)"

            else:

                note = "Готово"

            conn.commit()

 

        card_text, card_kb = build_admin_player_card(t_uid)

        if card_text:

            try:

                await call.message.edit_text(card_text, reply_markup=card_kb, parse_mode="HTML")

            except Exception:

                pass

        await call.answer(f"✅ {note}", show_alert=True)

 

    async def handle_set_rules(message: types.Message, raw_text: str):

        cid = message.chat.id

        uid = message.from_user.id

 

        if not await is_boss_user(cid, uid, min_rank=3):

            return await message.reply("⛔ <b>Устанавливать правила могут модераторы от 3 ранга (⚔️ Старший модератор) и выше!</b>", parse_mode="HTML")

 

        if not raw_text:

            return await message.reply(

                "📜 <b>Как создать правила чата:</b>\n"

                "Напиши <code>+правила</code>, нажми <b>Enter</b> и распиши пункты с новой строки:\n\n"

                "<code>+правила\n1. Не спамить\n2. Уважать участников</code>",

                parse_mode="HTML"

            )

 

        safe_rules = raw_text.replace("<", "").replace(">", "")

        author_name = (message.from_user.full_name or message.from_user.username or "Админ").replace("<", "").replace(">", "")

        now = int(time.time())

 

        with sqlite3.connect("game_v2.db") as conn:

            conn.execute("PRAGMA busy_timeout=5000;")

            c = conn.cursor()

            ensure_extra_tables(c)

            c.execute(

                "INSERT OR REPLACE INTO chat_rules (chat_id, rules_text, updated_by, updated_at) VALUES (?, ?, ?, ?)",

                (cid, safe_rules, author_name, now)

            )

            conn.commit()

 

        await message.reply(

            "✅ <b>Правила беседы успешно сохранены!</b>\n"

            "Теперь любой участник может открыть их словом <code>правила</code>.",

            parse_mode="HTML"

        )

 

    async def handle_del_rules(message: types.Message):

        cid = message.chat.id

        uid = message.from_user.id

 

        if not await is_boss_user(cid, uid, min_rank=4):

            return await message.reply("⛔ <b>Удалять правила могут админы от 4 ранга (👑 Заместитель) и Создатель!</b>", parse_mode="HTML")

 

        with sqlite3.connect("game_v2.db") as conn:

            conn.execute("PRAGMA busy_timeout=5000;")

            c = conn.cursor()

            ensure_extra_tables(c)

            c.execute("DELETE FROM chat_rules WHERE chat_id = ?", (cid,))

            conn.commit()

 

        await message.reply("🗑 <b>Правила этого чата удалены!</b>", parse_mode="HTML")

 

    async def handle_show_rules(message: types.Message):

        cid = message.chat.id

        with sqlite3.connect("game_v2.db") as conn:

            conn.execute("PRAGMA busy_timeout=5000;")

            c = conn.cursor()

            ensure_extra_tables(c)

            c.execute("SELECT rules_text, updated_by, updated_at FROM chat_rules WHERE chat_id = ?", (cid,))

            row = c.fetchone()

 

        if not row or not row[0]:

            return await message.reply(

                "📜 <b>В этом чате ещё не установлены правила!</b>\n"

                "<i>Старшие модераторы (3+ ранг) могут задать их командой <code>+правила [текст]</code>.</i>",

                parse_mode="HTML"

            )

 

        rules_text, author, upd_ts = row

        date_str = datetime.fromtimestamp(upd_ts).strftime("%d.%m.%Y")

        kb = InlineKeyboardMarkup(inline_keyboard=[

            [InlineKeyboardButton(text="😤 Ознакомлен(а), бака!", callback_data="chat_rules_ack")]

        ])

 

        msg_text = (

            f"📜 <b>ПРАВИЛА ЭТОЙ БЕСЕДЫ</b>\n"

            f"━━━━━━━━━━━━━━\n"

            f"{rules_text}\n"

            f"━━━━━━━━━━━━━━\n"

            f"✍️ <i>Обновил(а): {author} ({date_str})</i>"

        )

        await message.reply(msg_text, reply_markup=kb, parse_mode="HTML")

 

    async def handle_show_info(message: types.Message):

        kb = InlineKeyboardMarkup(inline_keyboard=[

            [InlineKeyboardButton(text="📖 Открыть полную инструкцию", url=INFO_URL)]

        ])

        info_text = (

            "📚 <b>ОБЩАЯ ИНФОРМАЦИЯ И ГАЙД ПО БОТУ</b>\n"

            "━━━━━━━━━━━━━━\n"

            "∙ 🎮 Суть игры и прокачка героев\n"

            "∙ 😤 Все РП-команды и реплики\n"

            "∙ 🎴 Досье шиноби и статистика чата\n"

            "∙ 🧠 Правила аниме-викторины\n"

            "∙ 🛡 Админ-команды, ранги и варны\n"

            "━━━━━━━━━━━━━━\n"

            "😤 <i>«Хмф! Специально для тебя всё расписал(а) на одной странице — нажимай и читай, бака!»</i>"

        )

        await message.reply(info_text, reply_markup=kb, parse_mode="HTML")

 

    @dp.callback_query(F.data == "chat_rules_ack")

    async def cb_rules_ack(callback: types.CallbackQuery):

        await callback.answer("Хмф! Смотри не нарушай их, бака, а то получишь по шее!", show_alert=True)

 

    async def check_quiz_answer_safe(event: types.Message):

        cid = event.chat.id

        if cid not in active_quiz_dict or not event.text or not event.from_user or event.from_user.is_bot:

            return False

 

        guess = (

            event.text.strip().lower()

            .replace(",", "").replace(".", "").replace("!", "")

            .replace(":", "").replace("-", " ").replace("ё", "е")

        )

        guess = " ".join(guess.split())

        quiz = active_quiz_dict.get(cid)

        if not quiz:

            return False

 

        clean_answers = [

            " ".join(a.lower().replace("-", " ").replace("ё", "е").split())

            for a in quiz.get("answers", [])

        ]

        if guess not in clean_answers:

            return False

 

        title = quiz.get("title")

        active_quiz_dict.pop(cid, None)

 

        with sqlite3.connect("game_v2.db") as conn:

            conn.execute("PRAGMA busy_timeout=5000;")

            c = conn.cursor()

            ensure_extra_tables(c)

            c.execute(

                "UPDATE chat_members SET quiz_wins = quiz_wins + 1 WHERE chat_id = ? AND user_id = ?",

                (cid, event.from_user.id)

            )

            conn.commit()

 

        uname = (event.from_user.full_name or event.from_user.username or "Шиноби").replace("<", "").replace(">", "")

        await event.reply(

            f"🎉 <b>ЕСТЬ ПРАВИЛЬНЫЙ ОТВЕТ!</b>\n\n"

            f"🏆 Самый быстрый знаток аниме: <a href=\"tg://user?id={event.from_user.id}\"><b>{uname}</b></a>\n"

            f"🎬 Загаданный тайтл: <b>{title}</b>\n\n"

            f"<i>Напиши <code>викторина</code> для нового раунда!</i>",

            parse_mode="HTML",

            disable_web_page_preview=True

        )

        return True


    def build_chat_top_card(cid: int, caller_id: int, mode: str = "today"):

        with sqlite3.connect("game_v2.db") as conn:

            c = conn.cursor()

            ensure_extra_tables(c)

 

            if mode == "today":

                c.execute("""

                    SELECT user_id, user_name, msg_today, msg_total

                    FROM chat_members

                    WHERE chat_id = ? AND msg_today > 0

                    ORDER BY msg_today DESC, msg_total DESC LIMIT 30

                """, (cid,))

                rows = c.fetchall()

                c.execute("SELECT COALESCE(SUM(msg_today), 0) FROM chat_members WHERE chat_id = ?", (cid,))

                (sum_val,) = c.fetchone()

                c.execute("SELECT msg_today, msg_total FROM chat_members WHERE chat_id = ? AND user_id = ?", (cid, caller_id))

                u_row = c.fetchone()

                u_tod, u_tot = (u_row[0], u_row[1]) if u_row else (0, 0)

                if u_tod > 0:

                    c.execute(

                        "SELECT COUNT(*) + 1 FROM chat_members WHERE chat_id = ? AND (msg_today > ? OR (msg_today = ? AND msg_total > ?))",

                        (cid, u_tod, u_tod, u_tot)

                    )

                    (u_rank,) = c.fetchone()

                    my_line = f"👤 Твоё место: <b>#{u_rank}</b> (+{u_tod} сег. | {u_tot} всего)"

                else:

                    my_line = f"👤 Твоё место: <b>вне топа дня</b> (0 сег. | {u_tot} всего)"

                header = f"🔥 <b>ТОП-30 АКТИВНОСТИ ЗА СЕГОДНЯ</b>\n💬 Написано за день: <b>+{sum_val} сообщ.</b>"

            else:

                c.execute("""

                    SELECT user_id, user_name, msg_total, msg_today

                    FROM chat_members

                    WHERE chat_id = ? AND msg_total > 0

                    ORDER BY msg_total DESC, msg_today DESC LIMIT 30

                """, (cid,))

                rows = c.fetchall()

                c.execute("SELECT COALESCE(SUM(msg_total), 0), COALESCE(SUM(msg_today), 0) FROM chat_members WHERE chat_id = ?", (cid,))

                sum_tot, sum_tod = c.fetchone()

                c.execute("SELECT msg_total, msg_today FROM chat_members WHERE chat_id = ? AND user_id = ?", (cid, caller_id))

                u_row = c.fetchone()

                u_tot, u_tod = (u_row[0], u_row[1]) if u_row else (0, 0)

                if u_tot > 0:

                    c.execute("SELECT COUNT(*) + 1 FROM chat_members WHERE chat_id = ? AND msg_total > ?", (cid, u_tot))

                    (u_rank,) = c.fetchone()

                    my_line = f"👤 Твоё место: <b>#{u_rank}</b> ({u_tot} сообщ., +{u_tod} сег.)"

                else:

                    my_line = "👤 Твоё место: <b>вне рейтинга</b> (0 сообщ.)"

                header = f"🏆 <b>ТОП-30 АКТИВНОСТИ ЗА ВСЁ ВРЕМЯ</b>\n💬 Всего в беседе: <b>{sum_tot}</b> (+{sum_tod} сег.)"

 

        lines = [header, "━━━━━━━━━━━━━━━━━━━━"]

        if not rows:

            lines.append("<i>Пока никто не написал ни одного сообщения!</i>")

        else:

            medals = {1: "🥇", 2: "🥈", 3: "🥉"}

            for idx, (uid, uname, main_cnt, sec_cnt) in enumerate(rows, 1):

                safe_n = str(uname or "Шиноби").replace("<", "").replace(">", "")

                u_link = f'<a href="tg://user?id={uid}"><b>{safe_n}</b></a>'

                mark = medals.get(idx, f"<b>{idx}.</b>")

                if mode == "today":

                    lines.append(f"{mark} {u_link} — <b>+{main_cnt}</b> <i>({sec_cnt} всего)</i>")

                else:

                    lines.append(f"{mark} {u_link} — <b>{main_cnt}</b> <i>(+{sec_cnt})</i>")

 

        lines.append("━━━━━━━━━━━━━━━━━━━━")

        lines.append(my_line)

        lines.append("<i>Команды: <code>стата</code> (день) | <code>вся стата</code> (всегда)</i>")

 

        kb = InlineKeyboardMarkup(inline_keyboard=[[

            InlineKeyboardButton(text="🔥 За сегодня" + (" ✓" if mode == "today" else ""), callback_data=f"ctop:today:{caller_id}"),

            InlineKeyboardButton(text="🏆 За всё время" + (" ✓" if mode == "all" else ""), callback_data=f"ctop:all:{caller_id}"),

        ]])

        return "\n".join(lines), kb

 

    @dp.callback_query(F.data.startswith("ctop:"))

    async def cb_switch_chat_top(call: types.CallbackQuery):

        _, mode, orig_uid_str = call.data.split(":")

        cid = call.message.chat.id

        text, kb = build_chat_top_card(cid, call.from_user.id, mode=mode)

        try:

            await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

        except Exception:

            pass

        await call.answer()

 

    async def send_user_dossier(message: types.Message):

        target = message.reply_to_message.from_user if (message.reply_to_message and message.reply_to_message.from_user) else message.from_user

        if target.is_bot:

            return await message.reply("😤 Я — великий Цундере-бот этой беседы! Нечего в моё досье заглядывать!")

 

        cid = message.chat.id

        uid = target.id

        uname = (target.full_name or target.username or "Шиноби").replace("<", "").replace(">", "")

        now = int(time.time())

 

        rnk = await get_member_rank(cid, uid)

        role_str = f"{RANK_NAMES[rnk]} ({rnk} ранг)" if rnk > 0 else "Участник"

 

        with sqlite3.connect("game_v2.db") as conn:

            conn.execute("PRAGMA busy_timeout=5000;")

            c = conn.cursor()

            ensure_extra_tables(c)

 

            c.execute(

                "SELECT msg_total, msg_today, quiz_wins, first_seen_ts FROM chat_members WHERE chat_id = ? AND user_id = ?",

                (cid, uid)

            )

            cm_row = c.fetchone()

            if cm_row:

                msg_total, msg_today, quiz_wins, first_ts = cm_row

            else:

                msg_total, msg_today, quiz_wins, first_ts = 0, 0, 0, now

 

            if not first_ts or first_ts <= 0:

                c.execute("UPDATE chat_members SET first_seen_ts = ? WHERE chat_id = ? AND user_id = ?", (now, cid, uid))

                conn.commit()

                first_ts = now

 

            c.execute("SELECT warns_count FROM chat_warns WHERE chat_id = ? AND user_id = ?", (cid, uid))

            w_row = c.fetchone()

            warns_cnt = int(w_row[0]) if w_row else 0

 

            c.execute("SELECT COUNT(*) + 1 FROM chat_members WHERE chat_id = ? AND msg_total > ?", (cid, msg_total))

            (chat_rank,) = c.fetchone()

 

            g_user = get_user_fn(uid, target.username)

            _, _, g_lvl, g_energy, _, _, _ = g_user

            lvl_data = levels.get(g_lvl)

            if lvl_data:

                hero_short = lvl_data.get("name").split(" (")[0]

                hero_line = f"{hero_short} (Ур. {g_lvl} ∙ <code>{g_energy}/{lvl_data.get('need')}⚡</code>)"

            else:

                hero_line = f"Бог Аниме (Ур. {g_lvl})"

 

            c.execute("SELECT COUNT(*) + 1 FROM users WHERE level > ? OR (level = ? AND energy > ?)", (g_lvl, g_lvl, g_energy))

            (global_rank,) = c.fetchone()

 

        first_date_str = datetime.fromtimestamp(first_ts).strftime("%d.%m.%Y")

        days_in_chat = max(1, (now - first_ts) // 86400)

        quote_line = PERSONAL_DOSSIER_QUOTES[uid % len(PERSONAL_DOSSIER_QUOTES)]

 

        dossier_text = (

            f"🎴 <b>ДОСЬЕ ШИНОБИ</b>\n"

            f"━━━━━━━━━━━━━━\n"

            f"👤 <a href=\"tg://user?id={uid}\"><b>{uname}</b></a> ∙ <i>{role_str}</i>\n"

            f"🦸 <b>Герой:</b> {hero_line}\n"

            f"🏆 <b>Топ:</b> #{chat_rank} в чате | #{global_rank} в боте\n"

            f"💬 <b>Чат:</b> {msg_total} сообщ. <i>(+{msg_today} сегодня)</i>\n"

            f"🧠 <b>Викторина:</b> {quiz_wins} побед | ⚠️ <b>Варны:</b> {warns_cnt}/3\n"

            f"📅 <b>В чате с:</b> {first_date_str} <i>({days_in_chat} дн.)</i>\n"

            f"━━━━━━━━━━━━━━\n"

            f"😤 <i>«{quote_line}»</i>"

        )

        await message.reply(dossier_text, parse_mode="HTML", disable_web_page_preview=True)

    @dp.message.outer_middleware()

    async def chat_extra_middleware(handler, event: types.Message, data: dict):

        if event.chat and event.chat.type == "private" and event.text:

            btn_text = event.text.strip()

            lower_priv = btn_text.lower()

 

            if event.from_user and event.from_user.id == admin_id:

                if lower_priv == "/admin":

                    admin_waiting_find.discard(admin_id)

                    extra_kb = InlineKeyboardMarkup(inline_keyboard=[

                        [InlineKeyboardButton(text="🕵️ Изменить игрока (Энергия / Ур.)", callback_data="adm_extra_find")],

                        [

                            InlineKeyboardButton(text="📊 Воронка уровней", callback_data="adm_extra_users"),

                            InlineKeyboardButton(text="💬 Пульс чатов", callback_data="adm_extra_chats"),

                        ]

                    ])

                    await event.answer("⚡ <b>Дополнительные инструменты управления:</b>", reply_markup=extra_kb, parse_mode="HTML")

 

                if admin_id in admin_waiting_find and not lower_priv.startswith("/"):

                    admin_waiting_find.discard(admin_id)

                    query_val = btn_text.lstrip("@")

                    with sqlite3.connect("game_v2.db") as conn:

                        c = conn.cursor()

                        if query_val.isdigit():

                            c.execute("SELECT user_id FROM users WHERE user_id = ?", (int(query_val),))

                        else:

                            c.execute("SELECT user_id FROM users WHERE LOWER(username) = ?", (query_val.lower(),))

                        u_row = c.fetchone()

 

                    if not u_row:

                        await event.reply(f"❌ Игрок <b>{query_val}</b> не найден в базе!", parse_mode="HTML")

                        return

 

                    card_text, card_kb = build_admin_player_card(u_row[0])

                    await event.reply(card_text, reply_markup=card_kb, parse_mode="HTML")

                    return

 

                if lower_priv == "/stat_users":

                    await event.reply(build_stat_users_text(), parse_mode="HTML")

                    return

 

                if lower_priv == "/stat_chats":

                    await event.reply(build_stat_chats_text(), parse_mode="HTML")

                    return

 

                if lower_priv.startswith("/find") or lower_priv.startswith("/edit"):

                    parts = btn_text.split(maxsplit=1)

                    if len(parts) < 2 or not parts[1].strip():

                        await event.reply("🔍 <b>Редактор игрока:</b>\nНапиши <code>/find @ник</code> или <code>/find ID</code>", parse_mode="HTML")

                        return

                    query_val = parts[1].strip().lstrip("@")

                    with sqlite3.connect("game_v2.db") as conn:

                        c = conn.cursor()

                        if query_val.isdigit():

                            c.execute("SELECT user_id FROM users WHERE user_id = ?", (int(query_val),))

                        else:

                            c.execute("SELECT user_id FROM users WHERE LOWER(username) = ?", (query_val.lower(),))

                        u_row = c.fetchone()

 

                    if not u_row:

                        await event.reply(f"❌ Игрок <b>{query_val}</b> не найден в базе!", parse_mode="HTML")

                        return

 

                    card_text, card_kb = build_admin_player_card(u_row[0])

                    await event.reply(card_text, reply_markup=card_kb, parse_mode="HTML")

                    return

 

            if btn_text == "📖 Информация и правила":

                await handle_show_info(event)

                return

            if btn_text == "🦸 Мой герой" and start_fn:

                await start_fn(event)

                return

            elif btn_text == "🛤 Дорога славы" and road_fn:

                await road_fn(event)

                return

            elif btn_text == "🏆 Топ 10" and top_fn:

                await top_fn(event)

                return

            elif btn_text == "🎟 Ввести промокод":

                await event.reply("🎟 <b>Ввод промокода:</b>\nОтправь боту команду: <code>/promo ТВОЙ_КОД</code>", parse_mode="HTML")

                return

 

        if event.chat and event.chat.type in ("group", "supergroup") and event.text:

            full_text = event.text.strip()

            lower_text = full_text.lower()

 

            if lower_text in DOSSIER_CMDS:

                await send_user_dossier(event)

                return



            if lower_text in ("стата", "топ", "топ чата", "стата день", "топ дня"):

                t_text, t_kb = build_chat_top_card(event.chat.id, event.from_user.id, mode="today")

                await event.reply(t_text, reply_markup=t_kb, parse_mode="HTML", disable_web_page_preview=True)

                return

 

            if lower_text in ("вся стата", "стата вся", "общий топ", "топ весь", "топ за все время", "топ за всё время"):

                t_text, t_kb = build_chat_top_card(event.chat.id, event.from_user.id, mode="all")

                await event.reply(t_text, reply_markup=t_kb, parse_mode="HTML", disable_web_page_preview=True)

                return
             

 

            if lower_text in RANKS_INFO_CMDS:

                await handle_ranks_info(event)

                return

 

            if lower_text in WHO_ADMIN_CMDS:

                await handle_who_admin(event)

                return

 

            if lower_text == "список мутов":

                await handle_punishments_list_extra(event, "mute")

                return

 

            if lower_text == "список банов":

                await handle_punishments_list_extra(event, "ban")

                return

 

            for w_list_cmd in ("варны", "список варнов", "предупреждения"):

                if lower_text == w_list_cmd or lower_text.startswith(w_list_cmd + " "):

                    await handle_warns_query(event, full_text[len(w_list_cmd):])

                    return

 

            for unwarn_cmd in ("снять варн", "-варн", "разварн"):

                if lower_text == unwarn_cmd or lower_text.startswith(unwarn_cmd + " "):

                    await handle_warn_action(event, "unwarn", full_text[len(unwarn_cmd):])

                    return

 

            for warn_cmd in ("варн", "+варн", "пред"):

                if lower_text == warn_cmd or lower_text.startswith(warn_cmd + " "):

                    await handle_warn_action(event, "warn", full_text[len(warn_cmd):])

                    return

 

            for mod_cmd in ("размут", "разбан", "мут", "бан"):

                if lower_text == mod_cmd or lower_text.startswith(mod_cmd + " "):

                    await handle_ranked_moderation(event, mod_cmd, full_text[len(mod_cmd):])

                    return

 

            for rem_cmd in ("снять админа", "разжаловать"):

                if lower_text == rem_cmd or lower_text.startswith(rem_cmd + " "):

                    await handle_rank_change(event, "remove", full_text[len(rem_cmd):])

                    return

 

            for prom_cmd in ("повысить", "+админ", "+модер"):

                if lower_text == prom_cmd or lower_text.startswith(prom_cmd + " "):

                    await handle_rank_change(event, "promote", full_text[len(prom_cmd):])

                    return

 

            for dem_cmd in ("понизить", "-админ", "-модер"):

                if lower_text == dem_cmd or lower_text.startswith(dem_cmd + " "):

                    await handle_rank_change(event, "demote", full_text[len(dem_cmd):])

                    return

 

            if lower_text in VIEW_RULES_CMDS or lower_text.startswith("/rules@"):

                await handle_show_rules(event)

                return

 

            if lower_text in INFO_CMDS or lower_text.startswith("/help@"):

                await handle_show_info(event)

                return

 

            if lower_text in DEL_RULES_CMDS:

                await handle_del_rules(event)

                return

 

            for prefix in ("+правила", "новые правила", "/setrules"):

                if lower_text == prefix or lower_text.startswith(prefix + " ") or lower_text.startswith(prefix + "\n"):

                    rules_body = full_text[len(prefix):].strip()

                    await handle_set_rules(event, rules_body)

                    return

 

            if await check_quiz_answer_safe(event):

                return

 

        return await handler(event, data)
