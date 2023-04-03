import asyncio
import io
import os
import re
import sys
import pickle
import traceback
from shutil import disk_usage
from time import time
from inspect import getfullargspec

from psutil import cpu_percent
from psutil import disk_usage as disk_usage_percent
from psutil import virtual_memory

from pyrogram import enums, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from misskaty import app, user, botStartTime, BOT_NAME
from misskaty.helper.localization import use_chat_lang
from misskaty.helper.human_read import get_readable_file_size, get_readable_time
from misskaty.core.message_utils import editPesan, hapusPesan, kirimPesan
from misskaty.vars import COMMAND_HANDLER, SUDO

__MODULE__ = "DevCommand"
__HELP__ = """
**For Owner Bot Only.**
/run [args] - Run eval CMD
/shell [args] - Run Exec/Terminal CMD
/download [link/reply_to_telegram_file] - Download file from Telegram

**For Public Use**
/json - Send structure message Telegram in JSON using Pyrogram Style.
"""


async def edit_or_reply(msg, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    await func(**{k: v for k, v in kwargs.items() if k in spec})


@app.on_message(filters.command(["logs"], COMMAND_HANDLER) & filters.user(SUDO))
@use_chat_lang()
async def log_file(bot, message, strings):
    """Send log file"""
    try:
        await message.reply_document(
            "MissKatyLogs.txt",
            caption="Log Bot MissKatyPyro",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            strings("cl_btn"),
                            f"close#{message.from_user.id}",
                        )
                    ]
                ]
            ),
        )
    except:
        err = traceback.format_exc()
        await message.reply(str(err))


@app.on_message(filters.command(["donate"], COMMAND_HANDLER))
async def donate(_, message):
    await message.reply_photo(
        "https://telegra.ph/file/2acf7698f300ef3d9138f.jpg",
        caption=f"Hai {message.from_user.mention}, jika kamu merasa bot ini berguna bisa melakukan donasi dengan scan kode QRIS diatas yaa. Terimakasih..",
    )


@app.on_message(filters.command(["balas"], COMMAND_HANDLER) & filters.user(SUDO) & filters.reply)
async def balas(c, m):
    pesan = m.text.split(" ", 1)
    await hapusPesan(m)
    await m.reply(pesan[1], reply_to_message_id=m.reply_to_message.id)


@app.on_message(filters.command(["stats"], COMMAND_HANDLER))
async def server_stats(c, m):
    """
    Give system stats of the server.
    """
    currentTime = get_readable_time(time() - botStartTime)
    total, used, free = disk_usage(".")
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    neofetch = (await shell_exec("neofetch --stdout"))[0]
    caption = f"""
**{BOT_NAME} is Up and Running successfully.**
Bot Uptime: `{currentTime}`
Total Disk Space: `{total}`
Used: `{used}({disk_usage_percent("/").percent}%)`
Free: `{free}`
CPU Usage: `{cpu_percent()}%`
RAM Usage: `{virtual_memory().percent}%`

`{neofetch}`
"""
    await kirimPesan(m, caption)


@app.on_message(filters.command(["shell", "sh"], COMMAND_HANDLER) & filters.user(SUDO))
@app.on_edited_message(filters.command(["shell", "sh"], COMMAND_HANDLER) & filters.user(SUDO))
@user.on_message(filters.command(["shell", "sh"], ".") & filters.me)
@use_chat_lang()
async def shell(_, m, strings):
    cmd = m.text.split(" ", 1)
    if len(m.command) == 1:
        return await edit_or_reply(m, text=strings("no_cmd"))
    msg = await editPesan(m, strings("run_exec")) if m.from_user.is_self else await kirimPesan(m, strings("run_exec"))
    shell = (await shell_exec(cmd[1]))[0]
    if len(shell) > 3000:
        with open("shell_output.txt", "w") as file:
            file.write(shell)
        with open("shell_output.txt", "rb") as doc:
            await m.reply_document(
                document=doc,
                file_name=doc.name,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=strings("cl_btn"), callback_data=f"close#{m.from_user.id}")]]),
            )
            await msg.delete()
            try:
                os.remove("shell_output.txt")
            except:
                pass
    elif len(shell) != 0:
        await edit_or_reply(
            m,
            text=shell,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=strings("cl_btn"), callback_data=f"close#{m.from_user.id}")]]),
        )
        if not m.from_user.is_self:
            await msg.delete()
    else:
        await m.reply(strings("no_reply"))


@app.on_message((filters.command(["ev", "run"], COMMAND_HANDLER) | filters.regex(r"app.run\(\)$")) & filters.user(SUDO))
@app.on_edited_message((filters.command(["ev", "run"]) | filters.regex(r"app.run\(\)$")) & filters.user(SUDO))
@user.on_message(filters.command(["ev", "run"], ".") & filters.me)
@use_chat_lang()
async def evaluation_cmd_t(_, m, strings):
    if (m.command and len(m.command) == 1) or m.text == "app.run()":
        return await edit_or_reply(m, text=strings("no_eval"))
    cmd = m.text.split(" ", 1)[1] if m.command else m.text.split("\napp.run()")[0]
    status_message = await editPesan(m, strings("run_eval")) if m.from_user.is_self else await kirimPesan(m, strings("run_eval"), quote=True)

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, _, m)
    except NameError as e:
        trace_output = "❌ MISSING VARIABEL:\n"
        trace_output += f"{e}"
        exc = trace_output
    except AttributeError as e:
        trace_output = "❌ MISSING ATTRIBUTE:\n"
        trace_output += f"{e}"
        exc = trace_output
    except SyntaxError:
        trace = traceback.format_exc()
        splitted = str(trace).split("\n")
        end_split = len(splitted)
        row_1 = splitted[end_split - 4]
        row_2 = splitted[end_split - 3]
        row_3 = splitted[end_split - 2]
        compiles = row_1 + "\n" + row_2 + "\n" + row_3
        trace_output = "⚙️ SYNTAX ERROR:\n"
        trace_output += f"{compiles}"
        exc = trace_output
    except ValueError as e:
        trace_output = "🧮 VALUE ERROR:\n"
        trace_output += f"{e}"
        exc = trace_output
    except Exception as e:
        # trace = traceback.format_exc()
        """Periksa apakah error regexnya tertangkap"""
        match = re.search(r"Telegram says: .+", str(e))
        trace_output = "⚠️ COMMON ERROR:\n"
        trace_output += f"{e}"
        if match:
            trace_output = f"👀 {match[0]}"
        exc = trace_output

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = strings("success")

    final_output = f"<b>EVAL</b>:\n<pre language='python'>{cmd}</pre>\n\n<b>OUTPUT</b>:\n<pre language='python'>{evaluation.strip()}</pre>\n"

    if len(final_output) > 4096:
        with open("MissKatyEval.txt", "w+", encoding="utf8") as out_file:
            out_file.write(final_output)
        await m.reply_document(
            document="MissKatyEval.txt",
            caption=f"<code>{cmd[1][: 4096 // 4 - 1]}</code>",
            disable_notification=True,
            thumb="assets/thumb.jpg",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=strings("cl_btn"), callback_data=f"close#{m.from_user.id}")]]),
        )
        os.remove("MissKatyEval.txt")
        await status_message.delete()
    else:
        await edit_or_reply(
            m,
            text=final_output,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=strings("cl_btn"), callback_data=f"close#{m.from_user.id}")]]),
        )
        if not m.from_user.is_self:
            await status_message.delete()


# Update and restart bot
@app.on_message(filters.command(["update"], COMMAND_HANDLER) & filters.user(SUDO))
@use_chat_lang()
async def update_restart(_, message, strings):
    try:
        out = (await shell_exec("git pull"))[0]
        if "Already up to date." in str(out):
            return await message.reply_text(strings("already_up"))
        await message.reply_text(f"<code>{out}</code>")
    except Exception as e:
        return await message.reply_text(str(e))
    msg = await message.reply_text(strings("up_and_rest"))
    with open("restart.pickle", "wb") as status:
        pickle.dump([message.chat.id, msg.id], status)
    os.execvp(sys.executable, [sys.executable, "-m", "misskaty"])


async def aexec(code, c, m):
    exec("async def __aexec(c, m): " + "\n p = print" + "\n replied = m.reply_to_message" + "".join(f"\n {l_}" for l_ in code.split("\n")))
    return await locals()["__aexec"](c, m)


async def shell_exec(code, treat=True):
    process = await asyncio.create_subprocess_shell(code, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)

    stdout = (await process.communicate())[0]
    if treat:
        stdout = stdout.decode().strip()
    return stdout, process
