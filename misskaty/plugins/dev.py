import asyncio
import io
import os
import sys
import traceback
from inspect import getfullargspec

from pyrogram import enums, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from misskaty import app, user
from misskaty.core.message_utils import editPesan, kirimPesan
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
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document(
            "MissKatyLogs.txt",
            caption="Log Bot MissKatyPyro",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="❌ Close",
                            callback_data=f"close#{message.from_user.id}",
                        )
                    ]
                ]
            ),
        )
    except Exception as e:
        await message.reply(str(e))


@app.on_message(filters.command(["donate"], COMMAND_HANDLER))
async def donate(_, message):
    await message.reply_photo(
        "AgACAgQAAxkBAAECsVNjbMvjxbN4gRafvNBH-Kv-Zqml8wACzq4xG95tbVPDeZ_UusonbAAIAQADAgADeQAHHgQ",
        caption=f"Hai {message.from_user.mention}, jika kamu merasa bot ini berguna bisa melakukan donasi dengan scan kode QRIS diatas untuk kebutuhan server dan lainnya. Terimakasih..",
    )


@app.on_message(filters.command(["balas"], COMMAND_HANDLER) & filters.user(SUDO) & filters.reply)
async def balas(c, m):
    pesan = m.text.split(" ", 1)
    await m.delete()
    await m.reply(pesan[1], reply_to_message_id=m.reply_to_message.id)


@app.on_message(filters.command(["neofetch"], COMMAND_HANDLER) & filters.user(SUDO))
async def neofetch(c, m):
    neofetch = (await shell_exec("neofetch --stdout"))[0]
    await m.reply(f"<code>{neofetch}</code>")


@app.on_message(filters.command(["shell", "sh"], COMMAND_HANDLER) & filters.user(SUDO))
@app.on_edited_message(filters.command(["shell", "sh"], COMMAND_HANDLER) & filters.user(SUDO))
@user.on_message(filters.command(["shell", "sh"], ".") & filters.me)
async def shell(_, m):
    cmd = m.text.split(" ", 1)
    if len(m.command) == 1:
        return await edit_or_reply(m, text="No command to execute was given.")
    msg = await editPesan(m, "<i>Processing exec pyrogram...</i>") if m.from_user.is_self else await kirimPesan(m, "<i>Processing exec pyrogram...</i>")
    shell = (await shell_exec(cmd[1]))[0]
    if len(shell) > 3000:
        with open("shell_output.txt", "w") as file:
            file.write(shell)
        with open("shell_output.txt", "rb") as doc:
            await m.reply_document(
                document=doc,
                file_name=doc.name,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="❌ Close", callback_data=f"close#{m.from_user.id}")]]),
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
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="❌ Close", callback_data=f"close#{m.from_user.id}")]]),
        )
    else:
        await m.reply("No Reply")


@app.on_message(filters.command(["ev", "run"], COMMAND_HANDLER) & filters.user(SUDO))
@app.on_edited_message(filters.command(["ev", "run"]) & filters.user(SUDO))
@user.on_message(filters.command(["ev", "run"], ".") & filters.me)
async def evaluation_cmd_t(_, m):
    cmd = m.text.split(" ", 1)
    if len(m.command) == 1:
        return await edit_or_reply(m, text="__No evaluate message!__")
    status_message = await editPesan(m, "<i>Processing eval pyrogram..</i>") if m.from_user.is_self else await kirimPesan(m, "<i>Processing eval pyrogram..</i>")

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd[1], _, m)
    except Exception:
        exc = traceback.format_exc()

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
        evaluation = "Success"

    final_output = f"**EVAL**:\n`{cmd[1]}`\n\n**OUTPUT**:\n`{evaluation.strip()}`\n"

    if len(final_output) > 4096:
        with open("MissKatyEval.txt", "w+", encoding="utf8") as out_file:
            out_file.write(final_output)
        await m.reply_document(
            document="MissKatyEval.txt",
            caption=f"<code>{cmd[1][: 4096 // 4 - 1]}</code>",
            disable_notification=True,
            thumb="img/thumb.jpg",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="❌ Close", callback_data=f"close#{m.from_user.id}")]]),
        )
        os.remove("MissKatyEval.txt")
        await status_message.delete()
    else:
        await edit_or_reply(
            m,
            text=final_output,
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="❌ Close", callback_data=f"close#{m.from_user.id}")]]),
        )

# Update and restart bot
@app.on_message(filters.command(["update"], COMMAND_HANDLER) & filters.user(SUDO))
async def update_restart(_, message):
    try:
        out = (await shell_exec("git pull"))[0]
        if "Already up to date." in str(out):
            return await message.reply_text("Its already up-to date!")
        await message.reply_text(f"<code>{out}</code>")
    except Exception as e:
        return await message.reply_text(str(e))
    await message.reply_text(
        "<b>Updated with default branch, restarting now.</b>"
    )
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
