# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import platform
import re
from datetime import datetime, timedelta

import pytz
from apscheduler.jobstores.base import ConflictingIdError
from pyrogram import __version__, filters
from pyrogram.errors import (
    ChannelInvalid,
    ChannelPrivate,
    ChatAdminRequired,
    ChatNotModified,
    ChatRestricted,
    PeerIdInvalid,
)
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup

from database.locale_db import get_db_lang
from misskaty import BOT_NAME, app, scheduler
from misskaty.core.decorator.permissions import require_admin
from misskaty.helper.localization import langdict, use_chat_lang
from misskaty.vars import COMMAND_HANDLER, LOG_CHANNEL, TZ

__MODULE__ = "NightMode"
__HELP__ = """<b>Enable or disable nightmode (locks the chat at specified intervals everyday)</b>
<b>Flags:</b>
'-s': "Specify starting time in 24hr format."
'-e': "Specify duration in hours / minute"
'-d': "Disable nightmode for chat."

<b>Examples:</b>
/nightmode -s=23:53 -e=6h
/nightmode -s=23:50 -e=120m
/nightmode -d
"""

TIME_ZONE = pytz.timezone(TZ)
reply_markup = InlineKeyboardMarkup(
    [[InlineKeyboardButton(text="❤️", callback_data="nightmd")]]
)


# Check calculate how long it will take to Ramadhan
def puasa():
    now = datetime.now(pytz.timezone("Asia/Jakarta"))
    tahun = now.strftime("%Y")
    bulan = now.strftime("%m")
    tgl = now.strftime("%d")
    jam = now.strftime("%H")
    menit = now.strftime("%M")
    detik = now.strftime("%S")
    x = datetime(int(tahun), int(bulan), int(tgl), int(jam), int(menit), int(detik))
    y = datetime(2022, 4, 2, 0, 0, 0)
    return y - x


def tglsekarang():
    now = datetime.now(pytz.timezone("Asia/Jakarta"))
    days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    month = [
        "Unknown",
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember",
    ]
    tgl = now.strftime("%d")
    tahun = now.strftime("%Y")
    jam = now.strftime("%H:%M")
    return f"{days[now.weekday()]}, {tgl} {month[now.month]} {tahun} {jam}"


def extract_time(time_val: str):
    if any(time_val.endswith(unit) for unit in ("m", "h")):
        unit = time_val[-1]
        time_num = time_val[:-1]
        if not time_num.isdigit():
            return ""
        if unit == "m":
            time = int(time_num) * 60
        elif unit == "h":
            time = int(time_num) * 60 * 60
        else:
            return ""
        return time
    return ""


async def un_mute_chat(chat_id: int, perm: ChatPermissions):
    getlang = await get_db_lang(chat_id)
    getlang = getlang or "en-US"
    try:
        await app.set_chat_permissions(chat_id, perm)
    except ChatAdminRequired:
        await app.send_message(
            LOG_CHANNEL,
            langdict[getlang]["nightmodev2"]["nmd_off_not_admin"].format(
                chat_id=chat_id, bname=BOT_NAME
            ),
        )
    except (ChannelInvalid, ChannelPrivate, PeerIdInvalid):
        scheduler.remove_job(f"enable_nightmode_{chat_id}")
        scheduler.remove_job(f"disable_nightmode_{chat_id}")
        await app.send_message(
            LOG_CHANNEL,
            langdict[getlang]["nightmodev2"]["nmd_off_not_present"].format(
                chat_id=chat_id, bname=BOT_NAME
            ),
        )
    except ChatNotModified:
        pass
    except Exception as e:
        await app.send_message(
            LOG_CHANNEL,
            langdict[getlang]["nightmodev2"]["nmd_off_err"].format(
                chat_id=chat_id, e=e
            ),
        )
    else:
        job = scheduler.get_job(f"enable_nightmode_{chat_id}")
        close_at = job.next_run_time
        try:
            await app.send_message(
                chat_id,
                langdict[getlang]["nightmodev2"]["nmd_off_success"].format(
                    dt=tglsekarang(), close_at=close_at
                ),
                reply_markup=reply_markup,
            )
        except ChatRestricted:
            scheduler.remove_job(f"enable_nightmode_{chat_id}")
            scheduler.remove_job(f"disable_nightmode_{chat_id}")


async def mute_chat(chat_id: int):
    getlang = await get_db_lang(chat_id)
    getlang = getlang or "en-US"
    try:
        await app.set_chat_permissions(chat_id, ChatPermissions())
    except ChatAdminRequired:
        await app.send_message(
            LOG_CHANNEL,
            langdict[getlang]["nightmodev2"]["nmd_on_not_admin"].format(
                chat_id=chat_id, bname=BOT_NAME
            ),
        )
    except (ChannelInvalid, ChannelPrivate, PeerIdInvalid):
        scheduler.remove_job(f"enable_nightmode_{chat_id}")
        scheduler.remove_job(f"disable_nightmode_{chat_id}")
        await app.send_message(
            LOG_CHANNEL,
            langdict[getlang]["nightmodev2"]["nmd_on_not_present"].format(
                chat_id=chat_id, bname=BOT_NAME
            ),
        )
    except ChatNotModified:
        pass
    except Exception as e:
        await app.send_message(
            LOG_CHANNEL,
            langdict[getlang]["nightmodev2"]["nmd_on_err"].format(chat_id=chat_id, e=e),
        )
    else:
        job = scheduler.get_job(f"disable_nightmode_{chat_id}")
        open_at = job.next_run_time
        await app.send_message(
            chat_id,
            langdict[getlang]["nightmodev2"]["nmd_on_success"].format(
                dt=tglsekarang(), open_at=open_at
            ),
            reply_markup=reply_markup,
        )


@app.on_message(filters.command("nightmode", COMMAND_HANDLER) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def nightmode_handler(_, msg, strings):
    chat_id = msg.chat.id

    if "-d" in msg.text:
        if scheduler.get_job(job_id=f"enable_nightmode_{chat_id}"):
            scheduler.remove_job(job_id=f"enable_nightmode_{chat_id}")
            scheduler.remove_job(job_id=f"disable_nightmode_{chat_id}")
            if not bool(scheduler.get_jobs()) and bool(scheduler.state):
                scheduler.shutdown()
            return await msg.reply_msg(strings("nmd_disabled"))
        return await msg.reply_msg(strings("nmd_not_enabled"))

    starttime = re.findall(r"-s=(\d+:\d+)", msg.text)
    start = starttime[0] if starttime else "00:00"
    now = datetime.now(TIME_ZONE)

    try:
        start_timestamp = TIME_ZONE.localize(
            datetime.strptime((now.strftime("%m:%d:%Y - ") + start), "%m:%d:%Y - %H:%M")
        )
    except ValueError:
        return await msg.reply_msg(strings("invalid_time_format"), del_in=6)
    lockdur = re.findall(r"-e=(\w+)", msg.text)
    lockdur = lockdur[0] if lockdur else "6h"
    lock_dur = extract_time(lockdur.lower())

    if not lock_dur:
        return await msg.reply_msg(strings("invalid_lockdur"), del_in=6)

    if start_timestamp < now:
        start_timestamp = start_timestamp + timedelta(days=1)
    end_time_stamp = start_timestamp + timedelta(seconds=int(lock_dur))
    try:
        # schedule to enable nightmode
        scheduler.add_job(
            mute_chat,
            "interval",
            [chat_id],
            id=f"enable_nightmode_{chat_id}",
            days=1,
            next_run_time=start_timestamp,
            max_instances=50,
            misfire_grace_time=None,
        )

        # schedule to disable nightmode
        scheduler.add_job(
            un_mute_chat,
            "interval",
            [chat_id, msg.chat.permissions],
            id=f"disable_nightmode_{chat_id}",
            days=1,
            next_run_time=end_time_stamp,
            max_instances=50,
            misfire_grace_time=None,
        )
    except ConflictingIdError:
        return await msg.reply_msg(strings("schedule_already_on"))
    await msg.reply_msg(
        strings("nmd_enable_success").format(
            st=start_timestamp.strftime("%H:%M:%S"), lockdur=lockdur
        )
    )
    if not bool(scheduler.state):
        scheduler.start()


@app.on_callback_query(filters.regex(r"^nightmd$"))
@use_chat_lang()
async def callbackanightmd(c, q, strings):
    await q.answer(
        strings("nmd_cb").format(
            bname=c.me.first_name, ver=__version__, pyver=platform.python_version()
        ),
        show_alert=True,
        cache_time=10,
    )
