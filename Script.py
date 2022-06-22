class script(object):
    START_TXT = """Hai {},
Namaku adalah <a href=https://t.me/{}>{}</a>, aku punya beberapa fitur berguna loh 😍. Penasaran? silahkan dicoba yaa. Mungkin masih ada banyak bug di bot ini, jadi harap dimaklumi saja yaa 😃."""
    SCRAP_TXT = """Disini tersedia command scraper untuk beberapa web film:
>> Melongmovie <<
Search: /melongmovie [judul]
Download Link (Owner Only): /melong [link]
>> Lk21 <<
Search: /lk21 [judul]
>> Movieku.cc <<
Search: /movieku [judul]
Download Link: /movieku_scrap [link]
>> Savefilm21 <<
Search: /savefilm21 [judul]
Download Link: /savefilm21_scrap [link]
>> Ngefilm21 <<
Search: /ngefilm21 [judul]
>> Nodrakor <<
Search: /nodrakor [judul]"""
    HELP_TXT = """Hai {}
Ini adalah daftar menu bantuan bot MissKatyRoBot. Kamu bisa membaca petunjuk melalui button dibawah ini.
<b>Catatan:</b>
Menu Bantuan ini belum selesai dibuat jadi mungkin masih acak-acakan.
Jika kamu ada kendala, bisa tanya saya di grup @indoupload atau @YMovieZChat. Jangan lupa yaa join disitu 🙃..

<b>Status Server Bot:</b>
<b>Bot Uptime:</b> <code>{}</code>
<b>Total Ruang Penyimpanan:</b> <code>{}</code>
<b>Disk Kosong:</b> <code>{}</code>
<b>Disk Digunakan:</b> <code>{}</code>
<b>CPU:</b> {}% <b>RAM:</b> {}% <b>DISK:</b> {}%

Hampir command bisa digunakan dengan ! atau /. Beberapa fitur atau menu help mungkin ada yang bermasalah, saya belum ada waktu untuk fix itu."""
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
• /pin - <code>Pin pesan digrup</code>
• /unpin - <code>Unpin pesan tersemat digrup</code>
• /adminlist - <code>Dapatkan daftar admin disebuah grup</code>
"""
    BUTTON_TXT = """No help"""
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

- No help"""
    EXTRAMOD_TXT = """Help: <b>Extra Modules</b>

<b>NOTE:</b>
Ini adalah fitur tambahan dari MissKatyRoBot.

<b>Daftar Perintah:</b>
• /id - <code>Dapatkan ID dari seorang user atau grup.</code>
• /info  - <code>Dapatkan informasi mengenai user.</code>
• /imdb  - <code>Dapatkan informasi mengenai film/series dari IMDb. (Translate ke Bahasa Indonesia)</code>
• /webss  - <code>Ambil screenshot dari sebuah website.</code>
• /json - <code>Melihat struktur pesan di Telegram. (<b>Pyrogram Versi 2</b>)
• /mediainfo - <code>Reply ke pesan Telegram atau dengan command /mediainfo [direct link], untuk mengetahui metadata sebuah file.</code>
• /tr, /trans - <code>Untuk menterjemahkan kalimat.</code>
• /tts - <code>Mengubah pesan teks menjadi voice message.</code>
• /google - <code>Browsing google melalui bot.</code>
• /tosticker - <code>Mengubah foto menjadi sticker.</code>
• /toimage - <code>Mengubah sticker menjadi foto.</code>
• /ocr - <code>Mengubah gambar atau sticker menjadi tulisan.</code>
• /genss [jumlah] - <code>Generate screenshot dari file Video.</code>
• /afk [alasan] - <code>Tandai diri kamu sedang AFK saat dimention.</code>
• /q - <code>Membuat stiker dari pesan, pesan bot tidak bisa di quote.</code>
• /paste - <code>Paste text ke Github Gist.</code>
"""
    ADMIN_TXT = """Help: <b>Admin mods</b>

<b>NOTE:</b>
This module only works for my owner

<b>Commands and Usage:</b>
• /run - <code>Menjalankan kode python</code>
• /logs - <code>to get the rescent errors</code>
• /users - <code>to get list of my users and ids.</code>
• /chats - <code>to get list of the my chats and ids </code>
• /leave  - <code>to leave from a chat.</code>
• /disable  -  <code>do disable a chat.</code>
• /ban  - <code>to ban a user.</code>
• /unban  - <code>to unban a user.</code>
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
