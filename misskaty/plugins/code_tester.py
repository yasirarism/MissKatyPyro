import aiohttp
from pyrogram import enums, filters
from pyrogram.errors import MessageTooLong

from misskaty import app
from misskaty.helper.tools import rentry
from misskaty.vars import COMMAND_HANDLER

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

# command "!" → langcode Glot.io (ekstensi file source).
GLOT_LANGS = {
    "assembly": "asm",
    "ats": "dats",
    "bash": "sh",
    "c": "c",
    "clojure": "clj",
    "cobol": "cob",
    "coffeescript": "coffee",
    "cpp": "cpp",
    "crystal": "cr",
    "csharp": "cs",
    "d": "d",
    "elixir": "ex",
    "elm": "elm",
    "erlang": "erl",
    "fsharp": "fs",
    "go": "go",
    "groovy": "groovy",
    "haskell": "hs",
    "idris": "idr",
    "java": "java",
    "javascript": "js",
    "julia": "jl",
    "kotlin": "kt",
    "lua": "lua",
    "mercury": "m",
    "nim": "nim",
    "nix": "nix",
    "ocaml": "ml",
    "perl": "pl",
    "php": "php",
    "python": "py",
    "raku": "raku",
    "ruby": "rb",
    "rust": "rs",
    "scala": "scala",
    "swift": "swift",
    "typescript": "ts",
}


async def listcode():
    async with aiohttp.ClientSession() as session:
        r = await session.get("https://glot.io/api/run")
        return await r.json()


async def glot(lang, langcode, code):
    async with aiohttp.ClientSession() as session:
        data = {"files": [{"name": f"misskaty.{langcode}", "content": code}]}
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb",
        }
        r = await session.post(
            f"https://glot.io/api/run/{lang}/latest", headers=headers, json=data
        )
        return await r.json()


@app.on_message(filters.command(["codelist"], COMMAND_HANDLER))
async def list_lang(_, message):
    daftarlang = await listcode()
    list_ = "".join(f"~> {i['name']}\n" for i in daftarlang)
    return await message.reply(
        f"<b>List of Supported Programming Languages:</b>\n{list_}"
    )


async def _run_glot(message, lang, langcode):
    if len(message.command) < 2:
        return await message.reply("Please enter the code you want to run.")
    res = await glot(lang, langcode, message.text.split(None, 1)[1])
    hasil = res["stdout"] or res["stderr"]
    hasil = f"Result :\n{hasil}"
    try:
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except MessageTooLong:
        post = await rentry(hasil)
        return await message.reply(f"<b>View Result in Rentry:</b>\n{post}")
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@app.on_message(filters.command(list(GLOT_LANGS), "!"))
@app.on_edited_message(filters.command(list(GLOT_LANGS), "!"))
async def run_code(_, message):
    lang = message.command[0]
    await _run_glot(message, lang, GLOT_LANGS[lang])
