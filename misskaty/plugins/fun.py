import textwrap
from asyncio import gather
from os import remove as hapus

from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters

from misskaty import app
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER


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
