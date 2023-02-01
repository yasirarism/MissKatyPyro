from pyrogram import filters

from datetime import datetime
import datetime as dtime
import asyncio, time

data = {}

async def task(msg, warn = False, sec = None):
    try:await msg.delete()
    except:pass
    if warn:
        user = msg.from_user
        ids = await msg.reply(f"Sorry {user.mention}, you're in cooldown now, wait for {sec}s to use command again..")
        await asyncio.sleep(sec)
        await ids.edit(f"Alright {user.mention}, your cooldown is over you can command again.")
        await asyncio.sleep(1)
        await ids.delete()

def wait(sec):
    async def ___(flt, cli, msg):
        user_id = msg.from_user.id
        timestamp = time.mktime(msg.date.timetuple())
        if user_id in data:
            if timestamp >= data[user_id]['timestamp'] + flt.data:
                data[user_id] = {'timestamp' : msg.date, 'warned' : False}
                return True
            else:
                if not data[user_id]['warned']:
                    data[user_id]['warned'] = True
                    asyncio.ensure_future(task(msg, True, flt.data)) # for super accuracy use (future - time.time())
                    return False # cause we dont need delete again

                asyncio.ensure_future(task(msg))
                return False
        else:
            data.update({user_id : {'timestamp' : timestamp, 'warned' : False}})
            return True
    return filters.create(___, data=sec)