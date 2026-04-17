"""
* @author        yasir <yasiramunandar@gmail.com>
* @date          2022-12-01 09:12:27
* @projectName   MissKatyPyro
* Copyright @YasirPedia All rights reserved
"""
import contextlib
import re

from pyrogram import Client, filters
from pyrogram import types as pyro_types
from pyrogram.errors import ChatSendPhotosForbidden, ChatWriteForbidden, QueryIdInvalid
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from database.users_chats_db import db
from misskaty import BOT_NAME, BOT_USERNAME, HELPABLE, app
from misskaty.helper import bot_sys_stats, paginate_modules
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER

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

home_text_pm = f"Hello <emoji id=5303081040464585038>🤗</emoji>, My name is <b>{BOT_NAME}</b> <emoji id=5474618190271104037>🐈</emoji>.\nI'm a bot with some useful features. You can change language bot using /setlang command, but it's still in beta stage.\nYou can choose an option below, by clicking a button."

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

FED_MARKUP = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Fed Owner Commands", callback_data="fed_owner"),
            InlineKeyboardButton("Fed Admin Commands", callback_data="fed_admin"),
        ],
        [
            InlineKeyboardButton("User Commands", callback_data="fed_user"),
        ],
        [
            InlineKeyboardButton("Back", callback_data="help_back"),
        ],
    ]
)


@app.on_message(filters.command("start", COMMAND_HANDLER))
@app.on_managed_bot()
@use_chat_lang()
async def start(self, ctx, strings):
    if ctx.chat.type.value != "private":
        nama = ctx.from_user.mention if ctx.from_user else ctx.sender_chat.title
        try:
            return await ctx.reply_photo(
                photo="https://img.yasirweb.eu.org/file/90e9a448bc2f8b055b762.jpg",
                caption=strings("start_msg").format(kamuh=nama),
                reply_markup=keyboard,
            )
        except (ChatSendPhotosForbidden, ChatWriteForbidden):
            return await ctx.chat.leave()
    if ctx.from_user and not await db.is_user_exist(ctx.from_user.id):
        await db.add_user(ctx.from_user.id, ctx.from_user.first_name)

    if len(ctx.text.split()) > 1:
        name = (ctx.text.split(None, 1)[1]).lower()
        if "_" in name:
            module = name.split("_", 1)[1]
            mod_obj = HELPABLE.get(module)
            if not mod_obj:
                return await ctx.reply("Unknown help module.")
            text = strings("help_name").format(mod=mod_obj.__MODULE__) + mod_obj.__HELP__
            await ctx.reply(
                text,
                link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                effect_id=5104841245755180586,
            )
            if module == "federation":
                return await ctx.reply(
                    text=text,
                    reply_markup=FED_MARKUP,
                    link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                    effect_id=5104841245755180586,
                )
            await ctx.reply(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("back", callback_data="help_back")]]
                ),
                link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                effect_id=5104841245755180586,
            )
        elif name == "help":
            text, keyb = await help_parser(ctx.from_user.first_name, strings)
            await ctx.reply(
                text, reply_markup=keyb, effect_id=5104841245755180586
            )
    else:
        await self.send_photo(
            ctx.chat.id,
            photo="https://img.yasirweb.eu.org/file/90e9a448bc2f8b055b762.jpg",
            caption=home_text_pm,
            reply_markup=home_keyboard_pm,
            reply_parameters=pyro_types.ReplyParameters(message_id=ctx.id),
        )


@app.on_callback_query(filters.regex("bot_commands"))
@use_chat_lang()
async def commands_callbacc(_, cb: CallbackQuery, strings):
    text, keyb = await help_parser(cb.from_user.mention, strings)
    await app.send_message(
        cb.message.chat.id,
        text=text,
        reply_markup=keyb,
        effect_id=5104841245755180586,
    )
    await cb.message.delete_msg()


@app.on_callback_query(filters.regex("stats_callback"))
async def stats_callbacc(_, cb: CallbackQuery):
    text = await bot_sys_stats()
    with contextlib.suppress(QueryIdInvalid):
        await app.answer_callback_query(cb.id, text, show_alert=True)


@app.on_message(filters.command("help", COMMAND_HANDLER))
@use_chat_lang()
async def help_command(_, ctx: Message, strings):
    if ctx.chat.type.value != "private":
        if len(ctx.command) >= 2:
            name = (ctx.text.split(None, 1)[1]).replace(" ", "_").lower()
            if str(name) in HELPABLE:
                key = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=strings("click_me"),
                                url=f"t.me/{BOT_USERNAME}?start=help_{name}",
                            )
                        ],
                    ]
                )
                await ctx.reply(
                    strings("click_btn").format(nm=name),
                    reply_markup=key,
                )
            else:
                await ctx.reply(strings("pm_detail"), reply_markup=keyboard)
        else:
            await ctx.reply(strings("pm_detail"), reply_markup=keyboard)
    elif len(ctx.command) >= 2:
        name = (ctx.text.split(None, 1)[1]).replace(" ", "_").lower()
        if str(name) in HELPABLE:
            text = (
                strings("help_name").format(mod=HELPABLE[name].__MODULE__)
                + HELPABLE[name].__HELP__
            )
            await ctx.reply(
                text,
                link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                effect_id=5104841245755180586,
            )
        else:
            text, help_keyboard = await help_parser(ctx.from_user.first_name, strings)
            await ctx.reply(
                text,
                reply_markup=help_keyboard,
                link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                effect_id=5104841245755180586,
            )
    else:
        text, help_keyboard = await help_parser(ctx.from_user.first_name, strings)
        await ctx.reply(
            text,
            reply_markup=help_keyboard,
            link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
            effect_id=5104841245755180586,
        )


async def help_parser(name, strings, keyb=None):
    if not keyb:
        keyb = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    return (
        strings("help_txt").format(kamuh=name, bot=BOT_NAME),
        keyb,
    )


@app.on_callback_query(filters.regex(r"help_(.*?)"))
@use_chat_lang()
async def help_button(self: Client, query: CallbackQuery, strings):
    home_match = re.match(r"help_home\((.+?)\)", query.data)
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    create_match = re.match(r"help_create", query.data)
    top_text = strings("help_txt").format(
        kamuh=query.from_user.first_name, bot=self.me.first_name
    )
    if mod_match:
        module = mod_match[1].replace(" ", "_")
        mod_obj = HELPABLE.get(module)
        if not mod_obj:
            return await query.answer("Module not found", show_alert=True)
        text = strings("help_name").format(mod=mod_obj.__MODULE__) + mod_obj.__HELP__
        if module == "federation":
            return await query.message.edit(
                text=text,
                reply_markup=FED_MARKUP,
                link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
            )
        await query.message.edit(
            text=text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(strings("back_btn"), callback_data="help_back")]]
            ),
            link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
        )
    elif home_match:
        await app.send_msg(
            query.from_user.id,
            text=home_text_pm,
            reply_markup=home_keyboard_pm,
        )
        await query.message.delete_msg()
    elif prev_match:
        curr_page = int(prev_match[1])
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(curr_page - 1, HELPABLE, "help")
            ),
            link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
        )

    elif next_match:
        next_page = int(next_match[1])
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(next_page + 1, HELPABLE, "help")
            ),
            link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
        )

    elif back_match:
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")),
            link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
        )

    elif create_match:
        text, keyb = await help_parser(query.from_user.first_name, strings)
        await query.message.edit(
            text=text,
            reply_markup=keyb,
            link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
        )

    try:
        await self.answer_callback_query(query.id)
    except:
        pass
