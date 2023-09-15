# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import logging

from pyrogram.types import Message

from misskaty import app
from misskaty.helper.http import fetch
from misskaty.vars import CURRENCY_API

__MODULE__ = "Currency"
__HELP__ = """
/currency - Send structure message Telegram in JSON using Pyrogram Style.
"""

LOGGER = logging.getLogger("MissKaty")


@app.on_cmd("currency")
async def currency(_, ctx: Message):
    if CURRENCY_API is None:
        return await ctx.reply_msg(
            "<code>Oops!!get the API from</code> <a href='https://app.exchangerate-api.com/sign-up'>HERE</a> <code>& add it to config vars</code> (<code>CURRENCY_API</code>)",
            disable_web_page_preview=True,
        )
    if len(ctx.text.split()) != 4:
        return await ctx.reply_msg(
            f"Use format /{ctx.command[0]} [amount] [currency_from] [currency_to] to convert currency.",
            del_in=6,
        )

    _, amount, currency_from, currency_to = ctx.text.split()
    if amount.isdigit() or (
        amount.replace(".", "", 1).isdigit() and amount.count(".") < 2
    ):
        url = (
            f"https://v6.exchangerate-api.com/v6/{CURRENCY_API}/"
            f"pair/{currency_from}/{currency_to}/{amount}"
        )
        try:
            res = await fetch.get(url)
            data = res.json()
            try:
                conversion_rate = data["conversion_rate"]
                conversion_result = data["conversion_result"]
                target_code = data["target_code"]
                base_code = data["base_code"]
                last_update = data["time_last_update_utc"]
            except KeyError:
                return await ctx.reply_msg("<code>Invalid response from api !</i>")
            await ctx.reply_msg(
                f"**CURRENCY EXCHANGE RATE RESULT:**\n\n`{format(float(amount), ',')}` **{base_code}** = `{format(float(conversion_result), ',')}` **{target_code}**\n<b>Rate Today</b> = `{format(float(conversion_rate), ',')}`\n<b>Last Update:</b> {last_update}"
            )
        except Exception as err:
            await ctx.reply_msg(
                f"Failed convert currency, maybe you give wrong currency format or api down.\n\n<b>ERROR</b>: {err}"
            )
    else:
        await ctx.reply_msg(
            "<code>This seems to be some alien currency, which I can't convert right now.. (⊙_⊙;)</code>"
        )
