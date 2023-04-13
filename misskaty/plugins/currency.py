from pyrogram import filters, Client
from pyrogram.types import Message
from misskaty import app
import logging
from misskaty.helper.http import http
from misskaty.core.message_utils import kirimPesan
from misskaty.vars import COMMAND_HANDLER, CURRENCY_API


__MODULE__ = "Currency"
__HELP__ = """
/currency - Send structure message Telegram in JSON using Pyrogram Style.
"""

LOGGER = logging.getLogger(__name__)


@app.on_message(filters.command(["currency"], COMMAND_HANDLER))
async def currency(c: Client, m: Message):
    if CURRENCY_API is None:
        return await kirimPesan(
            m,
            "<code>Oops!!get the API from</code> <a href='https://app.exchangerate-api.com/sign-up'>HERE</a> <code>& add it to config vars</code> (<code>CURRENCY_API</code>)",
            disable_web_page_preview=True,
        )
    if len(m.text.split()) != 4:
        return await kirimPesan(m, f"Use format /{m.command[0]} [amount] [currency_from] [currency_to] to convert currency.")

    teks = m.text.split()
    amount = teks[1]
    currency_from = teks[2]
    currency_to = teks[3]
    if amount.isdigit():
        url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API}/" f"pair/{currency_from}/{currency_to}/{amount}"
        try:
            res = await http.get(url)
            data = res.json()
            try:
                conversion_rate = data["conversion_rate"]
                conversion_result = data["conversion_result"]
                target_code = data["target_code"]
                base_code = data["base_code"]
                last_update = data["time_last_update_utc"]
            except KeyError:
                return await kirimPesan(m, "<code>Invalid response from api !</i>")
            await kirimPesan(m, "**CURRENCY EXCHANGE RATE RESULT:**\n\n" f"`{amount}` **{base_code}** = `{round(conversion_result)}` **{target_code}**\n" f"<b>Rate Today</b> = `{round(conversion_rate)}`\n" f"<b>Last Update:</b> {last_update}")
        except:
            await kirimPesan(m, "Failed convert currency, maybe you give wrong currency format or api down.")
    else:
        await kirimPesan(m, r"<code>This seems to be some alien currency, which I can't convert right now.. (⊙_⊙;)</code>")
