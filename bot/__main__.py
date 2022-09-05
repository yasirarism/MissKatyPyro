import asyncio, importlib, re
from bot import app, user, HELPABLE
from bot.plugins import ALL_MODULES
from bot.utils import paginate_modules
from bot.utils.tools import bot_sys_stats
from utils import temp
from logging import info as log_info
from pyrogram.raw.all import layer
from pyrogram import idle, __version__, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

loop = asyncio.get_event_loop()


# Run Bot
async def start_bot():
    global HELPABLE

    for module in ALL_MODULES:
        imported_module = importlib.import_module(f"bot.plugins.{module}")
        if (hasattr(imported_module, "__MODULE__")
                and imported_module.__MODULE__):
            imported_module.__MODULE__ = imported_module.__MODULE__
            if (hasattr(imported_module, "__HELP__")
                    and imported_module.__HELP__):
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
    await app.start()
    await user.start()
    me = await app.get_me()
    ubot = await user.get_me()
    log_info("+===============================================================+")
    log_info("|                        MissKatyPyro                           |")
    log_info("+===============+===============+===============+===============+")
    log_info(bot_modules)
    log_info("+===============+===============+===============+===============+")
    log_info(f"[INFO]: BOT STARTED AS @{me.username}!")

    try:
        log_info("[INFO]: SENDING ONLINE STATUS")
        await app.send_message(
            617426792,
            f"USERBOT AND BOT STARTED with Pyrogram v{__version__}..\nUserBot: {ubot.first_name}\nBot: {me.first_name}\n\nwith Pyrogram v{__version__} (Layer {layer}) started on @{me.username}."
        )
    except Exception:
        pass

    await idle()
    await app.stop()
    await user.stop()
    print("[INFO]: Bye!")


home_keyboard_pm = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text="Commands ❓", callback_data="bot_commands"),
        InlineKeyboardButton(
            text="Github 🛠",
            url="https://github.com/yasirarism",
        ),
    ],
    [
        InlineKeyboardButton(
            text="System Stats 🖥",
            callback_data="stats_callback",
        ),
        InlineKeyboardButton(text="Support 👨",
                             url="http://t.me/YasirPediaGroup"),
    ],
    [
        InlineKeyboardButton(
            text="Add Me To Your Group 🎉",
            url=f"http://t.me/MissKatyRoBot?startgroup=new",
        )
    ],
])

home_text_pm = (f"Hey there! My name is MissKatyRoBot. I can manage your " +
                "group with lots of useful features, feel free to " +
                "add me to your group.")

keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            text="Help ❓",
            url=f"t.me/MissKatyRoBot?start=help",
        ),
        InlineKeyboardButton(
            text="Github 🛠",
            url="https://github.com/yasirarism",
        ),
    ],
    [
        InlineKeyboardButton(
            text="System Stats 💻",
            callback_data="stats_callback",
        ),
        InlineKeyboardButton(text="Support 👨", url="t.me/YasirPediaGroup"),
    ],
])


@app.on_message(filters.command("start"))
async def start(_, message):
    if message.chat.type.value != "private":
        return await message.reply_photo(
            photo="https://telegra.ph/file/90e9a448bc2f8b055b762.jpg",
            caption="Pm Me For More Details.",
            reply_markup=keyboard,
        )
    if len(message.text.split()) > 1:
        name = (message.text.split(None, 1)[1]).lower()
        if "_" in name:
            module = name.split("_", 1)[1]
            text = (
                f"Here is the help for **{HELPABLE[module].__MODULE__}**:\n" +
                HELPABLE[module].__HELP__)
            await message.reply(text, disable_web_page_preview=True)
        elif name == "help":
            text, keyb = await help_parser(message.from_user.first_name)
            await message.reply(
                text,
                reply_markup=keyb,
            )
    else:
        await message.reply_photo(
            photo="https://telegra.ph/file/90e9a448bc2f8b055b762.jpg",
            caption=home_text_pm,
            reply_markup=home_keyboard_pm,
        )
    return


@app.on_callback_query(filters.regex("bot_commands"))
async def commands_callbacc(_, CallbackQuery):
    text, keyboard = await help_parser(CallbackQuery.from_user.mention)
    await app.send_message(
        CallbackQuery.message.chat.id,
        text=text,
        reply_markup=keyboard,
    )

    await CallbackQuery.message.delete()


@app.on_callback_query(filters.regex("stats_callback"))
async def stats_callbacc(_, CallbackQuery):
    text = await bot_sys_stats()
    await app.answer_callback_query(CallbackQuery.id, text, show_alert=True)

@app.on_message(filters.command("help"))
async def help_command(_, message):
    if message.chat.type.value != "private":
        if len(message.command) >= 2:
            name = (message.text.split(None, 1)[1]).replace(" ", "_").lower()
            if str(name) in HELPABLE:
                key = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            text="Click here",
                            url=f"t.me/MissKatyRoBot?start=help_{name}",
                        )
                    ],
                ])
                await message.reply(
                    f"Click on the below button to get help about {name}",
                    reply_markup=key,
                )
            else:
                await message.reply("PM Me For More Details.",
                                    reply_markup=keyboard)
        else:
            await message.reply("Pm Me For More Details.",
                                reply_markup=keyboard)
    else:
        if len(message.command) >= 2:
            name = (message.text.split(None, 1)[1]).replace(" ", "_").lower()
            if str(name) in HELPABLE:
                text = (
                    f"Here is the help for **{HELPABLE[name].__MODULE__}**:\n"
                    + HELPABLE[name].__HELP__)
                await message.reply(text, disable_web_page_preview=True)
            else:
                text, help_keyboard = await help_parser(
                    message.from_user.first_name)
                await message.reply(
                    text,
                    reply_markup=help_keyboard,
                    disable_web_page_preview=True,
                )
        else:
            text, help_keyboard = await help_parser(
                message.from_user.first_name)
            await message.reply(text,
                                reply_markup=help_keyboard,
                                disable_web_page_preview=True)
    return


async def help_parser(name, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    return (
        """Hello {first_name}, My name is {bot_name}.
I'm a group management bot with some useful features.
You can choose an option below, by clicking a button.
Also you can ask anything in Support Group.
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
I'm a group management bot with some usefule features.
You can choose an option below, by clicking a button.
Also you can ask anything in Support Group.
General command are:
 - /start: Start the bot
 - /help: Give this message
 """
    if mod_match:
        module = (mod_match.group(1)).replace(" ", "_")
        text = ("{} **{}**:\n".format("Here is the help for",
                                      HELPABLE[module].__MODULE__) +
                HELPABLE[module].__HELP__)

        await query.message.edit(
            text=text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("back", callback_data="help_back")]]),
            disable_web_page_preview=True,
        )
    elif home_match:
        await app.send_message(
            query.from_user.id,
            text=home_text_pm,
            reply_markup=home_keyboard_pm,
        )
        await query.message.delete()
    elif prev_match:
        curr_page = int(prev_match.group(1))
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(curr_page - 1, HELPABLE, "help")),
            disable_web_page_preview=True,
        )

    elif next_match:
        next_page = int(next_match.group(1))
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(next_page + 1, HELPABLE, "help")),
            disable_web_page_preview=True,
        )

    elif back_match:
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(0, HELPABLE, "help")),
            disable_web_page_preview=True,
        )

    elif create_match:
        text, keyboard = await help_parser(query)
        await query.message.edit(
            text=text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )

    return await client.answer_callback_query(query.id)


if __name__ == "__main__":
    try:
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        logging.info(
            '----------------------- Service Stopped -----------------------')