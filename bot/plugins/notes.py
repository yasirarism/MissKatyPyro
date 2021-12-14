from database import yasirdb as db
from bot import app
from pyrogram import filters
from info import COMMAND_HANDLER
import json
from bot.utils.admin_helper import is_admin

@app.on_message(filters.command(['save','save@MissKatyRoBot'], COMMAND_HANDLER) & filters.group)
async def addnote(_,message):
    if await is_admin(message.chat.id , message.from_user.id):
        note = message.text.split(' ')[1]
        text = message.text.replace(message.text.split(" ")[0] , "").replace(message.text.split(' ')[1] , "")
        db.insert_one(
            {
                "type": "note",
                "chat_id": message.chat.id,
                "note_name": note,
                "text": text
            }
        )

        await message.reply_text(f'Catatan {note} ditambahkan!')


@app.on_message(filters.command('getnote'))
async def get_note(_,message):
    
    try:
        note = message.text.split(' ')[1]
        data = db.find_one({"chat_id": message.chat.id , "type": "note" , "note_name": note})
        await message.reply(data['text'])        
    except Exception as e:
        await message.reply(f"ERROR: {str(e)}")
        
   
@app.on_message(filters.regex(r"^#.+"), filters.group)
async def gettnote(_,message):
    try:
        note_name = message.text.replace("#" , "")
        data = db.find_one({"chat_id": message.chat.id , "type": "note" , "note_name": note_name})
        await message.reply(data['text'], disable_web_page_preview=True)
    
    except Exception as e:
        await message.reply(f"ERROR: {str(e)}")  
    

@app.on_message(filters.command(['notes','notes@MissKatyRoBot'], COMMAND_HANDLER) & filters.group)
async def notes(_,message):
    notes = None

    for x in db.find({"chat_id": message.chat.id}):
        if notes:
            notes = f"__{notes}__\n __{x['note_name']}__"
        
        else:
            notes = x['note_name']
    
    await message.reply(notes)

    

@app.on_message(filters.command(['delnote','untag@MissKatyRoBot'], COMMAND_HANDLER) & filters.group)
async def delnote(_,message):
    if is_admin(message.chat.id , message.from_user.id):
        note = message.text.split(" ")[1]
        db.delete_one({"note_name": note})
        await message.reply(f'Catatan #{note} dihapus!')
    else:
        await message.reply('Kamu bukan admin disini')
