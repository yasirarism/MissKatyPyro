"""Nightmode — Auto-leave grup yang mengunci/menonaktifkan izin menulis bot (ChatWriteForbidden).

Fitur:
- /nightmode on|off : toggle fitur utk grup ini.
- Saat bot kena ChatWriteForbidden di grup yg nightmode aktif, data grup
  otomatis dihapus dr db & bot auto-leave (dihubungkan dr misskaty_patch/bound).

Output pesan memakai rich message style + custom emoji Telegram
(<emoji id=...>fallback</emoji>).
"""

from database.nightmode_chat_db import (  # isort: skip
    is_nightmode_on,
    nightmode_off,
    nightmode_on,
)
from misskaty import app
from misskaty.vars import COMMAND_HANDLER

__MODULE__ = "Nightmode"
__HELP__ = """
Nightmode - Auto-leave grup yg mengunci/mematikan izin menulis bot.

/nightmode [on|off] - Aktifkan/nonaktifkan fitur utk grup ini.
Saat aktif, kalau bot tidak bisa kirim pesan (ChatWriteForbidden) di grup
tersebut, bot otomatis leave & menghapus data nightmode.
"""

# Custom emoji Telegram (fallback unicode jika tidak bisa dirender)
_MOON = "<emoji id=6008118472066732010>🌙</emoji>"
_BELL = "<emoji id=5879770735999717115>📢</emoji>"
_SUN = "<emoji id=5316979941181496594>🌞</emoji>"
_WARN = "<emoji id=5956561916573782596>⚠️</emoji>"


@app.on_cmd("nightmode", group_only=True)
async def nightmode_toggle(_, message):
    # Hanya admin yang boleh toggle
    member = None
    try:
        member = await message.chat.get_member(message.from_user.id)
    except Exception:
        pass
    if not member or member.status not in ("administrator", "owner"):
        return await message.reply_text("❌ Hanya admin grup yang bisa menggunakan ini.")

    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg == "on":
        if await is_nightmode_on(message.chat.id):
            return await message.reply_text(f"{_MOON} <b>Nightmode</b> sudah aktif di grup ini.")
        await nightmode_on(message.chat.id)
        return await message.reply_text(
            f"{_MOON} <b>Nightmode dinyalakan!</b>\n\n"
            f"{_BELL} Mulai sekarang, jika bot tidak bisa menulis "
            f"(<code>ChatWriteForbidden</code>), bot akan otomatis "
            f"<b>leave grup</b> dan menghapus data nightmode.\n"
            f"{_SUN} Untuk matikan: <code>{COMMAND_HANDLER[0]}nightmode off</code>"
        )
    if arg == "off":
        if not await is_nightmode_on(message.chat.id):
            return await message.reply_text(f"{_MOON} Nightmode belum aktif utk grup ini.")
        await nightmode_off(message.chat.id)
        return await message.reply_text(f"{_SUN} <b>Nightmode dinonaktifkan</b> utk grup ini.")

    return await message.reply_text(
        f"{_WARN} <b>Usage:</b> <code>{COMMAND_HANDLER[0]}nightmode on|off</code>\n\n"
        f"{_MOON} <b>on</b> : aktifkan pelacakan (auto-leave saat bot tidak bisa chat)\n"
        f"{_SUN} <b>off</b>: nonaktifkan"
    )