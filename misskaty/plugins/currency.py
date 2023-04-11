from pyrogram import filters, Client
from pyrogram.types import Message
from misskaty import app
from misskaty.helper.http import http
from misskaty.core.message_utils import kirimPesan
from misskaty.vars import COMMAND_HANDLER, CURRENCY_API


__MODULE__ = "Currency"
__HELP__ = """
/currency - Send structure message Telegram in JSON using Pyrogram Style.
"""

@app.on_message(filters.command(["currency"], COMMAND_HANDLER))
async def currency(c: Client, m: Message):
    if CURRENCY_API is None:
        return await kirimPesan(
            m,
            "<code>Oops!!get the API from</code> "
            "<a href='https://app.exchangerate-api.com/sign-up'>HERE</a> "
            "<code>& add it to config vars</code> (<code>CURRENCY_API</code>)",
            disable_web_page_preview=True)
    if len(m.command) == 3:
        cmd, amount, currency_to, currency_from = m.text.split()
    else:
        return await kirimPesan(m, "Use format /{m.command[0]} [amount] [currency_from] [currency_to] to convert currency.")

    if amount.isdigit():
        url = ("https://v6.exchangerate-api.com/v6/{831e8214d53d862bf1dbd721}/"
               f"pair/{currency_from}/{currency_to}/{amount}")
        try:
            res = await http.get(url)
            data = res.json()
            try:
                conversion_rate = round(data["conversion_rate"])
                conversion_result = round(data["conversion_result"])
            except KeyError:
                return await kirimPesan(m, "<code>Invalid response from api !</i>")

            await kirimPesan(
                m,
                "**CURRENCY EXCHANGE RATE RESULT:**\n\n"
                f"`{amount}` **{currency_to.upper()}** = `{conversion_result}` **{currency_from.upper()}**\n"
                f"<b>Rate Today</b> = {conversion_rate}")
        except:
            await kirimPesan(m, "Failed convert currency, maybe you give wrong currency format or api down.")
    else:
        await kirimPesan(
            m,
            r"<code>This seems to be some alien currency, which I can't convert right now.. (⊙_⊙;)</code>")