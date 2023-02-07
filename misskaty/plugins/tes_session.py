# This plugin to learn session using pyrogram
from pyrogram import filters

from misskaty import app
from misskaty.vars import COMMAND_HANDLER


@app.on_message(filters.command(["session"], COMMAND_HANDLER))
async def session(_, message):
    if not message.from_user: return
    nama = await message.chat.ask("Ketik nama kamu:")
    umur = await message.chat.ask("Ketik umur kamu")
    alamat = await message.chat.ask("Ketik alamat kamu:")
    await app.send_message(
        message.chat.id,
        f"Nama Kamu Adalah: {nama.text}\nUmur Kamu Adalah: {umur.text}\nAlamat Kamu Adalah: {alamat.text}",
    )
