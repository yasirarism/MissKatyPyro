import textwrap
import random
from asyncio import gather
from os import remove as hapus

import regex
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram import types as pyro_types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import MessageIdInvalid, PeerIdInvalid, ReactionInvalid, ListenerTimeout

from misskaty import app, user
from misskaty.core.decorator.errors import capture_err
from misskaty.helper import use_chat_lang, fetch
from misskaty.vars import COMMAND_HANDLER, SUDO, OWNER_ID


__MODULE__ = "Fun"
__HELP__ = """
/q [int] - Generate quotly from message
/memify [text] - Reply to sticker to give text on sticker.
/react [emoji | list of emoji] - React to any message (Sudo and Owner only)
/beri [pesan] - Giving false hope to someone hehehe
/dice - Randomly roll the dice
/tebakgambar - Play "Tebak Gambar" in any room chat
/tebaklontong - Play "Tebak Lontong" in any room chat
/tebakkata - Play "Tebak Kata" in any room chat
/tebaktebakan - Play "Tebak Tebakan" in any room chat
/batu - Main batu gunting kertas pakai tombol
/tebakangka - Tebak angka 1-20 pakai callback button
"""

async def draw_meme_text(image_path, text):
    img = Image.open(image_path)
    hapus(image_path)
    i_width, i_height = img.size
    m_font = ImageFont.truetype(
        "assets/MutantAcademyStyle.ttf", int((70 / 640) * i_width)
    )
    if ";" in text:
        upper_text, lower_text = text.split(";")
    else:
        upper_text = text
        lower_text = ""
    draw = ImageDraw.Draw(img)
    current_h, pad = 10, 5
    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            text_bbox = m_font.getbbox(u_text)
            (left, top, right, bottom) = text_bbox
            u_width = abs(right - left)
            u_height = abs(top - bottom)

            draw.text(
                xy=(((i_width - u_width) / 2) - 1, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
                stroke_width=3,
                stroke_fill="black",
            )
            draw.text(
                xy=(((i_width - u_width) / 2) + 1, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
                stroke_width=3,
                stroke_fill="black",
            )
            draw.text(
                xy=((i_width - u_width) / 2, int(((current_h / 640) * i_width)) - 1),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
                stroke_width=3,
                stroke_fill="black",
            )
            draw.text(
                xy=(((i_width - u_width) / 2), int(((current_h / 640) * i_width)) + 1),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
                stroke_width=3,
                stroke_fill="black",
            )

            draw.text(
                xy=((i_width - u_width) / 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(255, 255, 255),
            )
            current_h += u_height + pad
    if lower_text:
        for l_text in textwrap.wrap(lower_text, width=15):
            text_bbox = m_font.getbbox(l_text)
            (left, top, right, bottom) = text_bbox
            u_width = abs(right - left)
            u_height = abs(top - bottom)

            draw.text(
                xy=(
                    ((i_width - u_width) / 2) - 1,
                    i_height - u_height - int((20 / 500) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
                stroke_width=3,
                stroke_fill="black",
            )
            draw.text(
                xy=(
                    ((i_width - u_width) / 2) + 1,
                    i_height - u_height - int((20 / 500) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
                stroke_width=3,
                stroke_fill="black",
            )
            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((20 / 500) * i_width)) - 1,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
                stroke_width=3,
                stroke_fill="black",
            )
            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((20 / 500) * i_width)) + 1,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
                stroke_width=3,
                stroke_fill="black",
            )

            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    i_height - u_height - int((20 / 500) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(255, 255, 255),
                stroke_width=3,
                stroke_fill="black",
            )
            current_h += u_height + pad

    webp_file = "misskatyfy.webp"
    png_file = "misskatyfy.png"
    new_size = (512, 512)
    img.resize(new_size)
    img.save(webp_file, "WebP")
    img.save(png_file, "PNG")
    img.close()
    return webp_file, png_file


@app.on_message(filters.command(["mmf"], COMMAND_HANDLER))
@capture_err
async def memify(_, message):
    if message.reply_to_message and (
        message.reply_to_message.sticker or message.reply_to_message.photo
    ):
        try:
            file = await message.reply_to_message.download()
            webp, png = await draw_meme_text(
                file, message.text.split(None, 1)[1].strip()
            )
            await gather(*[message.reply_document(png), message.reply_sticker(webp)])
            try:
                hapus(webp)
                hapus(png)
            except Exception:
                pass
        except Exception as err:
            try:
                hapus(webp)
                hapus(png)
            except Exception:
                pass
            await message.reply(f"ERROR: {err}")
    else:
        await message.reply(
            "Gunakan command <b>/mmf <text></b> dengan reply ke sticker, pisahkan dengan ; untuk membuat posisi text dibawah."
        )


@app.on_message(filters.command(["dice"], COMMAND_HANDLER))
@use_chat_lang()
async def dice(c, m, strings):
    dices = await c.send_dice(m.chat.id, reply_parameters=pyro_types.ReplyParameters(message_id=m.id))
    await dices.reply(strings("result").format(number=dices.dice.value))


@app.on_message(filters.command(["beri"], COMMAND_HANDLER))
async def beriharapan(c, m):
    reply = m.reply_to_message
    if not reply and m.command == 1:
        return m.reply("Harap berikan kalimat yang ingin diberi pada seseorang")
    pesan = m.text.split(maxsplit=1)[1]
    reply_name = reply.from_user.mention if reply.from_user else reply.sender_chat.title
    sender_name = m.from_user.mention if m.from_user else m.sender_chat.title
    await reply.reply(f"{sender_name} memberikan {pesan} pada {reply_name}")


@app.on_message(filters.command("react", COMMAND_HANDLER) & (filters.user(SUDO) | filters.user(OWNER_ID)))
@user.on_message(filters.command("react", "."))
async def givereact(c, m):
    if len(m.command) == 1:
        return await m.reply(
            "Please add reaction after command, you can give multiple reaction too."
        )
    if not m.reply_to_message:
        return await m.reply("Please reply to the message you want to react to.")
    emot = list(regex.findall(r"\p{Emoji}", m.text))
    try:
        await m.reply_to_message.react(emoji=emot)
    except ReactionInvalid:
        await m.reply("Please give valid reaction.")
    except MessageIdInvalid:
        await m.reply(
            "Sorry, i couldn't react to other bots or without being as administrator."
        )
    except PeerIdInvalid:
        await m.reply("Sorry, i can't react chat without join that groups.")
    except Exception as err:
        await m.reply(str(err))

game_status = {}

# Dictionary untuk memetakan perintah ke API dan parameter terkait
game_modes = {
    "tebakgambar": {
        "url": "https://yasirapi.eu.org/tebakgambar",
        "type": "image",
        "response_key": "img",
        "answer_key": "jawaban"
    },
    "tebaklontong": {
        "url": "https://yasirapi.eu.org/tebaklontong",
        "type": "text",
        "response_key": "soal",
        "answer_key": "jawaban",
        "description_key": "deskripsi"
    },
    "tebakkata": {
        "url": "https://yasirapi.eu.org/tebakkata",
        "type": "text",
        "response_key": "soal",
        "answer_key": "jawaban"
    },
    "tebaktebakan": {
        "url": "https://yasirapi.eu.org/tebaktebakan",
        "type": "text",
        "response_key": "soal",
        "answer_key": "jawaban"
    }
}

# Fungsi utama untuk semua permainan
async def play_game(client, message, game_mode):
    mode_data = game_modes[game_mode]
    # Fetch data dari API
    getdata = await fetch.get(mode_data["url"])
    if getdata.status_code != 200:
        return await message.reply_text(f"Gagal mendapatkan data dari {game_mode}.")

    result = getdata.json()
    correct_answer = result[mode_data["answer_key"]]

    game_status[message.chat.id] = {'correct_answer': correct_answer, 'active': True}

    # Kirim soal atau gambar berdasarkan mode
    if mode_data["type"] == "image":
        image_url = result[mode_data["response_key"]]
        await message.reply_photo(photo=image_url, caption="Tebak gambar ini! Kamu punya 45 detik untuk menjawab. Kirim /next untuk lanjut ke soal berikutnya atau /stopgame untuk berhenti.")
    else:
        soal = result[mode_data["response_key"]]
        await message.reply_text(f"{soal}\n\nKamu punya 45 detik untuk menjawab. Kirim /next untuk lanjut ke soal berikutnya atau /stopgame untuk berhenti.")

    # Handle jawaban
    while True:
        try:
            response = await client.listen(chat_id=message.chat.id, filters=filters.text, timeout=45)

            if response.text.lower() in ["/next", f"/next@{client.me.username.lower()}"]:
                await message.reply_text("Lanjut ke soal berikutnya!")
                game_status[message.chat.id]['active'] = False
                return await play_game(client, message, game_mode)  # Kirim soal berikutnya

            if response.text.lower() in ["/stopgame", f"/stopgame@{client.me.username.lower()}"]:
                await message.reply_text("Permainan dihentikan.")
                game_status[message.chat.id]['active'] = False
                break

            if response.text.lower() == correct_answer.lower():
                reply_message = f"Selamat! Jawaban kamu benar: <b>{correct_answer.upper()}</b>"

                # Jika ada deskripsi tambahan untuk tebak lontong
                if "description_key" in mode_data and mode_data["description_key"] in result:
                    deskripsi = result[mode_data["description_key"]]
                    reply_message += f"\nAlasan: {deskripsi}"

                await response.reply_text(reply_message)
                game_status[message.chat.id]['active'] = False
                break        
        except ListenerTimeout:
            reply_message = f"Waktu habis! Jawaban yang benar adalah: <b>{correct_answer.upper()}</b>"
            # Tambahkan deskripsi jika ada (untuk tebak lontong)
            if "description_key" in mode_data and mode_data["description_key"] in result:
                deskripsi = result[mode_data["description_key"]]
                reply_message += f"\nAlasan: {deskripsi}"
            await message.reply_text(reply_message)
            game_status[message.chat.id]['active'] = False
            break

# Handler untuk semua perintah permainan
@app.on_message(filters.command(["tebakgambar", "tebaklontong", "tebakkata", "tebaktebakan"]))
async def handle_game_command(client, message):
    await play_game(client, message, message.command[0])


def generate_game_id():
    return f"{random.randint(100000, 999999)}{random.randint(100, 999)}"


def build_tebak_angka_keyboard(game_id):
    rows = []
    buttons = []
    for nomor in range(1, 21):
        buttons.append(InlineKeyboardButton(str(nomor), callback_data=f"ga:{game_id}:{nomor}"))
        if len(buttons) == 5:
            rows.append(buttons)
            buttons = []
    rows.append([InlineKeyboardButton("🛑 Berhenti", callback_data=f"ga:{game_id}:stop")])
    return InlineKeyboardMarkup(rows)


@app.on_message(filters.command(["batu", "suit", "rps"], COMMAND_HANDLER))
async def batu_gunting_kertas(_, message):
    if not message.from_user:
        return await message.reply_text("Game ini hanya bisa dimulai oleh akun user.")

    game_id = generate_game_id()
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🪨 Batu", callback_data=f"rps:{game_id}:batu"),
                InlineKeyboardButton("✂️ Gunting", callback_data=f"rps:{game_id}:gunting"),
                InlineKeyboardButton("📄 Kertas", callback_data=f"rps:{game_id}:kertas"),
            ],
            [InlineKeyboardButton("❌ Batalkan", callback_data=f"rps:{game_id}:stop")],
        ]
    )

    msg = await message.reply_text(
        "🎮 <b>Batu Gunting Kertas</b>\n"
        f"Pemain: {message.from_user.mention}\n"
        "Klik salah satu tombol di bawah untuk memilih.",
        reply_markup=keyboard,
    )

    try:
        click = await msg.wait_for_click(
            from_user_id=message.from_user.id,
            timeout=45,
        )
    except ListenerTimeout:
        return await msg.edit_text("⌛ Waktu habis, game Batu Gunting Kertas kedaluwarsa.")

    pilihan_user = click.data.split(":", 2)[2]
    if pilihan_user == "stop":
        await click.answer("Game dibatalkan.")
        return await msg.edit_text("Game Batu Gunting Kertas dibatalkan.")

    pilihan_valid = {
        "batu": "🪨 Batu",
        "gunting": "✂️ Gunting",
        "kertas": "📄 Kertas",
    }
    aturan_menang = {
        "batu": "gunting",
        "gunting": "kertas",
        "kertas": "batu",
    }

    pilihan_bot = random.choice(list(pilihan_valid.keys()))
    if pilihan_user == pilihan_bot:
        hasil = "🤝 Seri!"
    elif aturan_menang[pilihan_user] == pilihan_bot:
        hasil = "🎉 Kamu menang!"
    else:
        hasil = "😼 Bot menang!"

    await click.answer("Pilihan diterima!")
    await msg.edit_text(
        "🎮 <b>Hasil Batu Gunting Kertas</b>\n"
        f"Pemain: {message.from_user.mention}\n"
        f"Pilihan kamu: {pilihan_valid[pilihan_user]}\n"
        f"Pilihan bot: {pilihan_valid[pilihan_bot]}\n\n{hasil}"
    )


@app.on_message(filters.command(["tebakangka", "guessnumber"], COMMAND_HANDLER))
async def tebak_angka(_, message):
    if not message.from_user:
        return await message.reply_text("Game ini hanya bisa dimulai oleh akun user.")

    game_id = generate_game_id()
    angka_rahasia = random.randint(1, 20)
    percobaan_maks = 5
    percobaan = 0

    msg = await message.reply_text(
        "🎯 <b>Game Tebak Angka</b>\n"
        f"Pemain: {message.from_user.mention}\n"
        "Aku sudah memilih angka dari <b>1 sampai 20</b>.\n"
        "Klik angka pada tombol di bawah.\n"
        "Maksimal <b>5 percobaan</b>.",
        reply_markup=build_tebak_angka_keyboard(game_id),
    )

    while percobaan < percobaan_maks:
        try:
            click = await msg.wait_for_click(
                from_user_id=message.from_user.id,
                timeout=45,
            )
        except ListenerTimeout:
            return await msg.edit_text(
                f"⌛ Waktu habis! Angka yang benar adalah <b>{angka_rahasia}</b>."
            )

        pilihan = click.data.split(":", 2)[2]
        if pilihan == "stop":
            await click.answer("Game dihentikan.")
            return await msg.edit_text("🛑 Game Tebak Angka dibatalkan.")

        tebakan = int(pilihan)
        percobaan += 1

        if tebakan == angka_rahasia:
            await click.answer("Jawaban benar!", show_alert=True)
            return await msg.edit_text(
                "🏆 <b>Selamat!</b>\n"
                f"{message.from_user.mention} berhasil menebak angka <b>{angka_rahasia}</b> "
                f"dalam <b>{percobaan}</b> percobaan."
            )

        sisa = percobaan_maks - percobaan
        petunjuk = "terlalu kecil" if tebakan < angka_rahasia else "terlalu besar"

        if sisa <= 0:
            await click.answer("Percobaan habis.", show_alert=True)
            return await msg.edit_text(
                "💥 <b>Game selesai!</b>\n"
                f"Percobaan habis. Angka yang benar adalah <b>{angka_rahasia}</b>."
            )

        await click.answer(f"Tebakan {petunjuk}. Sisa {sisa} percobaan.", show_alert=True)
        await msg.edit_text(
            "🎯 <b>Game Tebak Angka</b>\n"
            f"Pemain: {message.from_user.mention}\n"
            f"Percobaan dipakai: <b>{percobaan}</b>/<b>{percobaan_maks}</b>\n"
            f"Hint terakhir: <b>{tebakan}</b> itu {petunjuk}.\n"
            "Pilih angka lagi dari tombol di bawah.",
            reply_markup=build_tebak_angka_keyboard(game_id),
        )
