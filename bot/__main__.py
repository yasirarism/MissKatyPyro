import logging, asyncio, importlib, re
from uvloop import install
from bot import app, user
from bot.plugins import ALL_MODULES
from bot.utils import paginate_modules
from utils import temp
from pyrogram.raw.all import layer
from pyrogram import idle, __version__, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from contextlib import closing, suppress

loop = asyncio.get_event_loop()

HELPABLE = {}


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
    print("+===============================================================+")
    print("|                        MissKatyPyro                           |")
    print("+===============+===============+===============+===============+")
    print(bot_modules)
    print("+===============+===============+===============+===============+")
    print(f"[INFO]: BOT STARTED AS @{me.username}!")

    try:
        print("[INFO]: SENDING ONLINE STATUS")
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
            url=f"t.me/MissKatyRoBot?start=bantuan",
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


@app.on_message(filters.command("bantuan"))
async def help_command(_, message):
    if message.chat.type.value != "private":
        if len(message.command) >= 2:
            name = (message.text.split(None, 1)[1]).replace(" ", "_").lower()
            if str(name) in HELPABLE:
                key = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            text="Click here",
                            url=f"t.me/MissKatyRoBot?start=bantuan_{name}",
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
        keyboard = InlineKeyboardMarkup(
            paginate_modules(0, HELPABLE, "bantuan"))
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


@app.on_callback_query(filters.regex(r"bantuan_(.*?)"))
async def help_button(client, query):
    home_match = re.match(r"bantuan_home\((.+?)\)", query.data)
    mod_match = re.match(r"bantuan_module\((.+?)\)", query.data)
    prev_match = re.match(r"bantuan_prev\((.+?)\)", query.data)
    next_match = re.match(r"bantuan_next\((.+?)\)", query.data)
    back_match = re.match(r"bantuan_back", query.data)
    create_match = re.match(r"bantuan_create", query.data)
    top_text = f"""
Hello {query.from_user.first_name}, My name is MissKaty.
I'm a group management bot with some usefule features.
You can choose an option below, by clicking a button.
Also you can ask anything in Support Group.
General command are:
 - /start: Start the bot
 - /bantuan: Give this message
 """
    if mod_match:
        module = (mod_match.group(1)).replace(" ", "_")
        text = ("{} **{}**:\n".format("Here is the help for",
                                      HELPABLE[module].__MODULE__) +
                HELPABLE[module].__HELP__)

        await query.message.edit(
            text=text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("back",
                                       callback_data="bantuan_back")]]),
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
                paginate_modules(curr_page - 1, HELPABLE, "bantuan")),
            disable_web_page_preview=True,
        )

    elif next_match:
        next_page = int(next_match.group(1))
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(next_page + 1, HELPABLE, "bantuan")),
            disable_web_page_preview=True,
        )

    elif back_match:
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(0, HELPABLE, "bantuan")),
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
    install()
    with closing(loop):
        with suppress(asyncio.exceptions.CancelledError):
            loop.run_until_complete(start_bot())
        loop.run_until_complete(asyncio.sleep(3.0))
