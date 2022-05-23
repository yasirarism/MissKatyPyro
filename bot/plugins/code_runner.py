from pyrogram import Client, filters, enums
import requests, json, aiohttp
from info import COMMAND_HANDLER


async def listcode():
    async with aiohttp.ClientSession() as session:
        r = await session.get("https://glot.io/api/run")
        return await r.json()


async def glot(lang, langcode, code):
    async with aiohttp.ClientSession() as session:
        data = {"files": [{"name": f"Yasir.{langcode}", "content": code}]}
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        r = await session.post(f"https://glot.io/api/run/{lang}/latest",
                               headers=headers,
                               json=data)
        return await r.json()


@Client.on_message(
    filters.command(["codelist", "codelist@MissKatyRoBot"], COMMAND_HANDLER))
async def list_lang(client, message):
    daftarlang = await listcode()
    list_ = "".join(f"~> {i['name']}\n" for i in daftarlang)
    return await message.reply(
        f"Daftar Bahasa Pemrograman Yang Didukung:\n{list_}")


@Client.on_message(filters.command(["assembly"], "!"))
async def assembly(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        res = await glot("assembly", "asm", message.text.split(None, 1)[1])
        hasil = res['stdout'] if res['stdout'] else res['stderr']
        hasil = f"Hasil :\n{hasil}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["ats", "ats@MissKatyRoBot"], "!"))
async def ats(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/ats/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.dats", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["bash", "bash@MissKatyRoBot"], "!"))
async def bash(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/bash/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.sh", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["c", "c@MissKatyRoBot"], "!"))
async def c(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/c/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.c", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["clojure", "clojure@MissKatyRoBot"], "!"))
async def clojure(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/clojure/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.clj", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["cobol", "cobol@MissKatyRoBot"], "!"))
async def cobol(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/cobol/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.cob", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(
    filters.command(["coffeescript", "coffeescript@MissKatyRoBot"], "!"))
async def coffeescript(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/coffeescript/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.coffee", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["cpp", "cpp@MissKatyRoBot"], "!"))
async def cpp(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/cpp/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.cpp", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["crystal", "crystal@MissKatyRoBot"], "!"))
async def crystal(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/crystal/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.cr", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["csharp", "csharp@MissKatyRoBot"], "!"))
async def csharp(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/csharp/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.cs", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["d", "d@MissKatyRoBot"], "!"))
async def d(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/d/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.d", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["elixir", "elixir@MissKatyRoBot"], "!"))
async def elixir(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/elixir/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.ex", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["elm", "elm@MissKatyRoBot"], "!"))
async def elm(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/elm/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.elm", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["erlang", "erlang@MissKatyRoBot"], "!"))
async def erlang(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/erlang/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.erl", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["fsharp", "fsharp@MissKatyRoBot"], "!"))
async def fsharp(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/fsharp/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.fs", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["go", "go@MissKatyRoBot"], "!"))
async def go(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/go/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.go", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["groovy", "groovy@MissKatyRoBot"], "!"))
async def groovy(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/groovy/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.groovy", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["haskell", "haskell@MissKatyRoBot"], "!"))
async def haskell(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/haskell/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.hs", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["idris", "idris@MissKatyRoBot"], "!"))
async def idris(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/idris/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.idr", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["java", "java@MissKatyRoBot"], "!"))
async def java(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/java/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.java", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(
    filters.command(["javascript", "javascript@MissKatyRoBot"], "!"))
async def javascript(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/javascript/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.js", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["julia", "julia@MissKatyRoBot"], "!"))
async def julia(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/julia/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.jl", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["kotlin", "kotlin@MissKatyRoBot"], "!"))
async def kotlin(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/kotlin/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.kt", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["lua", "lua@MissKatyRoBot"], "!"))
async def lua(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/lua/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.lua", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["mercury", "mercury@MissKatyRoBot"], "!"))
async def mercury(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/mercury/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.m", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["nim", "nim@MissKatyRoBot"], "!"))
async def nim(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/nim/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.nim", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["nix", "nix@MissKatyRoBot"], "!"))
async def nix(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/nix/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.nix", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["ocaml", "ocaml@MissKatyRoBot"], "!"))
async def ocaml(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/ocaml/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.ml", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["perl", "perl@MissKatyRoBot"], "!"))
async def perl(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/perl/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.pl", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']
        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["php", "php@MissKatyRoBot"], "!"))
async def php(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/php/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.php", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["python", "python@MissKatyRoBot"], "!"))
async def python(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/python/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.py", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["raku", "raku@MissKatyRoBot"], "!"))
async def raku(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/raku/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.raku", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["ruby", "ruby@MissKatyRoBot"], "!"))
async def ruby(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/ruby/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.rb", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["rust", "rust@MissKatyRoBot"], "!"))
async def rust(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/rust/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.rs", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["scala", "scala@MissKatyRoBot"], "!"))
async def scala(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/scala/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.scala", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(filters.command(["swift", "swift@MissKatyRoBot"], "!"))
async def swift(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/ats/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.swift", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        stdout = response['stdout']

        stderr = response['stderr']
        hasil = f"Hasil : {stdout}\nStderr : {stderr}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)


@Client.on_message(
    filters.command(["typescript", "typescript@MissKatyRoBot"], "!"))
async def typescript(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "Silahkan masukkan kode yang ingin dijalankan.")
    try:
        siteurl = "https://glot.io/api/run/typescript/latest"
        headers = {
            "content-type": "application/json",
            "Authorization": "Token b8a2b75a-a078-4089-869c-e53d448b1ebb"
        }
        code = message.text.split(None, 1)[1]
        data = {"files": [{"name": "Yasir.ts", "content": code}]}
        response = requests.post(siteurl, json=data, headers=headers)
        response = response.json()
        hasil = response['stdout'] if response['stdout'] else response['stderr']
        hasil = f"Hasil :\n{stdout}"
        return await message.reply(hasil, parse_mode=enums.ParseMode.DISABLED)
    except Exception as e:
        return await message.reply(e, parse_mode=enums.ParseMode.DISABLED)
