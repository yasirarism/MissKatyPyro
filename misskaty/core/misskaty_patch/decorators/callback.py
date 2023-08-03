# tgEasy - Easy for a brighter Shine. A monkey pather add-on for Pyrogram
# Copyright (C) 2021 - 2022 Jayant Hegde Kageri <https://github.com/jayantkageri>

# This file is part of tgEasy.

# tgEasy is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# tgEasy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with tgEasy.  If not, see <http://www.gnu.org/licenses/>.

import typing

import pyrogram
from pyrogram.methods import Decorators

from ..utils import handle_error


def callback(
    self,
    data: typing.Union[str, list],
    self_admin: typing.Union[bool, bool] = False,
    filtercb: typing.Union[pyrogram.filters.Filter] = None,
    *args,
    **kwargs,
):
    """
    ### `Client.callback`

    - A decorater to Register Callback Quiries in simple way and manage errors in that Function itself, alternative for `@pyrogram.Client.on_callback_query(pyrogram.filters.regex('^data.*'))`
    - Parameters:
    - data (str || list):
        - The callback query to be handled for a function

    - self_admin (bool) **optional**:
        - If True, the command will only executeed if the Bot is Admin in the Chat, By Default False

    - filter (`~pyrogram.filters`) **optional**:
        - Pyrogram Filters, hope you know about this, for Advaced usage. Use `and` for seaperating filters.

    #### Example
    .. code-block:: python
        import pyrogram

        app = pyrogram.Client()

        @app.command("start")
        async def start(client, message):
            await message.reply_text(
            f"Hello {message.from_user.mention}",
            reply_markup=pyrogram.types.InlineKeyboardMarkup([[
                pyrogram.types.InlineKeyboardButton(
                "Click Here",
                "data"
                )
            ]])
            )

        @app.callback("data")
        async def data(client, CallbackQuery):
        await CallbackQuery.answer("Hello :)", show_alert=True)
    """
    if filtercb:
        filtercb = pyrogram.filters.regex(f"^{data}.*") & args["filter"]
    else:
        filtercb = pyrogram.filters.regex(f"^{data}.*")

    def wrapper(func):
        async def decorator(client, CallbackQuery: pyrogram.types.CallbackQuery):
            if self_admin:
                me = await client.get_chat_member(
                    CallbackQuery.message.chat.id, (await client.get_me()).id
                )
                if me.status not in (
                    pyrogram.enums.ChatMemberStatus.OWNER,
                    pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                ):
                    return await CallbackQuery.message.edit_text(
                        "I must be admin to execute this Command"
                    )
            try:
                await func(client, CallbackQuery)
            except pyrogram.errors.exceptions.forbidden_403.ChatAdminRequired:
                pass
            except BaseException as e:
                return await handle_error(e, CallbackQuery)

        self.add_handler(pyrogram.handlers.CallbackQueryHandler(decorator, filtercb))
        return decorator

    return wrapper


Decorators.on_cb = callback
