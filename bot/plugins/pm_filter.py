# Kanged From @TroJanZheX
import time
import shutil, psutil

from Script import script
from bot import botStartTime, app
from bot.helper.human_read import get_readable_time, get_readable_file_size
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, enums
from utils import get_size, temp
from database.users_chats_db import db
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}


@app.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
        buttons = [
            [
                InlineKeyboardButton(
                    "➕ Tambahkan Saya ke Grup ➕",
                    url=f"http://t.me/{temp.U_NAME}?startgroup=true")
            ],
            [
                InlineKeyboardButton("YMovieZNew Channel",
                                     url="https://t.me/YMovieZNew"),
                InlineKeyboardButton("Updates",
                                     url="https://t.me/YasirPediaChannel")
            ],
            [
                InlineKeyboardButton("ℹ️ Help", callback_data="help"),
                InlineKeyboardButton("😊 About", callback_data="about")
            ],
            [
                InlineKeyboardButton("📦 Source Code",
                                     url="tg://need_update_for_some_feature")
            ],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(text=script.START_TXT.format(
            query.from_user.mention, temp.U_NAME, temp.B_NAME),
                                      reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)
    elif query.data == "help":
        buttons = [
            [
                InlineKeyboardButton("Admin", callback_data="manuelfilter"),
                InlineKeyboardButton("Code Runner", callback_data="autofilter")
            ],
            [
                InlineKeyboardButton("Connection", callback_data="coct"),
                InlineKeyboardButton("Extra Mods", callback_data="extra")
            ],
            [
                InlineKeyboardButton("🏠 Home", callback_data="start"),
                InlineKeyboardButton("🔮 Status", callback_data="stats")
            ],
            [InlineKeyboardButton("Web Scraper", callback_data="scrap")],
        ]
        currentTime = get_readable_time(time.time() - botStartTime)
        total, used, free = shutil.disk_usage(".")
        total = get_readable_file_size(total)
        used = get_readable_file_size(used)
        free = get_readable_file_size(free)
        cpuUsage = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(text=script.HELP_TXT.format(
            query.from_user.mention, currentTime, total, free, used, cpuUsage,
            memory, disk),
                                      reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)
    elif query.data == "about":
        buttons = [
            [
                InlineKeyboardButton("🤖 Updates",
                                     url="https://t.me/YasirPediaChannel"),
                InlineKeyboardButton("♥️ Source", callback_data="source")
            ],
            [
                InlineKeyboardButton("🏠 Home", callback_data="start"),
                InlineKeyboardButton("🔐 Close", callback_data="close_data")
            ],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(text=script.ABOUT_TXT.format(
            temp.B_NAME),
                                      reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)
    elif query.data == "source":
        buttons = [[InlineKeyboardButton("👩‍🦯 Back", callback_data="about")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(text=script.SOURCE_TXT,
                                      reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton("👩‍🦯 Back", callback_data="help"),
            InlineKeyboardButton("⏹️ Buttons", callback_data="button")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(text=script.MANUELFILTER_TXT,
                                      reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton("👩‍🦯 Back", callback_data="manuelfilter")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(text=script.BUTTON_TXT,
                                      reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)
    elif query.data == "autofilter":
        buttons = [[InlineKeyboardButton("👩‍🦯 Back", callback_data="help")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(text=script.AUTOFILTER_TXT,
                                      reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)
    elif query.data == "scrap":
        buttons = [[InlineKeyboardButton("👩‍🦯 Back", callback_data="help")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        teks = script.SCRAP_TXT
        await query.message.edit_text(text=teks,
                                      reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)
    elif query.data == "coct":
        buttons = [[InlineKeyboardButton("👩‍🦯 Back", callback_data="help")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(text=script.CONNECTION_TXT,
                                      reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton("👩‍🦯 Back", callback_data="help"),
            InlineKeyboardButton("👮‍♂️ Admin", callback_data="admin")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(text=script.EXTRAMOD_TXT,
                                      reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)
    elif query.data == "admin":
        buttons = [[InlineKeyboardButton("👩‍🦯 Back", callback_data="extra")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(text=script.ADMIN_TXT,
                                      reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton("👩‍🦯 Back", callback_data="help"),
            InlineKeyboardButton("♻️", callback_data="rfrsh")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = "None"
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(text=script.STATUS_TXT.format(
            total, users, chats, monsize, free),
                                      reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton("👩‍🦯 Back", callback_data="help"),
            InlineKeyboardButton("♻️", callback_data="rfrsh")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = "None"
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(text=script.STATUS_TXT.format(
            total, users, chats, monsize, free),
                                      reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)
