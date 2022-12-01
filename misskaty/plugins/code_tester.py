from pyrogram import enums, filters
from pyrogram.errors import MessageTooLong
import aiohttp
from misskaty.helper.tools import rentry
from info import COMMAND_HANDLER
from misskaty import app

__MODULE__ = "CodeTester"
__HELP__ = """
This feature allows you to run multiple programming languages through this bot via the Glot.io api.  The following is a list of supported languages, for temporary commands only support with a "!"  like the example below.

List of Supported Programming Languages:
~> assembly
~> ats
~> bash
~> c
~> clojure
~> cobol
~> coffeescript
~> cpp
~> crystal
~> csharp
~> d
~> elixir
~> elm
~> erlang
~> fsharp
~> go
~> groovy
~> haskell
~> idris
~> java
~> javascript
~> julia
~> kotlin
~> lua
~> mercury
~> nim
~> nix
~> ocaml
~> perl
~> php
~> python
~> raku
~> ruby
~> rust
~> scala
~> swift
~> typescript

**Example:**
~> `!python print("Hai aku MissKatyRoBot")`
"""


async def listcode():
    async with aiohttp.ClientSession() as session:
        r = await session.get("https://glot.io/api/run")
        return await r.json()


async def glot(lang, langcode, code):
    async with aiohttp.ClientSession() as session:
        data = {"files": [{"name": f"misskaty.{langcode}", "content": code}]}
        headers = {"content-type": "application/json", "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"}
        r = await session.post(f"https://glot.io/api/run/{lang}/latest", headers=headers, json=data)
        return await r.json()


@app.on_message(filters.command(["codelist"], COMMAND_HANDLER))
async def list_lang(client, message):
    daftarlang = await listcode()
    list_ = "".join(f"~> {i['name']}\n" for i in daftarlang)
    return await message.reply(f"<b>List of Supported Programming Languages:</b>\n{list_}")


@app.on_message(filters.command(["assembly"], "!"))
@app.on_edited_message(filters.command(["assembly"], "!"))
async def assembly(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "asm", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["ats"], "!"))
@app.on_edited_message(filters.command(["ats"], "!"))
async def ats(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "dats", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["bash"], "!"))
@app.on_edited_message(filters.command(["bash"], "!"))
async def bash(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "sh", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["c"], "!"))
@app.on_edited_message(filters.command(["c"], "!"))
async def c(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "c", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["clojure"], "!"))
@app.on_edited_message(filters.command(["clojure"], "!"))
async def clojure(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "clj", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["cobol"], "!"))
@app.on_edited_message(filters.command(["cobol"], "!"))
async def cobol(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "cob", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["coffeescript"], "!"))
@app.on_edited_message(filters.command(["coffeescript"], "!"))
async def coffeescript(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "coffee", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["cpp"], "!"))
@app.on_edited_message(filters.command(["cpp"], "!"))
async def cpp(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "cpp", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["crystal"], "!"))
@app.on_edited_message(filters.command(["crystal"], "!"))
async def crystal(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "cr", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["csharp"], "!"))
@app.on_edited_message(filters.command(["csharp"], "!"))
async def csharp(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "cs", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["d"], "!"))
@app.on_edited_message(filters.command(["d"], "!"))
async def d(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "d", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["elixir"], "!"))
@app.on_edited_message(filters.command(["elixir"], "!"))
async def elixir(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "ex", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["elm"], "!"))
@app.on_edited_message(filters.command(["elm"], "!"))
async def elm(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "elm", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["erlang"], "!"))
@app.on_edited_message(filters.command(["erlang"], "!"))
async def erlang(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "erl", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["fsharp"], "!"))
@app.on_edited_message(filters.command(["fsharp"], "!"))
async def fsharp(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "fs", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["go"], "!"))
@app.on_edited_message(filters.command(["go"], "!"))
async def go(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "go", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["groovy"], "!"))
@app.on_edited_message(filters.command(["groovy"], "!"))
async def groovy(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "groovy", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["haskell"], "!"))
@app.on_edited_message(filters.command(["haskell"], "!"))
async def haskell(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "hs", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["idris"], "!"))
@app.on_edited_message(filters.command(["idris"], "!"))
async def idris(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "idr", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["java"], "!"))
@app.on_edited_message(filters.command(["java"], "!"))
async def java(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "java", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["javascript"], "!"))
@app.on_edited_message(filters.command(["javascript"], "!"))
async def javascript(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "js", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["julia"], "!"))
@app.on_edited_message(filters.command(["julia"], "!"))
async def julia(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "jl", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["kotlin"], "!"))
@app.on_edited_message(filters.command(["kotlin"], "!"))
async def kotlin(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "kt", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["lua"], "!"))
@app.on_edited_message(filters.command(["lua"], "!"))
async def lua(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "lua", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["mercury"], "!"))
@app.on_edited_message(filters.command(["mercury"], "!"))
async def mercury(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "m", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["nim"], "!"))
@app.on_edited_message(filters.command(["nim"], "!"))
async def nim(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "nim", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["nix"], "!"))
@app.on_edited_message(filters.command(["nix"], "!"))
async def nix(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "nix", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["ocaml"], "!"))
@app.on_edited_message(filters.command(["ocaml"], "!"))
async def ocaml(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "ml", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["perl"], "!"))
@app.on_edited_message(filters.command(["perl"], "!"))
async def perl(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "pl", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["php"], "!"))
@app.on_edited_message(filters.command(["php"], "!"))
async def php(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "php", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["python"], "!"))
@app.on_edited_message(filters.command(["python"], "!"))
async def python(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "py", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["raku"], "!"))
@app.on_edited_message(filters.command(["raku"], "!"))
async def raku(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "raku", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["ruby"], "!"))
@app.on_edited_message(filters.command(["ruby"], "!"))
async def ruby(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "rb", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["rust"], "!"))
@app.on_edited_message(filters.command(["rust"], "!"))
async def rust(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "rs", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["scala"], "!"))
@app.on_edited_message(filters.command(["scala"], "!"))
async def scala(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "scala", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["swift"], "!"))
@app.on_edited_message(filters.command(["swift"], "!"))
async def swift(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "swift", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(["typescript"], "!"))
@app.on_edited_message(filters.command(["typescript"], "!"))
async def typescript(client, message):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(message.command[0], "ts", message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)
