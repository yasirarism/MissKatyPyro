import json
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.plugins.dev import shell_exec
from bot import app
from pyrogram import filters
from info import COMMAND_HANDLER
from bot.utils.decorator import capture_err

@capture_err
@app.on_message(filters.command(["extractsub"], COMMAND_HANDLER))
async def extractsub(_, msg):
  if len(link) == 1:
     return await msg.reply('null.')
  link = msg.text.split()[1]
  pesan = await msg.reply("Processing...")
  res = (await shell_exec(f"ffprobe -loglevel 0 -print_format json -show_format -show_streams {link}"))[0]
  details = json.loads(res)
  buttons = []
  DATA[f"{msg.chat.id}-{pesan.id}"] = {}
  for stream in details["streams"]:
    mapping = stream['index']
    stream_name = stream['codec_name']
    stream_type = stream['codec_type']
    if stream_type in ("audio", "subtitle"):
      pass
    else:
      continue
    try:
      lang = stream["tags"]["language"]
    except:
       lang = mapping
    DATA[f"{msg.chat.id}-{pesan.id}"][int(mapping)] = {
            "map" : mapping,
            "name" : stream_name,
            "type" : stream_type,
            "lang" : lang,
            "link" : link
    }
    buttons.append([
            InlineKeyboardButton(
                f"{stream_type.upper()} - {str(lang).upper()}", f"{stream_type}_{mapping}_{message.chat.id}-{msg.message_id}"
            )
    ])

  buttons.append([
        InlineKeyboardButton("CANCEL",f"cancel_{mapping}_{message.chat.id}-{msg.message_id}")
  ])
  await pesan.edit_text(
        "**Select the Stream to be Extracted...**",
        reply_markup=InlineKeyboardMarkup(buttons)
  )
