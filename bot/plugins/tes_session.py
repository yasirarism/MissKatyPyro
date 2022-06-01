from bot import app
from info import COMMAND_HANDLER
from pyrogram import filters


@app.on_message(filters.command(["session"], COMMAND_HANDLER))
async def session(_, message):
    nama = await app.ask(message.chat.id, 'Ketik nama kamu:')
    umur = await app.ask(message.chat.id, 'Ketik umur kamu')
    alamat = await app.ask(message.chat.id, 'Ketik alamat kamu:')
    await app.send_message(
        message.chat.id,
        f'Nama Kamu Adalah: {nama.text}\nUmur Kamu Adalah: {umur.text}\nAlamat Kamu Adalah: {alamat.text}'
    )
