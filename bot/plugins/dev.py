"""Evaluate Python Code inside Telegram
Syntax: .eval PythonCode"""
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import io
import sys
import os
import traceback
import asyncio
from pyrogram import filters, enums
from info import COMMAND_HANDLER
from bot import app, user
from subprocess import run as srun

@app.on_message(
    filters.command(["balas"], COMMAND_HANDLER)
    & filters.user([617426792, 2024984460]) & filters.reply)
async def balas(c, m):
    pesan = m.text.split(' ', 1)
    await m.delete()
    await m.reply(pesan[1], reply_to_message_id=m.reply_to_message.id)

@app.on_message(filters.command(["neofetch"], COMMAND_HANDLER) & filters.user(617426792))
async def neofetch(c, m):
    neofetch = (await shell_exec("neofetch --stdout"))[0]
    await m.reply(f"<code>{neofetch}</code>", parse_mode=enums.ParseMode.HTML)

@app.on_message(filters.command(["remove"], COMMAND_HANDLER))
async def clearlocal(c, m):
    cmd = m.text.split(' ', 1)
    if len(cmd) == 1:
        return await m.reply('Give path file to delete.')
    remove = (await shell_exec(f"rm -rf {cmd[1]}"))[0]
    await m.reply("Done")

@app.on_message(
    filters.command(["shell", "shell@MissKatyRoBot"], COMMAND_HANDLER)
    & filters.user([617426792, 2024984460]))
@app.on_edited_message(
    filters.command(["shell", "shell@MissKatyRoBot"], COMMAND_HANDLER)
    & filters.user([617426792, 2024984460]))
async def shell(client, message):
    cmd = message.text.split(' ', 1)
    if len(cmd) == 1:
        return await message.reply('No command to execute was given.')
    shell = (await shell_exec(cmd[1]))[0]
    if len(shell) > 3000:
        with open('shell_output.txt', 'w') as file:
            file.write(shell)
        with open('shell_output.txt', 'rb') as doc:
            await message.reply_document(document=doc, file_name=doc.name)
            try:
                os.remove('shell_output.txt')
            except:
                pass
    elif len(shell) != 0:
        await message.reply(shell, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply('No Reply')


@app.on_message(
    filters.command(["run", "run@MissKatyRoBot"], COMMAND_HANDLER)
    & filters.user([617426792, 2024984460]))
@app.on_edited_message(
    filters.command(["run", "run@MissKatyRoBot"], COMMAND_HANDLER)
    & filters.user([617426792, 2024984460]))
async def eval(client, message):
    if len(message.command) < 2:
        return await message.reply("Masukkan kode yang ingin dijalankan..")
    status_message = await message.reply_text("Sedang Memproses Eval...")
    cmd = message.text.split(" ", maxsplit=1)[1]

    reply_to_ = message
    if message.reply_to_message:
        reply_to_ = message.reply_to_message

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, client, message)
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
        evaluation = "Berhasil"

    final_output = "**EVAL**: "
    final_output += f"```{cmd}```\n\n"
    final_output += "**OUTPUT***:\n"
    final_output += f"```{evaluation.strip()}```\n"

    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "MissKaty_Eval.txt"
            await reply_to_.reply_document(
                document=out_file,
                caption=cmd[:4096 // 4 - 1],
                disable_notification=True,
                quote=True
            )
            try:
                os.remove("MissKaty_Eval.txt")
            except:
                pass
    else:
        await reply_to_.reply_text(final_output, quote=True, parse_mode=enums.ParseMode.MARKDOWN)
    await status_message.delete()


async def aexec(code, client, message):
    exec("async def __aexec(client, message): " +
         "".join(f"\n {l_}" for l_ in code.split("\n")))
    return await locals()["__aexec"](client, message)


async def shell_exec(code, treat=True):
    process = await asyncio.create_subprocess_shell(
        code, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)

    stdout = (await process.communicate())[0]
    if treat:
        stdout = stdout.decode().strip()
    return stdout, process
