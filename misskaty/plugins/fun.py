import textwrap
from asyncio import gather
from os import remove as hapus

import regex
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
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
            except:
                pass
        except Exception as err:
            try:
                hapus(webp)
                hapus(png)
            except:
                pass
            await message.reply_msg(f"ERROR: {err}")
    else:
        await message.reply_msg(
            "Gunakan command <b>/mmf <text></b> dengan reply ke sticker, pisahkan dengan ; untuk membuat posisi text dibawah."
        )


@app.on_message(filters.command(["dice"], COMMAND_HANDLER))
@use_chat_lang()
async def dice(c, m, strings):
    dices = await c.send_dice(m.chat.id, reply_to_message_id=m.id)
    await dices.reply_msg(strings("result").format(number=dices.dice.value), quote=True)


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

@app.on_message(filters.command("tebakgambar"))
async def tebak_gambar(client, message):
    getdata = await fetch.get("https://yasirapi.eu.org/tebakgambar")
    if getdata.status_code != 200:
        return await message.reply_msg("Gagak Mendapatkan data tebak gambar.")
    result = getdata.json()
    image_url = result['data']['result']['image']
    correct_answer = result['data']['result']['answer']
    await message.reply_photo(photo=image_url, caption="Tebak gambar ini! Kamu punya 30 detik untuk menjawab.")
    while True:
        try:
            response = await client.listen(chat_id=message.chat.id, filters=filters.text, timeout=30)
            if response.text.lower() == correct_answer.lower():
                await response.reply_text(f"Selamat! Jawaban kamu benar: <b>{correct_answer.upper()}</b>")
                break
            else:
                await response.reply_text("Jawaban salah, coba lagi!")
        except ListenerTimeout:
            await message.reply_text(f"Waktu habis! Jawaban yang benar adalah: <b>{correct_answer.upper()}</b>")
            break