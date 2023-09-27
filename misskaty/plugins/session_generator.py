import traceback
from logging import getLogger

from pyrogram import Client, filters
from pyrogram.errors import (
    ApiIdInvalid,
    PasswordHashInvalid,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
    SessionPasswordNeeded,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)
from telethon.sessions import StringSession

from misskaty import app
from misskaty.core.misskaty_patch.listen.listen import ListenerTimeout
from misskaty.vars import API_HASH, API_ID, COMMAND_HANDLER

LOGGER = getLogger("MissKaty")

__MODULE__ = "SessionGen"
__HELP__ = """
/genstring - Generate string session using this bot. Only support Pyrogram v2 and Telethon.
"""


ask_ques = "**» Please choose the library for which you want generate string :**\n\nNote: I'm not collecting any personal info from this feature, you can deploy own bot if you want."
buttons_ques = [
    [
        InlineKeyboardButton("Pyrogram", callback_data="pyrogram"),
        InlineKeyboardButton("Telethon", callback_data="telethon"),
    ],
    [
        InlineKeyboardButton("Pyrogram Bot", callback_data="pyrogram_bot"),
        InlineKeyboardButton("Telethon Bot", callback_data="telethon_bot"),
    ],
]

gen_button = [
    [InlineKeyboardButton(text="🙄 Generate Session 🙄", callback_data="genstring")]
]


async def is_batal(msg):
    if msg.text == "/cancel":
        await msg.reply(
            "**» Cancelled the ongoing string session generation process !**",
            quote=True,
            reply_markup=InlineKeyboardMarkup(gen_button),
        )
        return True
    elif msg.text == "/skip":
        return False
    elif msg.text.startswith("/"):  # Bot Commands
        await msg.reply(
            "**» Cancelled the ongoing string session generation process !**",
            quote=True,
        )
        return True
    else:
        return False


@app.on_callback_query(
    filters.regex(pattern=r"^(genstring|pyrogram|pyrogram_bot|telethon_bot|telethon)$")
)
async def callbackgenstring(bot, callback_query):
    query = callback_query.matches[0].group(1)
    if query == "genstring":
        await callback_query.answer()
        await callback_query.message.reply(
            ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques)
        )
    elif query.startswith("pyrogram") or query.startswith("telethon"):
        try:
            if query == "pyrogram":
                await callback_query.answer()
                await generate_session(bot, callback_query.message)
            elif query == "pyrogram_bot":
                await callback_query.answer(
                    "» The session generator will be of Pyrogram v2.", show_alert=True
                )
                await generate_session(bot, callback_query.message, is_bot=True)
            elif query == "telethon_bot":
                await callback_query.answer()
                await generate_session(
                    bot, callback_query.message, telethon=True, is_bot=True
                )
            elif query == "telethon":
                await callback_query.answer()
                await generate_session(bot, callback_query.message, telethon=True)
        except Exception as e:
            LOGGER.error(traceback.format_exc())
            ERROR_MESSAGE = (
                "Something went wrong. \n\n**ERROR** : {} "
                "\n\n**Please forward this message to my Owner**, if this message "
                "doesn't contain any sensitive data "
                "because this error is **not logged by bot.** !"
            )
            await callback_query.message.reply(ERROR_MESSAGE.format(str(e)))


@app.on_message(
    filters.private & ~filters.forwarded & filters.command("genstring", COMMAND_HANDLER)
)
async def genstringg(_, msg):
    await msg.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))


async def generate_session(bot, msg, telethon=False, is_bot: bool = False):
    ty = "Telethon" if telethon else "Pyrogram"
    if is_bot:
        ty += " Bot"
    await msg.reply(f"» Trying to start **{ty}** session generator...")
    api_id_msg = await msg.chat.ask(
        "Please send your **API_ID** to proceed.\n\nClick on /skip for using bot's api.",
        filters=filters.text,
    )
    if await is_batal(api_id_msg):
        return
    if api_id_msg.text == "/skip":
        api_id = API_ID
        api_hash = API_HASH
    else:
        try:
            api_id = int(api_id_msg.text)
            await api_id_msg.delete()
        except ValueError:
            return await api_id_msg.reply(
                "**API_ID** must be integer, start generating your session again.",
                quote=True,
                reply_markup=InlineKeyboardMarkup(gen_button),
            )
        api_hash_msg = await msg.chat.ask(
            "» Now please send your **API_HASH** to continue.", filters=filters.text
        )
        if await is_batal(api_hash_msg):
            return
        api_hash = api_hash_msg.text
        await api_hash_msg.delete()
    t = (
        "Please send your **BOT_TOKEN** to continue.\nExample : `5432198765:abcdanonymousterabaaplol`'"
        if is_bot
        else "» Please send your **PHONE_NUMBER** with country code for which you want generate session. \nᴇxᴀᴍᴩʟᴇ : `+6286356837789`'"
    )
    phone_number_msg = await msg.chat.ask(t, filters=filters.text)
    if await is_batal(phone_number_msg):
        return
    phone_number = phone_number_msg.text
    await phone_number_msg.delete()
    if not is_bot:
        await msg.reply("» Trying to send OTP at the given number...")
    else:
        await msg.reply("» Trying to login using Bot Token...")
    if telethon and is_bot or telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif is_bot:
        client = Client(
            name="bot",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=phone_number,
            in_memory=True,
        )
    else:
        client = Client(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)
    await client.connect()
    try:
        code = None
        if not is_bot:
            if telethon:
                code = await client.send_code_request(phone_number)
            else:
                code = await client.send_code(phone_number)
    except (ApiIdInvalid, ApiIdInvalidError):
        return await msg.reply(
            "» Your **API_ID** and **API_HASH** combination doesn't match. \n\nPlease start generating your session again.",
            reply_markup=InlineKeyboardMarkup(gen_button),
        )
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        return await msg.reply(
            "» The **PHONE_NUMBER** you've doesn't belong to any account in Telegram.\n\nPlease start generating your session again.",
            reply_markup=InlineKeyboardMarkup(gen_button),
        )
    try:
        phone_code_msg = None
        if not is_bot:
            phone_code_msg = await msg.chat.ask(
                "» Please send the **OTP** That you've received from Telegram on your account.\nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.",
                filters=filters.text,
                timeout=600,
            )
            if await is_batal(phone_code_msg):
                return
    except ListenerTimeout:
        return await msg.reply(
            "» Time limit reached of 10 minutes.\n\nPlease start generating your session again.",
            reply_markup=InlineKeyboardMarkup(gen_button),
        )
    if not is_bot:
        phone_code = phone_code_msg.text.replace(" ", "")
        await phone_code_msg.delete()
        try:
            if telethon:
                await client.sign_in(phone_number, phone_code, password=None)
            else:
                await client.sign_in(phone_number, code.phone_code_hash, phone_code)
        except (PhoneCodeInvalid, PhoneCodeInvalidError):
            return await msg.reply(
                "» The OTP you've sent is **wrong.**\n\nPlease start generating your session again.",
                reply_markup=InlineKeyboardMarkup(gen_button),
            )
        except (PhoneCodeExpired, PhoneCodeExpiredError):
            return await msg.reply(
                "» The OTP you've sent is **expired.**\n\nPlease start generating your session again.",
                reply_markup=InlineKeyboardMarkup(gen_button),
            )
        except (SessionPasswordNeeded, SessionPasswordNeededError):
            try:
                two_step_msg = await msg.chat.ask(
                    "» Please enter your **Two Step Verification** password to continue.",
                    filters=filters.text,
                    timeout=300,
                )
            except ListenerTimeout:
                return await msg.reply(
                    "» Time limit reached of 5 minutes.\n\nPlease start generating your session again.",
                    reply_markup=InlineKeyboardMarkup(gen_button),
                )
            try:
                password = two_step_msg.text
                await two_step_msg.delete()
                if telethon:
                    await client.sign_in(password=password)
                else:
                    await client.check_password(password=password)
                if await is_batal(api_id_msg):
                    return
            except (PasswordHashInvalid, PasswordHashInvalidError):
                return await two_step_msg.reply(
                    "» The password you've sent is wrong.\n\nPlease start generating session again.",
                    quote=True,
                    reply_markup=InlineKeyboardMarkup(gen_button),
                )
    elif telethon:
        try:
            await client.start(bot_token=phone_number)
        except Exception as err:
            return await msg.reply(err)
    else:
        try:
            await client.sign_in_bot(phone_number)
        except Exception as err:
            return await msg.reply(err)
    if telethon:
        string_session = client.session.save()
    else:
        string_session = await client.export_session_string()
    text = f"**This is your {ty} String Session** \n\n`{string_session}` \n\n**Generated By :** @{bot.me.username}\n🍒 **Note :** Don't share it to anyone  And don't forget to support this owner bot if you like🥺"
    try:
        if not is_bot:
            await client.send_message("me", text)
        else:
            await bot.send_message(msg.chat.id, text)
    except KeyError:
        pass
    await client.disconnect()
    await bot.send_message(
        msg.chat.id,
        f'» Successfully generated your {"Telethon" if telethon else "Pyrogram"} String Session.\n\nPlease check saved messages to get it ! \n\n**A String Generator bot by ** @IAmCuteCodes',
    )
