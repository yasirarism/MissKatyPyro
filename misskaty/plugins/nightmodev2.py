from email import message
import re
from datetime import datetime, timedelta

import pytz
from apscheduler.jobstores.base import ConflictingIdError
from pyrogram import filters
from pyrogram.errors import (ChannelInvalid, ChannelPrivate, ChatAdminRequired,
                             ChatNotModified)
from pyrogram.types import ChatPermissions

from database.nightmode_db import TZ, scheduler
from misskaty import BOT_NAME, app
from misskaty.core.message_utils import *
from misskaty.core.decorator.permissions import adminsOnly
from misskaty.vars import COMMAND_HANDLER, LOG_CHANNEL

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

def extract_time(time_val: str):
    if any(time_val.endswith(unit) for unit in ('m', 'h')):
        unit = time_val[-1]
        time_num = time_val[:-1]
        if not time_num.isdigit():
            return ""
        if unit == 'm':
            time = int(time_num) * 60
        elif unit == 'h':
            time = int(time_num) * 60 * 60
        else:
            return ""
        return time
    return ""

async def un_mute_chat(chat_id: int, perm: ChatPermissions):
    try:
        await app.set_chat_permissions(chat_id, perm)
    except ChatAdminRequired:
        await app.send_message(
            LOG_CHANNEL,
            f"#NIGHT_MODE_FAIL\nFailed to turn off nightmode at `{chat_id}`,"
            f"since {BOT_NAME} is not an admin in chat `{chat_id}`")
    except (ChannelInvalid, ChannelPrivate):
        scheduler.remove_job(f"enable_nightmode_{chat_id}")
        scheduler.remove_job(f"disable_nightmode_{chat_id}")
        await app.send_message(
            LOG_CHANNEL,
            f"#NIGHT_MODE_FAIL\nFailed to turn off nightmode at `{chat_id}`,"
            f"since {BOT_NAME} is not present in chat `{chat_id}`"
            " Removed group from list.")
    except ChatNotModified:
        pass
    except Exception as e:
        await app.send_message(
            LOG_CHANNEL,
            f"#NIGHT_MODE_FAIL\nFailed to turn off nightmode at `{chat_id}`\n"
            f"ERROR: `{e}`")
    else:
        job = scheduler.get_job(f"enable_nightmode_{chat_id}")
        close_at = job.next_run_time
        await app.send_message(
            chat_id,
            f"#AUTOMATED_HANDLER\nGroup is Opening.\nWill be closed at {close_at}")
        await app.send_message(
            LOG_CHANNEL,
            f"#NIGHT_MODE_SUCCESS\nSuccessfully turned off nightmode at `{chat_id}`,")


async def mute_chat(chat_id: int):
    try:
        await app.set_chat_permissions(chat_id, ChatPermissions())
    except ChatAdminRequired:
        await app.send_message(
            LOG_CHANNEL,
            f"#NIGHT_MODE_FAIL\nFailed to enable nightmode at `{chat_id}`,"
            f"since {BOT_NAME} is not an admin in chat `{chat_id}`")
    except (ChannelInvalid, ChannelPrivate):
        scheduler.remove_job(f"enable_nightmode_{chat_id}")
        scheduler.remove_job(f"disable_nightmode_{chat_id}")
        await app.send_message(
            LOG_CHANNEL,
            f"#NIGHT_MODE_FAIL\nFailed to enable nightmode at `{chat_id}`,"
            f"since {BOT_NAME} is not present in chat `{chat_id}`"
            " Removed group from list.")
    except ChatNotModified:
        pass
    except Exception as e:
        await app.send_message(
            LOG_CHANNEL,
            f"#NIGHT_MODE_FAIL\nFailed to enable nightmode at `{chat_id}`\n"
            f"ERROR: `{e}`")
    else:
        job = scheduler.get_job(f"disable_nightmode_{chat_id}")
        open_at = job.next_run_time
        await app.send_message(
            chat_id,
            f"#AUTOMATED_HANDLER\nGroup is closing.\nWill be opened at {open_at}")
        await app.send_message(
            LOG_CHANNEL,
            f"#NIGHT_MODE_SUCCESS\nSuccessfully turned on nightmode at `{chat_id}`,")

@app.on_message(filters.command("nightmode", COMMAND_HANDLER) & filters.group)
@adminsOnly("can_change_info")
async def nightmode_handler(c, msg):
    chat_id = msg.chat.id

    if "-d" in msg.text:
        job = scheduler.get_job(job_id=f"enable_nightmode_{chat_id}")
        if job:
            scheduler.remove_job(job_id=f"enable_nightmode_{chat_id}")
            scheduler.remove_job(job_id=f"disable_nightmode_{chat_id}")
            if not bool(scheduler.get_jobs()) and bool(scheduler.state):
                scheduler.shutdown()
            return await kirimPesan(msg, 'Nightmode disabled.')
        return await kirimPesan(msg, "Nightmode isn't enabled in this chat.")

    starttime = re.findall(r"-s=(\d+:\d+)", msg.text)
    start = starttime if starttime else "00:00"
    now = datetime.now(TIME_ZONE)

    try:
        start_timestamp = TIME_ZONE.localize(
            datetime.strptime(
                (now.strftime('%m:%d:%Y - ') + start),
                '%m:%d:%Y - %H:%M'))
    except ValueError:
        return await kirimPesan(msg, "Invalid time format. Use HH:MM format.")
    lockdur = re.findall(r"-e=(\w+)", msg.text)
    lockdur = lockdur if lockdur else "6h"
    lock_dur = extract_time(lockdur.lower())

    if not lock_dur:
        return await kirimPesan(
            msg,
            'Invalid time duration. Use proper format.'
            '\nExample: 6h (for 6 hours), 10m for 10 minutes.')

    if start_timestamp < now:
        start_timestamp = start_timestamp + timedelta(days=1)
    end_time_stamp = start_timestamp + timedelta(seconds=int(lock_dur))
    try:
        # schedule to enable nightmode
        scheduler.add_job(
            mute_chat,
            'interval',
            [chat_id],
            id=f"enable_nightmode_{chat_id}",
            days=1,
            next_run_time=start_timestamp,
            max_instances=50,
            misfire_grace_time=None)

        # schedule to disable nightmode
        scheduler.add_job(
            un_mute_chat,
            'interval',
            [chat_id,
            msg.chat.permissions],
            id=f"disable_nightmode_{chat_id}",
            days=1,
            next_run_time=end_time_stamp,
            max_instances=50,
            misfire_grace_time=None)
    except ConflictingIdError:
        return await kirimPesan(
            msg,
            'Already a schedule is running in this chat. Disable it using `-d` flag.')
    await kirimPesan(
        msg,
        'Successfully enabled nightmode in this chat.\n'
        f'Group will be locked at {start_timestamp.strftime("%H:%M:%S")}'
        f' and will be opened after {lockdur} everyday.')
    if not bool(scheduler.state):
        scheduler.start()

if bool(scheduler.get_jobs()):
    scheduler.start()