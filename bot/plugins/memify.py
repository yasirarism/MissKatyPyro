from bot.utils.decorator import capture_err
from bot import app
from pyrogram import filters
from info import COMMAND_HANDLER
from PIL import Image, ImageFont, ImageDraw
import textwrap, os

async def draw_meme_text(image_path, text):
    img = Image.open(image_path)
    os.remove(image_path)
    i_width, i_height = img.size
    m_font = ImageFont.truetype(
        "Calistoga-Regular.ttf",
        int((70 / 640) * i_width)
    )
    if ";" in text:
        upper_text, lower_text = text.split(";")
    else:
        upper_text = text
        lower_text = ''
    draw = ImageDraw.Draw(img)
    current_h, pad = 10, 5
    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            u_width, u_height = draw.textsize(u_text, font=m_font)

            draw.text(xy=(((i_width - u_width) / 2) - 1, int((current_h / 640)*i_width)),
                      text=u_text, font=m_font, fill=(0, 0, 0), stroke_width=3, stroke_fill='black')
            draw.text(xy=(((i_width - u_width) / 2) + 1, int((current_h / 640)*i_width)),
                      text=u_text, font=m_font, fill=(0, 0, 0), stroke_width=3, stroke_fill='black')
            draw.text(xy=((i_width - u_width) / 2, int(((current_h / 640)*i_width)) - 1),
                      text=u_text, font=m_font, fill=(0, 0, 0), stroke_width=3, stroke_fill='black')
            draw.text(xy=(((i_width - u_width) / 2), int(((current_h / 640)*i_width)) + 1),
                      text=u_text, font=m_font, fill=(0, 0, 0), stroke_width=3, stroke_fill='black')

            draw.text(xy=((i_width - u_width) / 2, int((current_h / 640)*i_width)),
                      text=u_text, font=m_font, fill=(255, 255, 255))
            current_h += u_height + pad
    if lower_text:
        for l_text in textwrap.wrap(lower_text, width=15):
            u_width, u_height = draw.textsize(l_text, font=m_font)

            draw.text(
                xy=(((i_width - u_width) / 2) - 1, i_height - u_height - int((20 / 640)*i_width)),
                text=l_text, font=m_font, fill=(0, 0, 0), stroke_width=3, stroke_fill='black')
            draw.text(
                xy=(((i_width - u_width) / 2) + 1, i_height - u_height - int((20 / 640)*i_width)),
                text=l_text, font=m_font, fill=(0, 0, 0), stroke_width=3, stroke_fill='black')
            draw.text(
                xy=((i_width - u_width) / 2, (i_height - u_height - int((20 / 640)*i_width)) - 1),
                text=l_text, font=m_font, fill=(0, 0, 0), stroke_width=3, stroke_fill='black')
            draw.text(
                xy=((i_width - u_width) / 2, (i_height - u_height - int((20 / 640)*i_width)) + 1),
                text=l_text, font=m_font, fill=(0, 0, 0), stroke_width=3, stroke_fill='black')

            draw.text(
                xy=((i_width - u_width) / 2, i_height - u_height - int((20 / 640)*i_width)),
                text=l_text, font=m_font, fill=(255, 255, 255), stroke_width=3, stroke_fill='black')
            current_h += u_height + pad

    webp_file = "memify.webp"
    img.save(webp_file, "WebP")
    return webp_file

@capture_err
@app.on_message(filters.command(["mmf"], COMMAND_HANDLER))
async def memify(client, message):
  if message.reply_to_message and (not message.reply_to_message.sticker.is_animated or message.reply_to_message.photo):
    try:
      file = await message.reply_to_message.download()
      res = await draw_meme_text(file, message.text.split(None, 1)[1].strip())
      await message.reply_sticker(res)
      try:
        os.remove(res)
      except:
        pass
    except:
      await message.reply("Gunakan command <b>/mmf <text></b> dengan reply ke sticker, pisahkan dengan ; untuk membuat posisi text dibawah.")
  else:
    await message.reply("Gunakan command <b>/mmf <text></b> dengan reply ke sticker, pisahkan dengan ; untuk membuat posisi text dibawah.")
