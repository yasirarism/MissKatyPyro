from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import MessageTooLong, PeerIdInvalid, RightForbidden, RPCError, UserAdminInvalid
from bot import app
from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, COMMAND_HANDLER
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import get_size, temp
from Script import script
from pyrogram.errors import ChatAdminRequired

"""-----------------------------------------https://t.me/GetTGLink/4179 --------------------------------------"""

@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    r_j_check = [u.id for u in message.new_chat_members]
    if temp.ME in r_j_check:
        if not await db.get_chat(message.chat.id):
            total=await bot.get_chat_members_count(message.chat.id)
            r_j = message.from_user.mention if message.from_user else "Anonymous" 
            await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, r_j))       
            await db.add_chat(message.chat.id, message.chat.title)
        if message.chat.id in temp.BANNED_CHATS:
            # Inspired from a boat of a banana tree
            buttons = [[
                InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
            ]]
            reply_markup=InlineKeyboardMarkup(buttons)
            k = await message.reply(
                text='<b>CHAT NOT ALLOWED 🐞\n\nMy admins has restricted me from working here ! If you want to know more about it contact support..</b>',
                reply_markup=reply_markup,
            )

            try:
                await k.pin()
            except:
                pass
            await bot.leave_chat(message.chat.id)
            return
        buttons = [[
            InlineKeyboardButton('ℹ️ Help', url=f"https://t.me/{temp.U_NAME}?start=help"),
            InlineKeyboardButton('📢 Updates', url='https://t.me/TeamEvamaria')
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=f"<b>Terimakasih sudah menambahkan saya di {message.chat.title} ❣️\n\nJika ada kendala atau saran bisa kontak ke saya.</b>",
            reply_markup=reply_markup)
    else:
        for u in message.new_chat_members:
            if (temp.MELCOW).get('welcome') is not None:
                try:
                    await (temp.MELCOW['welcome']).delete()
                except:
                    pass
            temp.MELCOW['welcome'] = await message.reply(f"<b>Hai, {u.mention}, Selamat datang di {message.chat.title}</b>")


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
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat,
            text='<b>Hai kawan, \nOwner aku bilang saya harus pergi! Jika kamu ingin menambahkan bot ini lagi silahkan kontak owner bot ini.</b>',
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
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply("Chat Not Found In DB")
    if cha_t['is_disabled']:
        return await message.reply(f"This chat is already disabled:\nReason-<code> {cha_t['reason']} </code>")
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    await message.reply('Chat Succesfully Disabled')
    try:
        buttons = [[
            InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_, 
            text=f'<b>Hello Friends, \nMy admin has told me to leave from group so i go! If you wanna add me again contact my support group.</b> \nReason : <code>{reason}</code>',
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
    await db.re_enable_chat(int(chat_))
    temp.BANNED_CHATS.remove(int(chat_))
    await message.reply("Chat Succesfully re-enabled")


@Client.on_message(filters.command('stats') & filters.incoming)
async def get_ststs(bot, message):
    rju = await message.reply('Fetching stats..')
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    files = await Media.count_documents()
    size = await db.get_db_size()
    free = 536870912 - size
    size = get_size(size)
    free = get_size(free)
    await rju.edit(script.STATUS_TXT.format(files, total_users, totl_chats, size, free))


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
        return await message.reply("Invite Link Generation Failed, Iam Not Having Sufficient Rights")
    except Exception as e:
        return await message.reply(f'Error {e}')
    await message.reply(f'Here is your Invite Link {link.invite_link}')

@app.on_message(filters.command(["adminlist","adminlist@MissKatyRoBot"], COMMAND_HANDLER))
async def adminlist(_, message):
    if message.chat.type == 'private':
        return await message.reply("Perintah ini hanya untuk grup")
    try:
        mem = await app.get_chat_members(message.chat.id, filter="administrators")
        res = "".join(f"~ <a href='tg://user?id={i['user']['id']}'>{i['user']['first_name']}</a>\n" for i in mem)
        return await message.reply(f"<b>Daftar Admin di {message.chat.title}:</b>\n{res}")
    except Exception as e:
        await message.reply(f"ERROR: {str(e)}")

@app.on_message(filters.command(["zombies","zombies@MissKatyRoBot"], COMMAND_HANDLER))
async def zombie_clean(_, message):
    
    zombie = 0
    wait = await message.reply_text("Searching ... and banning ...")
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
        f"<b>{zombie}</b> Zombies ditemukan dan telah banned!",
    )

@Client.on_message(filters.command(["kickme","kickme@MissKatyRoBot"], COMMAND_HANDLER))
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
        await message.reply_text(f"Sepertinya ada error, silahkan report ke owner saya. \nERROR: {str(ef)}")
    return

@Client.on_message(filters.command(['dban','dban@MissKatyRoBot'], COMMAND_HANDLER) & filters.group)
async def ban_a_user(bot, message):
    admin = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if admin.status not in ['administrator','creator']:
        await message.reply_text("Kamu bukan admin disini")
        await message.stop_propagation()

    if len(message.text.split()) == 1 and not message.reply_to_message:
        await message.reply_text("Gunakan command ini dengan reply atau mention user")
        await message.stop_propagation()

    if not message.reply_to_message:
        return await message.reply_text(
            "Balas ke pesan untuk delete dan ban pengguna!")

    if message.reply_to_message and not message.reply_to_message.from_user:
        user_id, user_first_name = (
            message.reply_to_message.sender_chat.id,
            message.reply_to_message.sender_chat.title,
        )
    else:
        user_id, user_first_name = (
            message.reply_to_message.from_user.id,
            message.reply_to_message.from_user.first_name,
        )

    if not user_id:
        await message.reply_text("Aku tidak bisa menemukan pengguna untuk diban")
        return
    if user_id == message.chat.id:
        await message.reply_text("Itu adalah hal gila jika saya ban admin!")
        await message.stop_propagation()
    if user_id == 1507530289:
        await message.reply_text("Hah, saya harus ban diriku sendiri?")
        await message.stop_propagation()

    admin = await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    if user_id in ['administrator','creator']:
        await message.reply_text("Saya tidak bisa ban admin")
        await message.stop_propagation()

    reason = None
    if len(message.text.split()) >= 2:
        reason = message.text.split(None, 1)[1]

    try:
        await message.reply_to_message.delete()
        await message.chat.kick_member(user_id)
        txt = ("{} banned {} di <b>{}</b>!").format(
            message.from_user.mention,
            message.reply_to_message.from_user.mention,
            message.chat.title,
        )
        txt += f"\n<b>Alasan</b>: {reason}" if reason else ""
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "⚠️ Unban (Hanya Admin)",
                callback_data=f"unban_={user_id}",
            ),
        ]])
        await bot.send_message(message.chat.id, txt, reply_markup=keyboard)
    except ChatAdminRequired:
        await message.reply_text("Sepertinya aku bukan admin disini.")
    except PeerIdInvalid:
        await message.reply_text(
            "Aku belum pernah melihat pengguna ini sebelumnya...!\nMungkin bisa dengan forward pesan dia?",
        )
    except UserAdminInvalid:
        await message.reply_text("Tidak dapat bertindak atas pengguna ini, mungkin bukan saya yang mengubah izinnya")
    except RightForbidden:
        await message.reply_text("Aku tidak punya ijin untuk membanned pengguna ini")
    except RPCError as ef:
        await message.reply_text(f"Sepertinya ada yg salah, silahkan lapor ke owner saya.\nERROR: {str(ef)}")
                                 
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
    doneto = whoo.title if whoo.title else whoo.first_name
    ids = whoo.id
    try:
        await q.message.chat.unban_member(user_id)
    except RPCError as e:
        await q.message.edit_text(f"Error: {e}")
        return
    await q.message.edit_text(f"{q.from_user.mention} unbanned <a href='tg://user?id={ids}'>{doneto}</a>!")
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
        return await message.reply("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply("Thismight be a channel, make sure its a user.")
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
