from pyrogram import Client, idle, filters

api_id = 1046625
api_hash = "c68afc924b92d73ce27708b155f1e5b4"
bot_token = "1507530289:AAFLdrEV-SmWiQPyfmMe9r2Y-LmtgB0Shdw"

app = Client("YasirUBot", api_id=api_id, api_hash=api_hash)
app2 = Client("MissKatyBot",
              api_id=api_id,
              api_hash=api_hash,
              bot_token=bot_token)


@app.on_message(filters.command("hai"))
def hai(client, message):
    message.reply("hai")


@app2.on_message(filters.command("hai2"))
def hai2(client, message):
    message.reply("ok")


app.start()
app2.start()
s = app.export_session_string()
print(s)
idle()
