# This plugin to learn session using pyrogram
from pyrogram.types import Message

from misskaty import app


@app.on_cmd("session")
async def session(_, ctx: Message):
    nama = await ctx.chat.ask("Ketik nama kamu:")
    umur = await ctx.chat.ask("Ketik umur kamu")
    alamat = await ctx.chat.ask("Ketik alamat kamu:")
    await app.send_msg(
        ctx.chat.id,
        f"Nama Kamu Adalah: {nama.text}\nUmur Kamu Adalah: {umur.text}\nAlamat Kamu Adalah: {alamat.text}",
    )
