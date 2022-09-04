import logging, asyncio, importlib
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


keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            text="Help ❓",
            url=f"t.me/MissKatyPyro?start=help",
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


if __name__ == "__main__":
    install()
    with closing(loop):
        with suppress(asyncio.exceptions.CancelledError):
            loop.run_until_complete(start_bot())
        loop.run_until_complete(asyncio.sleep(3.0))
