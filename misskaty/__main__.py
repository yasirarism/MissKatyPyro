"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2022-12-01 09:33:16
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
 """
import asyncio
import importlib
import re
import traceback
from logging import getLogger

from pyrogram import __version__, filters, idle
from pyrogram.raw.all import layer
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.users_chats_db import db
from misskaty import (
    BOT_NAME,
    BOT_USERNAME,
    HELPABLE,
    UBOT_NAME,
    app,
    user,
)
from misskaty.core.message_utils import *
from misskaty.helper import bot_sys_stats, paginate_modules
from misskaty.plugins import ALL_MODULES
from misskaty.vars import COMMAND_HANDLER, LOG_CHANNEL, SUDO
from utils import auto_clean, temp

LOGGER = getLogger(__name__)
loop = asyncio.get_event_loop()

# Run Bot
async def start_bot():
    global HELPABLE

    for module in ALL_MODULES:
        imported_module = importlib.import_module(f"misskaty.plugins.{module}")
        if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
            imported_module.__MODULE__ = imported_module.__MODULE__
            if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
                HELPABLE[imported_module.__MODULE__.lower()] = imported_module
    bot_modules = ""
    j = 1
    for i in ALL_MODULES:
        if j == 4:
            bot_modules += "|{:<15}|\n".format(i)
            j = 0
        else:
            bot_modules += "|{:<15}".format(i)
        j += 1
    LOGGER.info("+===============================================================+")
    LOGGER.info("|                        MissKatyPyro                           |")
    LOGGER.info("+===============+===============+===============+===============+")
    LOGGER.info(bot_modules)
    LOGGER.info("+===============+===============+===============+===============+")
    LOGGER.info(f"[INFO]: BOT STARTED AS @{BOT_USERNAME}!")

    try:
        LOGGER.info("[INFO]: SENDING ONLINE STATUS")
        for i in SUDO:
            await app.send_message(
                i,
                f"USERBOT AND BOT STARTED with Pyrogram v{__version__}..\nUserBot: {UBOT_NAME}\nBot: {BOT_NAME}\n\nwith Pyrogram v{__version__} (Layer {layer}) started on @{BOT_USERNAME}.\n\n<code>{bot_modules}</code>",
            )
    except Exception as e:
        LOGGER.error(str(e))
    asyncio.create_task(auto_clean())
    await idle()


home_keyboard_pm = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="Commands ❓", callback_data="bot_commands"),
            InlineKeyboardButton(
                text="Source Code 🛠",
                url="https://github.com/yasirarism/MissKatyPyro",
            ),
        ],
        [
            InlineKeyboardButton(
                text="System Stats 🖥",
                callback_data="stats_callback",
            ),
            InlineKeyboardButton(text="Dev 👨", url="https://t.me/YasirArisM"),
        ],
        [
            InlineKeyboardButton(
                text="Add Me To Your Group 🎉",
                url=f"http://t.me/{BOT_USERNAME}?startgroup=new",
            )
        ],
    ]
)

home_text_pm = f"Hey there! My name is {BOT_NAME}. I have many useful features for you, feel free to add me to your group.\n\nIf you want give coffee to my owner you can send /donate command for more info."

keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="Help ❓", url=f"t.me/{BOT_USERNAME}?start=help"),
            InlineKeyboardButton(
                text="Source Code �",
                url="https://github.com/yasirarism/MissKatyPyro",
            ),
        ],
        [
            InlineKeyboardButton(
                text="System Stats 💻",
                callback_data="stats_callback",
            ),
            InlineKeyboardButton(text="Dev 👨", url="https://t.me/YasirArisM"),
        ],
    ]
)


@app.on_message(filters.command("start", COMMAND_HANDLER))
async def start(_, message):
    if not message.from_user: return
    if message.chat.type.value != "private":
        if not await db.get_chat(message.chat.id):
            total = await app.get_chat_members_count(message.chat.id)
            await app.send_message(
                LOG_CHANNEL,
                f"#NewGroup\nGroup = {message.chat.title}(<code>{message.chat.id}</code>)\nMembers Count = <code>{total}</code>\nAdded by - Unknown",
            )

            await db.add_chat(message.chat.id, message.chat.title)
        nama = (
            message.from_user.mention
            if message.from_user
            else message.sender_chat.title
        )
        return await message.reply_photo(
            photo="https://telegra.ph/file/90e9a448bc2f8b055b762.jpg",
            caption=f"Hi {nama}, Pm Me For More Info About Me.",
            reply_markup=keyboard,
        )
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await app.send_message(
            LOG_CHANNEL,
            f"#NewUser\nID - <code>{message.from_user.id}</code>\nName - {message.from_user.mention}",
        )

    if len(message.text.split()) > 1:
        name = (message.text.split(None, 1)[1]).lower()
        if "_" in name:
            module = name.split("_", 1)[1]
            text = (
                f"Here is the help for **{HELPABLE[module].__MODULE__}**:\n"
                + HELPABLE[module].__HELP__
            )
            await kirimPesan(message, text, disable_web_page_preview=True)
        elif name == "help":
            text, keyb = await help_parser(message.from_user.first_name)
            await kirimPesan(
                message,
                text,
                reply_markup=keyb,
            )
    else:
        await message.reply_photo(
            photo="https://telegra.ph/file/90e9a448bc2f8b055b762.jpg",
            caption=home_text_pm,
            reply_markup=home_keyboard_pm,
        )


@app.on_callback_query(filters.regex("bot_commands"))
async def commands_callbacc(_, CallbackQuery):
    text, keyboard = await help_parser(CallbackQuery.from_user.mention)
    await app.send_message(
        CallbackQuery.message.chat.id,
        text=text,
        reply_markup=keyboard,
    )
    await hapusPesan(CallbackQuery.message)


@app.on_callback_query(filters.regex("stats_callback"))
async def stats_callbacc(_, CallbackQuery):
    text = await bot_sys_stats()
    await app.answer_callback_query(CallbackQuery.id, text, show_alert=True)


@app.on_message(filters.command("help", COMMAND_HANDLER))
async def help_command(_, message):
    if not message.from_user: return
    if message.chat.type.value != "private":
        if not await db.get_chat(message.chat.id):
            total = await app.get_chat_members_count(message.chat.id)
            await app.send_message(
                LOG_CHANNEL,
                f"#NewGroup\nGroup = {message.chat.title}(<code>{message.chat.id}</code>)\nMembers Count = <code>{total}</code>\nAdded by - Unknown",
            )

            await db.add_chat(message.chat.id, message.chat.title)
        if len(message.command) >= 2:
            name = (message.text.split(None, 1)[1]).replace(" ", "_").lower()
            if str(name) in HELPABLE:
                key = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Click here",
                                url=f"t.me/{BOT_USERNAME}?start=help_{name}",
                            )
                        ],
                    ]
                )
                await kirimPesan(
                    message,
                    f"Click on the below button to get help about {name}",
                    reply_markup=key,
                )
            else:
                await kirimPesan(message, "PM Me For More Details.", reply_markup=keyboard)
        else:
            await kirimPesan(message, "Pm Me For More Details.", reply_markup=keyboard)
    else:
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            await app.send_message(
                LOG_CHANNEL,
                f"#NewUser\nID - <code>{message.from_user.id}</code>\nName - {message.from_user.mention}",
            )

        if len(message.command) >= 2:
            name = (message.text.split(None, 1)[1]).replace(" ", "_").lower()
            if str(name) in HELPABLE:
                text = (
                    f"Here is the help for **{HELPABLE[name].__MODULE__}**:\n"
                    + HELPABLE[name].__HELP__
                )
                await kirimPesan(message, text, disable_web_page_preview=True)
            else:
                text, help_keyboard = await help_parser(message.from_user.first_name)
                await kirimPesan(
                    message,
                    text,
                    reply_markup=help_keyboard,
                    disable_web_page_preview=True,
                )
        else:
            text, help_keyboard = await help_parser(message.from_user.first_name)
            await kirimPesan(
                message, text, reply_markup=help_keyboard, disable_web_page_preview=True
            )
    return


async def help_parser(name, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    return (
        """Hello {first_name}, My name is {bot_name}.
I'm a bot with some useful features.
You can choose an option below, by clicking a button.

If you want give coffee to my owner you can send /donate command for more info.
""".format(
            first_name=name,
            bot_name="MissKaty",
        ),
        keyboard,
    )


@app.on_callback_query(filters.regex(r"help_(.*?)"))
async def help_button(client, query):
    home_match = re.match(r"help_home\((.+?)\)", query.data)
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    create_match = re.match(r"help_create", query.data)
    top_text = f"""
Hello {query.from_user.first_name}, My name is MissKaty.
I'm a bot with some usefule features.
You can choose an option below, by clicking a button below.

General command are:
 - /start: Start the bot
 - /help: Give this message
 """
    if mod_match:
        module = mod_match[1].replace(" ", "_")
        text = f"Here is the help for **{HELPABLE[module].__MODULE__}**:\n{HELPABLE[module].__HELP__}"

        await editPesan(
            query.message,
            text=text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("back", callback_data="help_back")]]
            ),
            disable_web_page_preview=True,
        )
    elif home_match:
        await app.send_message(
            query.from_user.id,
            text=home_text_pm,
            reply_markup=home_keyboard_pm,
        )
        await hapusPesan(query.message)
    elif prev_match:
        curr_page = int(prev_match[1])
        await editPesan(
            query.message,
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(curr_page - 1, HELPABLE, "help")
            ),
            disable_web_page_preview=True,
        )

    elif next_match:
        next_page = int(next_match[1])
        await editPesan(
            query.message,
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(next_page + 1, HELPABLE, "help")
            ),
            disable_web_page_preview=True,
        )

    elif back_match:
        await editPesan(
            query.message,
            text=top_text,
            reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")),
            disable_web_page_preview=True,
        )

    elif create_match:
        text, keyboard = await help_parser(query)
        await editPesan(
            query.message,
            text=text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )

    return await client.answer_callback_query(query.id)




if __name__ == "__main__":
    try:
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        pass
    except Exception:
        err = traceback.format_exc()
        LOGGER.error(err)
    finally:
        loop.stop()
        print("------------------------ Stopped Services ------------------------")
