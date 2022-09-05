import os
import time
import logging
import random
import asyncio
from Script import script
import shutil, psutil

from pyrogram import Client, filters, enums
from bot import botStartTime, app
from bot.utils.human_read import get_readable_time, get_readable_file_size
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.users_chats_db import db
from info import ADMINS, CHANNELS, COMMAND_HANDLER, LOG_CHANNEL, PICS
from utils import temp

logger = logging.getLogger(__name__)

# @app.on_message(
#     filters.command(["help", "help@MissKatyRoBot"], COMMAND_HANDLER))
# async def help(client, message):
#     if message.chat.type in ["group", "supergroup"]:
#         buttons = [
#             [
#                 InlineKeyboardButton(
#                     text="ℹ️ Klik Saya",
#                     url=f"https://t.me/{temp.U_NAME}?start=help")
#             ],
#         ]
#         return await message.reply(
#             "Silahkan PM saya untuk melihat menu bantuan..",
#             reply_markup=InlineKeyboardMarkup(buttons))
#     else:
#         buttons = [
#             [
#                 InlineKeyboardButton("Admin", callback_data="manuelfilter"),
#                 InlineKeyboardButton("Code Runner", callback_data="autofilter")
#             ],
#             [
#                 InlineKeyboardButton("Connection", callback_data="coct"),
#                 InlineKeyboardButton("Misc", callback_data="extra")
#             ],
#             [
#                 InlineKeyboardButton("🏠 Home", callback_data="start"),
#                 InlineKeyboardButton("🔮 Status", callback_data="stats")
#             ],
#         ]
#         currentTime = get_readable_time(time.time() - botStartTime)
#         total, used, free = shutil.disk_usage(".")
#         total = get_readable_file_size(total)
#         used = get_readable_file_size(used)
#         free = get_readable_file_size(free)
#         cpuUsage = psutil.cpu_percent(interval=0.5)
#         memory = psutil.virtual_memory().percent
#         disk = psutil.disk_usage("/").percent
#         reply_markup = InlineKeyboardMarkup(buttons)
#         await message.reply_text(text=script.HELP_TXT.format(
#             message.from_user.mention, currentTime, total, free, used,
#             cpuUsage, memory, disk),
#                                  reply_markup=reply_markup,
#                                  parse_mode=enums.ParseMode.HTML)

# @app.on_message(
#     filters.command(["start", "start@MissKatyRoBot"], COMMAND_HANDLER))
# async def start(client, message):
#     if message.chat.type == "private" and message.text == "/start help":
#         buttons = [
#             [
#                 InlineKeyboardButton("Admin", callback_data="manuelfilter"),
#                 InlineKeyboardButton("Code Runner", callback_data="autofilter")
#             ],
#             [
#                 InlineKeyboardButton("Stickers", callback_data="coct"),
#                 InlineKeyboardButton("Misc", callback_data="extra")
#             ],
#             [
#                 InlineKeyboardButton("🏠 Home", callback_data="start"),
#                 InlineKeyboardButton("🔮 Status", callback_data="stats")
#             ],
#         ]
#         currentTime = get_readable_time(time.time() - botStartTime)
#         total, used, free = shutil.disk_usage(".")
#         total = get_readable_file_size(total)
#         used = get_readable_file_size(used)
#         free = get_readable_file_size(free)
#         cpuUsage = psutil.cpu_percent(interval=0.5)
#         memory = psutil.virtual_memory().percent
#         disk = psutil.disk_usage("/").percent
#         reply_markup = InlineKeyboardMarkup(buttons)
#         await message.reply_text(text=script.HELP_TXT.format(
#             message.from_user.mention, currentTime, total, free, used,
#             cpuUsage, memory, disk),
#                                  reply_markup=reply_markup,
#                                  parse_mode=enums.ParseMode.HTML)
#         return
#     if message.chat.type in ["group", "supergroup"]:
#         buttons = [
#             [
#                 InlineKeyboardButton("🤖 Updates",
#                                      url="https://t.me/YasirPediaChannel")
#             ],
#             [
#                 InlineKeyboardButton(
#                     "ℹ️ Help", url=f"https://t.me/{temp.U_NAME}?start=help"),
#             ],
#         ]
#         reply_markup = InlineKeyboardMarkup(buttons)
#         await message.reply(script.START_TXT.format(
#             message.from_user.mention if message.from_user else
#             message.chat.title, temp.U_NAME, temp.B_NAME),
#                             reply_markup=reply_markup,
#                             disable_web_page_preview=True)
#         await asyncio.sleep(
#             2
#         )  # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
#         if not await db.get_chat(message.chat.id):
#             total = await client.get_chat_members_count(message.chat.id)
#             await client.send_message(
#                 LOG_CHANNEL,
#                 script.LOG_TEXT_G.format(message.chat.title, message.chat.id,
#                                          total, "Unknown"))
#             await db.add_chat(message.chat.id, message.chat.title)
#         return
#     if not await db.is_user_exist(message.from_user.id):
#         await db.add_user(message.from_user.id, message.from_user.first_name)
#         await client.send_message(
#             LOG_CHANNEL,
#             script.LOG_TEXT_P.format(message.from_user.id,
#                                      message.from_user.mention))
#     if message.text == "/start":
#         buttons = [
#             [
#                 InlineKeyboardButton(
#                     "➕ Tambahkan Saya ke Grup ➕",
#                     url=f"http://t.me/{temp.U_NAME}?startgroup=true")
#             ],
#             [
#                 InlineKeyboardButton("YMovieZNew Channel",
#                                      url="https://t.me/YMovieZNew"),
#                 InlineKeyboardButton("Updates",
#                                      url="https://t.me/YasirPediaChannel")
#             ],
#             [
#                 InlineKeyboardButton("ℹ️ Help", callback_data="help"),
#                 InlineKeyboardButton("😊 About", callback_data="about")
#             ],
#             [
#                 InlineKeyboardButton("📦 Source Code",
#                                      url="tg://need_update_for_some_feature")
#             ],
#         ]
#         reply_markup = InlineKeyboardMarkup(buttons)
#         await message.reply_photo(photo=random.choice(PICS),
#                                   caption=script.START_TXT.format(
#                                       message.from_user.mention, temp.U_NAME,
#                                       temp.B_NAME),
#                                   reply_markup=reply_markup,
#                                   parse_mode=enums.ParseMode.HTML)
#         return

@app.on_message(filters.command(["logs"]) & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document("MissKatyLogs.txt")
    except Exception as e:
        await message.reply(str(e))
