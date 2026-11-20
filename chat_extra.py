import sqlite3

import time

from datetime import datetime

from aiogram import Bot, Dispatcher, types

 

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

 

 

def setup_chat_extra(dp: Dispatcher, bot: Bot, cur, db, admin_id: int, levels: dict, get_user_fn):

 

    async def send_user_dossier(message: types.Message):

        if message.chat.type not in ("group", "supergroup"):

            return

 

        target = message.reply_to_message.from_user if (message.reply_to_message and message.reply_to_message.from_user) else message.from_user

        if target.is_bot:

            return await message.reply("😤 Я — великий Цундере-бот этой беседы! Нечего в моё досье заглядывать!")

 

        cid = message.chat.id

        uid = target.id

        uname = (target.full_name or target.username or "Шиноби").replace("<", "").replace(">", "")

        now = int(time.time())

 

        try:

            member = await bot.get_chat_member(cid, uid)

            if uid == admin_id:

                role_str = "👑 Создатель"

            elif member.status == "creator":

                role_str = "👑 Создатель"

            elif member.status == "administrator":

                role_str = "🛡 Админ"

            else:
import sqlite3

import time

from datetime import datetime

from aiogram import Bot, Dispatcher, types

 

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

 

 

def ensure_chat_columns(c):

    for col_sql in [

        "ALTER TABLE chat_members ADD COLUMN quiz_wins INTEGER DEFAULT 0",

        "ALTER TABLE chat_members ADD COLUMN first_seen_ts INTEGER DEFAULT 0",

    ]:

        try:

            c.execute(col_sql)

        except sqlite3.OperationalError:

            pass

 

 

def setup_chat_extra(dp: Dispatcher, bot: Bot, cur, db, admin_id: int, levels: dict, get_user_fn):

 

    async def check_quiz_answer_safe(event: types.Message):

        try:

            import bot as main_bot

            quiz_dict = getattr(main_bot, "active_emoji_quiz", {})

        except Exception:

            return False

 

        cid = event.chat.id

        if cid not in quiz_dict or not event.text or not event.from_user or event.from_user.is_bot:

            return False

 

        guess = (

            event.text.strip().lower()

            .replace(",", "").replace(".", "").replace("!", "")

            .replace(":", "").replace("-", " ").replace("ё", "е")

        )

        guess = " ".join(guess.split())

        quiz = quiz_dict.get(cid)

        if not quiz:

            return False

 

        clean_answers = [

            " ".join(a.lower().replace("-", " ").replace("ё", "е").split())

            for a in quiz.get("answers", [])

        ]

        if guess not in clean_answers:

            return False

 

        title = quiz.get("title")

        quiz_dict.pop(cid, None)

 

        with sqlite3.connect("game_v2.db") as conn:

            conn.execute("PRAGMA busy_timeout=5000;")

            c = conn.cursor()

            ensure_chat_columns(c)

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

 

    async def send_user_dossier(message: types.Message):

        if message.chat.type not in ("group", "supergroup"):

            return

 

        target = message.reply_to_message.from_user if (message.reply_to_message and message.reply_to_message.from_user) else message.from_user

        if target.is_bot:

            return await message.reply("😤 Я — великий Цундере-бот этой беседы! Нечего в моё досье заглядывать!")

 

        cid = message.chat.id

        uid = target.id

        uname = (target.full_name or target.username or "Шиноби").replace("<", "").replace(">", "")

        now = int(time.time())

 

        try:

            member = await bot.get_chat_member(cid, uid)

            if uid == admin_id:

                role_str = "👑 Создатель"

            elif member.status == "creator":

                role_str = "👑 Создатель"

            elif member.status == "administrator":

                role_str = "🛡 Админ"

            else:

                role_str = "Участник"

        except Exception:

            role_str = "Участник"

 

        with sqlite3.connect("game_v2.db") as conn:

            conn.execute("PRAGMA busy_timeout=5000;")

            c = conn.cursor()

            ensure_chat_columns(c)

 

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

 

            c.execute("SELECT COUNT(*) + 1 FROM chat_members WHERE chat_id = ? AND msg_total > ?", (cid, msg_total))

            (chat_rank,) = c.fetchone()

 

            g_user = get_user_fn(uid, target.username)

            _, _, g_lvl, g_energy, _, _, _ = g_user

            lvl_data = levels.get(g_lvl)

            if lvl_data:

                hero_short = lvl_data.get("name").split(" (").pop(0)

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

            f"🧠 <b>Викторина:</b> {quiz_wins} побед\n"

            f"📅 <b>В чате с:</b> {first_date_str} <i>({days_in_chat} дн.)</i>\n"

            f"━━━━━━━━━━━━━━\n"

            f"😤 <i>«{quote_line}»</i>"

        )

        await message.reply(dossier_text, parse_mode="HTML", disable_web_page_preview=True)

 

    @dp.message.outer_middleware()

    async def chat_extra_middleware(handler, event: types.Message, data: dict):

        if event.chat and event.chat.type in ("group", "supergroup") and event.text:

            clean_cmd = event.text.strip().lower()

            if clean_cmd in DOSSIER_CMDS:

                await send_user_dossier(event)

                return

            if await check_quiz_answer_safe(event):

                return

        return await handler(event, data)
