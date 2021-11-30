class script(object):
    START_TXT = """Hai {},
Namaku adalah <a href=https://t.me/{}>{}</a>, aku punya beberapa fitur berguna loh 😍. Penasaran? silahkan dicoba yaa. Mungkin masih ada banyak bug di bot ini, jadi harap dimaklumi 😃."""
    HELP_TXT = """Hai {}
Ini adalah daftar menu bantuan."""
    ABOUT_TXT = """✯ 𝙼𝚈 𝙽𝙰𝙼𝙴: {}
✯ OWNER: <a href=https://t.me/YasirArisM>Yasir Aris M</a>
✯ LIBRARY: Pyrogram
✯ BAHASA: Python 3
✯ DATABASE: MONGO DB
✯ SERVER BOT: Railway
✯ BUILD STATUS: v1.0.1 [ BETA ]"""
    SOURCE_TXT = """<b>NOTE:</b>
- MissKatyRoBot adalah project closed source. Saya hanya membuat bot ini untuk sekedar belajar mengenai programming. 
- Source - 🙃

<b>Owner:</b>
- <a href=https://t.me/YasirArisM>Yasir Aris M</a>"""
    MANUELFILTER_TXT = """Help: <b>Admin</b>

- Berikut ini ada beberapa fitur yang berguna banget buat manajemen grup.

<b>Commands and Usage:</b>
• /ban - <code>Banned user dari grup</code>
• /kick - <code>list all the filters of a chat</code>
• /del - <code>delete a specific filter in chat</code>
• /delall - <code>delete the whole filters in a chat (chat owner only)</code>"""
    BUTTON_TXT = """Help: <b>Buttons</b>

<b>NOTE:</b>
1. Telegram will not allows you to send buttons without any content, so content is mandatory.
2. Eva Maria supports buttons with any telegram media type.
3. Buttons should be properly parsed as markdown format

<b>URL buttons:</b>
<code>[Button Text](buttonurl:https://t.me/EvaMariaBot)</code>

<b>Alert buttons:</b>
<code>[Button Text](buttonalert:This is an alert message)</code>"""
    AUTOFILTER_TXT = """Help: <b>Code Runner</b>

Fitur ini kamu bisa menjalankan beberapa bahasa pemrograman melalui bot ini. Berikut ini daftar bahasa yang didukung.

Daftar Bahasa Pemrograman Yang Didukung:
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

<b>Cara penggunaan:</b>
~> <code>/python print("Hai aku MissKatyRoBot")</code>
"""
    CONNECTION_TXT = """Help: <b>Connections</b>

- Used to connect bot to PM for managing filters 
- it helps to avoid spamming in groups.

<b>NOTE:</b>
1. Only admins can add a connection.
2. Send <code>/connect</code> for connecting me to ur PM

<b>Commands and Usage:</b>
• /connect  - <code>connect a particular chat to your PM</code>
• /disconnect  - <code>disconnect from a chat</code>
• /connections - <code>list all your connections</code>"""
    EXTRAMOD_TXT = """Help: <b>Extra Modules</b>

<b>NOTE:</b>
these are the extra features of Eva Maria

<b>Commands and Usage:</b>
• /id - <code>get id of a specifed user.</code>
• /info  - <code>get information about a user.</code>
• /imdb  - <code>get the film information from IMDb source.</code>
• /search  - <code>get the film information from various sources.</code>"""
    ADMIN_TXT = """Help: <b>Admin mods</b>

<b>NOTE:</b>
This module only works for my admins

<b>Commands and Usage:</b>
• /logs - <code>to get the rescent errors</code>
• /stats - <code>to get status of files in db.</code>
• /delete - <code>to delete a specific file from db.</code>
• /users - <code>to get list of my users and ids.</code>
• /chats - <code>to get list of the my chats and ids </code>
• /leave  - <code>to leave from a chat.</code>
• /disable  -  <code>do disable a chat.</code>
• /ban  - <code>to ban a user.</code>
• /unban  - <code>to unban a user.</code>
• /channel - <code>to get list of total connected channels</code>
• /broadcast - <code>to broadcast a message to all users</code>"""
    STATUS_TXT = """★ 𝚃𝙾𝚃𝙰𝙻 𝙵𝙸𝙻𝙴𝚂: <code>{}</code>
★ Jumlah Pengguna: <code>{}</code>
★ Jumlah Chat: <code>{}</code>
★ Penggunaan Storage Disk: <code>{}</code> 𝙼𝚒𝙱
★ Sisa Ruang Disk: <code>{}</code> 𝙼𝚒𝙱"""
    LOG_TEXT_G = """#NewGroup
Group = {}(<code>{}</code>)
Total Members = <code>{}</code>
Added By - {}
"""
    LOG_TEXT_P = """#NewUser
ID - <code>{}</code>
Name - {}
"""
