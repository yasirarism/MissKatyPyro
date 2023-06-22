# This plugin to learn session using pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message

from misskaty import app
from misskaty.vars import COMMAND_HANDLER


@app.on_message(filters.command(["session"], COMMAND_HANDLER))
async def session(self: Client, ctx: Message):
    if not ctx.from_user:
        return
    nama = await ctx.chat.ask("Ketik nama kamu:")
    umur = await ctx.chat.ask("Ketik umur kamu")
    alamat = await ctx.chat.ask("Ketik alamat kamu:")
    await app.send_msg(
        ctx.chat.id,
        f"Nama Kamu Adalah: {nama.text}\nUmur Kamu Adalah: {umur.text}\nAlamat Kamu Adalah: {alamat.text}",
    )
