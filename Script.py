class script(object):
    START_TXT = """Hai {},
Namaku adalah <a href=https://t.me/{}>{}</a>, aku punya beberapa fitur berguna loh 😍. Penasaran? silahkan dicoba yaa. Mungkin masih ada banyak bug di bot ini, jadi harap dimaklumi saja yaa 😃."""
    HELP_TXT = """Hai {}
Ini adalah daftar menu bantuan bot MissKatyRoBot. Kamu bisa membaca petunjuk melalui button dibawah ini.
<b>Catatan:</b>
Menu Bantuan ini belum selesai dibuat jadi mungkin masih acak-acakan.
Jika kamu ada kendala, bisa tanya saya di grup @indocloud atau @YMovieZChat. Jangan lupa yaa join disitu 🙃..

<b>Status Server Bot:</b>
<b>Bot Uptime:</b> <code>{}</code>
<b>Total Ruang Penyimpanan:</b> <code>{}</code>
<b>Disk Kosong:</b> <code>{}</code>
<b>Disk Digunakan:</b> <code>{}</code>
<b>CPU:</b> {}% <b>RAM:</b> {}% <b>DISK:</b> {}%

Semua command bisa digunakan dengan ! atau /."""
    ABOUT_TXT = """✯ Tentang Saya: {}
✯ OWNER: <a href=https://t.me/YasirArisM>Yasir Aris M</a>
✯ LIBRARY: Pyrogram
✯ BAHASA: Python 3
✯ DATABASE: MONGO DB
✯ SERVER BOT: HEROKU
✯ BUILD STATUS: v1.0.1 [ BETA ]"""
    SOURCE_TXT = """<b>NOTE:</b>
- MissKatyRoBot adalah project closed source. Saya hanya membuat bot ini untuk sekedar belajar mengenai programming. 

<b>Owner:</b>
- <a href=https://t.me/YasirArisM>Yasir Aris M</a>"""
    MANUELFILTER_TXT = """Help: <b>Admin</b>

- Berikut ini ada beberapa fitur yang berguna banget buat manajemen grup.

<b>Commands and Usage:</b>
• /ban - <code>Banned user dari grup</code>
• /dban - <code>Hapus pesan dan banned user dari grup</code>
• /kickme - <code>Menendang diri sendiri dari grup</code>
• /kick - <code>kick from a chat</code>
• /del - <code>delete a specific filter in chat</code>
• /delall - <code>Hapus pesan seluruh chat.</code>
• /purge - <code>Hapus seluruh pesan mulain dari pesan yang direply.</code>
• /pin - <code>delete the whole filters in a chat (chat owner only)</code>
Docs ini belum selesai harap bersabar.. 🙃"""
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

Fitur ini kamu bisa menjalankan beberapa bahasa pemrograman melalui bot ini. Berikut ini daftar bahasa yang didukung. Untuk command sementara hanya support dengan tanda "!" seperti contoh dibawah.

<b>Daftar Bahasa Pemrograman Yang Didukung:</b>
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
~> <code>!python print("Hai aku MissKatyRoBot")</code>
"""
    CONNECTION_TXT = """Help: <b>Inline</b>

- Used to connect bot to PM for managing filters 
- it helps to avoid spamming in groups.

<b>NOTE:</b>
1. Only admins can add a connection.
2. Send <code>/connect</code> for connecting me to ur PM

<b>Commands and Usage:</b>
• /google  - <code>connect a particular chat to your PM</code>
• /disconnect  - <code>disconnect from a chat</code>
• /connections - <code>list all your connections</code>"""
    EXTRAMOD_TXT = """Help: <b>Extra Modules</b>

<b>NOTE:</b>
Ini adalah fitur tambahan dari MissKatyRoBot, mungkin akan saya kelompokkan berdasarkan kategori jika sempat.

<b>Commands and Usage:</b>
• /id - <code>Dapatkan ID dari seorang user atau grup.</code>
• /info  - <code>Dapatkan informasi mengenai user.</code>
• /imdb  - <code>Dapatkan informasi mengenai film/series dari IMDb. (Translate ke Bahasa Indonesia)</code>
• /webss  - <code>Ambil screenshot dari sebuah website.</code>
• /json - <code>Melihat struktur pesan di Telegram. (<b>Pyrogram Version</b>)
• /mediainfo - <code>Reply ke pesan Telegram atau dengan command /mediainfo [direct link], untuk mengetahui metadata sebuah file. Sangat berguna jika kamu punya channel film..</code>
• /tr, /trans - <code>Untuk menterjemahkan kalimat.</code>
• /tts - <code>Mengubah pesan teks menjadi voice message.</code>
• /google - <code>Browsing google melalui bot.</code>
• /tosticker - <code>Mengubah foto menjadi sticker.</code>
• /toimage - <code>Mengubah sticker menjadi foto.</code>
• /ocr - <code>Mengubah gambar atau sticker menjadi tulisan.</code>
"""
    ADMIN_TXT = """Help: <b>Admin mods</b>

<b>NOTE:</b>
This module only works for my owner

<b>Commands and Usage:</b>
• /run - <code>Menjalankan kode python</code>
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
Jumlah Members = <code>{}</code>
Ditambahkan Oleh - {}
"""
    LOG_TEXT_P = """#NewUser
ID - <code>{}</code>
Name - {}
"""
