from asyncio import sleep
from datetime import datetime
import time
import logging
import os
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ChatMemberUpdated
from pyrogram.errors import MessageTooLong, PeerIdInvalid, RightForbidden, RPCError, UserAdminInvalid, FloodWait
from bot import app
from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, COMMAND_HANDLER
from bot.utils.admin_helper import is_admin
from PIL import Image, ImageChops, ImageDraw, ImageFont
import textwrap
from database.users_chats_db import db
from utils import get_size, temp
from Script import script
from pyrogram.errors import ChatAdminRequired


def circle(pfp, size=(215, 215)):
    pfp = pfp.resize(size, Image.ANTIALIAS).convert("RGBA")
    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp


def draw_multiple_line_text(image, text, font, text_start_height):
    '''
    From unutbu on [python PIL draw multiline text on image](https://stackoverflow.com/a/7698300/395857)
    '''
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    y_text = text_start_height
    lines = textwrap.wrap(text, width=38)
    for line in lines:
        line_width, line_height = font.getsize(line)
        draw.text(((image_width - line_width) / 2, y_text),
                  line,
                  font=font,
                  fill="black")
        y_text += line_height


async def welcomepic(pic, user, chat, count, id):
    background = Image.open(
        "/YasirBot/img/bg.png")  # <- Background Image (Should be PNG)
    background = background.resize((1024, 500), Image.ANTIALIAS)
    pfp = Image.open(pic).convert("RGBA")
    pfp = circle(pfp)
    pfp = pfp.resize(
        (265,
         265))  # Resizes the Profilepicture so it fits perfectly in the circle
    font = ImageFont.truetype(
        "/YasirBot/LemonMilkMedium-mLZYV.otf", 42
    )  # <- Text Font of the Member Count. Change the text size for your preference
    member_text = (f"User#{count} Selamat Datang {user}"
                   )  # <- Text under the Profilepicture with the Membercount
    draw_multiple_line_text(background, member_text, font, 385)
    draw_multiple_line_text(background, chat, font, 23)
    background.paste(pfp, (379, 123),
                     pfp)  # Pastes the Profilepicture on the Background Image
    background.save(
        f"/YasirBot/welcome#{id}.png"
    )  # Saves the finished Image in the folder with the filename
    return f"/YasirBot/welcome#{id}.png"


@app.on_chat_member_updated(filters.group & filters.chat(-1001128045651))
async def member_has_joined(c: app, member: ChatMemberUpdated):
    MEMJOIN = {}
    if (not member.new_chat_member or member.new_chat_member.status
            in {"banned", "left", "restricted"} or member.old_chat_member):
        return
    user = member.new_chat_member.user if member.new_chat_member else member.from_user
    if user.id == 617426792:
        await c.send_message(
            member.chat.id,
            "Waw, owner kamu baru saja bergabung ke grup!",
        )
        return
    elif user.is_bot:
        return  # ignore bots
    else:
        if (temp.MELCOW).get('welcome') is not None:
            try:
                await (temp.MELCOW['welcome']).delete()
            except:
                pass
        mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
        joined_date = datetime.fromtimestamp(
            time.time()).strftime("%Y.%m.%d %H:%M:%S")
        first_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        id = user.id
        dc = user.dc_id if user.dc_id else "Member tanpa PP"
        count = await app.get_chat_members_count(member.chat.id)
        try:
            pic = await app.download_media(user.photo.big_file_id,
                                           file_name=f"pp{user.id}.png")
        except AttributeError:
            pic = "/YasirBot/img/profilepic.png"
        welcomeimg = await welcomepic(pic, user.first_name, member.chat.title,
                                      count, user.id)
        temp.MELCOW['welcome'] = await c.send_photo(
            member.chat.id,
            photo=welcomeimg,
            caption=
            f"Hai {mention}, Selamat datang digrup {member.chat.title} harap baca rules di pinned message terlebih dahulu.\n\n<b>Nama :<b> <code>{first_name}</code>\n<b>ID :<b> <code>{id}</code>\n<b>DC ID :<b> <code>{dc}</code>\n<b>Tanggal Join :<b> <code>{joined_date}</code>",
        )
        try:
            os.remove(f"/YasirBot/welcome#{user.id}.png")
            os.remove(f"/YasirBot/downloads/pp{user.id}.png")
        except Exception as err:
            logging.error(err)
        #temp.MELCOW['welcome'] = await c.send_message(
        #    member.chat.id,
        #    f"Hai {mention}, Selamat datang digrup {member.chat.title} harap baca rules di pinned message terlebih dahulu.\n\n<b>Nama :<b> <code>{first_name}</code>\n<b>ID :<b> <code>{id}</code>\n<b>DC ID :<b> <code>{dc}</code>\n<b>Tanggal Join :<b> <code>{joined_date}</code>",
        #)


@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    r_j_check = [u.id for u in message.new_chat_members]
    if temp.ME in r_j_check:
        if not await db.get_chat(message.chat.id):
            total = await bot.get_chat_members_count(message.chat.id)
            r_j = message.from_user.mention if message.from_user else "Anonymous"
            await bot.send_message(
                LOG_CHANNEL,
                script.LOG_TEXT_G.format(message.chat.title, message.chat.id,
                                         total, r_j))
            await db.add_chat(message.chat.id, message.chat.title)
        if message.chat.id in temp.BANNED_CHATS:
            # Inspired from a boat of a banana tree
            buttons = [[
                InlineKeyboardButton('Support',
                                     url=f'https://t.me/{SUPPORT_CHAT}')
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            k = await message.reply(
                text=
                '<b>CHAT NOT ALLOWED 🐞\n\nMy admins has restricted me from working here ! If you want to know more about it contact support..</b>',
                reply_markup=reply_markup,
            )

            try:
                await k.pin()
            except:
                pass
            await bot.leave_chat(message.chat.id)
            return
        buttons = [[
            InlineKeyboardButton('ℹ️ Help',
                                 url=f"https://t.me/{temp.U_NAME}?start=help"),
            InlineKeyboardButton('📢 Updates',
                                 url='https://t.me/YasirPediaChannel')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=
            f"<b>Terimakasih sudah menambahkan saya di {message.chat.title} ❣️\n\nJika ada kendala atau saran bisa kontak ke saya.</b>",
            reply_markup=reply_markup)
    else:
        for u in message.new_chat_members:
            count = await app.get_chat_members_count(message.chat.id)
            try:
                pic = await app.download_media(u.photo.big_file_id,
                                               file_name=f"pp{u.id}")
            except AttributeError:
                pic = "/YasirBot/img/profilepic.png"
            welcomeimg = await welcomepic(pic, u.first_name,
                                          message.chat.title, count, u.id)
            if (temp.MELCOW).get('welcome') is not None:
                try:
                    await (temp.MELCOW['welcome']).delete()
                except:
                    pass
            temp.MELCOW['welcome'] = await app.send_photo(
                message.chat.id,
                photo=welcomeimg,
                caption=
                f"Hai {u.mention}, Selamat datang digrup {message.chat.title}.",
            )
            try:
                os.remove(f"/YasirBot/welcome#{u.id}.png")
                os.remove(f"/YasirBot/downloads/pp{u.id}.png")
            except Exception as err:
                logging.error(err)


@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        buttons = [[
            InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat,
            text=
            '<b>Hai kawan, \nOwner aku bilang saya harus pergi! Jika kamu ingin menambahkan bot ini lagi silahkan kontak owner bot ini.</b>',
            reply_markup=reply_markup,
        )
        await bot.leave_chat(chat)
    except Exception as e:
        await message.reply(f'Error - {e}')


@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    cha_t = await db.get_chat(chat_)
    if not cha_t:
        return await message.reply("Chat Not Found In DB")
    if cha_t['is_disabled']:
        return await message.reply(
            f"This chat is already disabled:\nReason-<code> {cha_t['reason']} </code>"
        )
    await db.disable_chat(chat_, reason)
    temp.BANNED_CHATS.append(chat_)
    await message.reply('Chat Succesfully Disabled')
    try:
        buttons = [[
            InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_,
            text=
            f'<b>Hello Friends, \nMy admin has told me to leave from group so i go! If you wanna add me again contact my support group.</b> \nReason : <code>{reason}</code>',
            reply_markup=reply_markup)
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f"Error - {e}")


@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply("Chat Not Found In DB !")
    if not sts.get('is_disabled'):
        return await message.reply('This chat is not yet disabled.')
    await db.re_enable_chat(chat_)
    temp.BANNED_CHATS.remove(chat_)
    await message.reply("Chat Succesfully re-enabled")


# a function for trespassing into others groups, Inspired by a Vazha
# Not to be used , But Just to showcase his vazhatharam.
# @Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    try:
        link = await bot.create_chat_invite_link(chat)
    except ChatAdminRequired:
        return await message.reply(
            "Invite Link Generation Failed, Iam Not Having Sufficient Rights")
    except Exception as e:
        return await message.reply(f'Error {e}')
    await message.reply(f'Here is your Invite Link {link.invite_link}')


@app.on_message(
    filters.command(["adminlist", "adminlist@MissKatyRoBot"], COMMAND_HANDLER))
async def adminlist(_, message):
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply("Perintah ini hanya untuk grup")
    try:
        administrators = []
        async for m in app.get_chat_members(
                message.chat.id,
                filter=enums.ChatMembersFilter.ADMINISTRATORS):
            administrators.append(f"{m.user.first_name}")

        res = "".join(f"~ {i}\n" for i in administrators)
        return await message.reply(
            f"Daftar Admin di <b>{message.chat.title}</b> ({message.chat.id}):\n~ {res}"
        )
    except Exception as e:
        await message.reply(f"ERROR: {str(e)}")


@app.on_message(
    filters.command(["zombies", "zombies@MissKatyRoBot"], COMMAND_HANDLER))
async def zombie_clean(_, m):

    zombie = 0
    wait = await m.reply_text("Searching ... and banning ...")
    async for member in app.iter_chat_members(m.chat.id):
        if member.user.is_deleted:
            zombie += 1
            try:
                await app.kick_chat_member(m.chat.id, member.user.id)
            except UserAdminInvalid:
                zombie -= 1
            except FloodWait as e:
                await sleep(e.x)
    if zombie == 0:
        return await wait.edit_text("Group is clean!")
    return await wait.edit_text(
        f"<b>{zombie}</b> Zombies ditemukan dan telah banned!", )


@Client.on_message(
    filters.command(["kickme", "kickme@MissKatyRoBot"], COMMAND_HANDLER))
async def kickme(_, message):
    reason = None
    if len(message.text.split()) >= 2:
        reason = message.text.split(None, 1)[1]
    try:
        await message.chat.kick_member(message.from_user.id)
        txt = f"Pengguna {message.from_user.mention} menendang dirinya sendiri. Mungkin dia sedang frustasi 😕"
        txt += f"\n<b>Alasan</b>: {reason}" if reason else ""
        await message.reply_text(txt)
        await message.chat.unban_member(message.from_user.id)
    except RPCError as ef:
        await message.reply_text(
            f"Sepertinya ada error, silahkan report ke owner saya. \nERROR: {str(ef)}"
        )
    return


@app.on_message(filters.command(['pin', 'pin@MissKatyRoBot'], COMMAND_HANDLER))
async def pin(_, message):
    if message.reply_to_message:
        message_id = message.reply_to_message.id
        if await is_admin(message.chat.id, message.from_user.id):
            await app.pin_chat_message(message.chat.id, message_id)
            await message.reply("Berhasil menyematkan pesan ini",
                                reply_to_message_id=message_id)
    elif not await is_admin(message.chat.id, message.from_user.id):
        await message.reply("Uppss, kamu bukan admin disini..")
    else:
        message.reply("Balas ke pesan yang mau dipin.")


@app.on_message(
    filters.command(['unpin', 'unpin@MissKatyRoBot'], COMMAND_HANDLER))
async def unpin(_, message):
    if message.reply_to_message:
        message_id = message.reply_to_message.id
        if await is_admin(message.chat.id, message.from_user.id):
            await app.unpin_chat_message(message.chat.id, message_id)
            await message.reply("Berhasil unpin pesan ini",
                                reply_to_message_id=message_id)
    elif not await is_admin(message.chat.id, message.from_user.id):
        await message.reply("Upps, kamu bukan admin disini")
    else:
        await message.reply("Balas ke pesan yang mau diunpin")


@app.on_message(
    filters.command(['dban', 'dban@MissKatyRoBot'], COMMAND_HANDLER)
    & filters.group)
async def ban_a_user(_, message):
    admin = await app.get_chat_member(message.chat.id, message.from_user.id)
    if admin.status not in ['administrator', 'creator']:
        await message.reply_text("Kamu bukan admin disini")
        await message.stop_propagation()

    if len(message.text.split()) == 1 and not message.reply_to_message:
        await message.reply_text(
            "Gunakan command ini dengan reply atau mention user")
        await message.stop_propagation()

    if not message.reply_to_message:
        return await message.reply_text(
            "Balas ke pesan untuk delete dan ban pengguna!")

    user_id, user_first_name = ((
        message.reply_to_message.from_user.id,
        message.reply_to_message.from_user.first_name,
    ) if message.reply_to_message.from_user else (
        message.reply_to_message.sender_chat.id,
        message.reply_to_message.sender_chat.title,
    ))

    if not user_id:
        await message.reply_text(
            "Aku tidak bisa menemukan pengguna untuk diban")
        return
    if user_id == message.chat.id:
        await message.reply_text("Itu adalah hal gila jika saya ban admin!")
        await message.stop_propagation()
    if user_id == 1507530289:
        await message.reply_text("Hah, saya harus ban diriku sendiri?")
        await message.stop_propagation()

    admin = await app.get_chat_member(message.chat.id,
                                      message.reply_to_message.from_user.id)
    if user_id in ['administrator', 'creator']:
        await message.reply_text("Saya tidak bisa ban admin")
        await message.stop_propagation()

    reason = None
    if len(message.text.split()) >= 2:
        reason = message.text.split(None, 1)[1]

    try:
        await message.reply_to_message.delete()
        await message.chat.kick_member(user_id)
        txt = f"{message.from_user.mention} banned {message.reply_to_message.from_user.mention} di <b>{message.chat.title}</b>!"

        txt += f"\n<b>Alasan</b>: {reason}" if reason else ""
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "⚠️ Unban (Hanya Admin)",
                callback_data=f"unban_={user_id}",
            ),
        ]])
        await app.send_message(message.chat.id, txt, reply_markup=keyboard)
    except ChatAdminRequired:
        await message.reply_text("Sepertinya aku bukan admin disini.")
    except PeerIdInvalid:
        await message.reply_text(
            "Aku belum pernah melihat pengguna ini sebelumnya...!\nMungkin bisa dengan forward pesan dia?",
        )
    except UserAdminInvalid:
        await message.reply_text(
            "Tidak dapat bertindak atas pengguna ini, mungkin bukan saya yang mengubah izinnya"
        )
    except RightForbidden:
        await message.reply_text(
            "Aku tidak punya ijin untuk membanned pengguna ini")
    except RPCError as ef:
        await message.reply_text(
            f"Sepertinya ada yg salah, silahkan lapor ke owner saya.\nERROR: {str(ef)}"
        )


@Client.on_callback_query(filters.regex("^unban_"))
async def unbanbutton(bot: Client, q: CallbackQuery):
    splitter = (str(q.data).replace("unban_", "")).split("=")
    user_id = int(splitter[1])
    user = await q.message.chat.get_member(q.from_user.id)

    if not user.can_restrict_members and q.from_user.id != 617426792:
        await q.answer(
            "Kamu ga punya cukup ijin untuk melakukan ini!!",
            show_alert=True,
        )
        return
    whoo = await bot.get_chat(user_id)
    doneto = whoo.title or whoo.first_name
    ids = whoo.id
    try:
        await q.message.chat.unban_member(user_id)
    except RPCError as e:
        await q.message.edit_text(f"Error: {e}")
        return
    await q.message.edit_text(
        f"{q.from_user.mention} unbanned <a href='tg://user?id={ids}'>{doneto}</a>!"
    )
    return


@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply(
            "This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply(
            "Thismight be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply(f"{k.mention} is not yet banned.")
        await db.remove_ban(k.id)
        temp.BANNED_USERS.remove(k.id)
        await message.reply(f"Succesfully unbanned {k.mention}")


@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    # https://t.me/GetTGLink/4184
    raju = await message.reply('Getting List Of Users')
    users = await db.get_all_users()
    out = "Users Saved In DB Are:\n\n"
    async for user in users:
        out += f"<a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += '( Banned User )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="List Of Users")


@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    raju = await message.reply('Getting List Of chats')
    chats = await db.get_all_chats()
    out = "Chats Saved In DB Are:\n\n"
    async for chat in chats:
        out += f"**Title:** `{chat['title']}`\n**- ID:** `{chat['id']}`"
        if chat['chat_status']['is_disabled']:
            out += '( Disabled Chat )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="List Of Chats")
