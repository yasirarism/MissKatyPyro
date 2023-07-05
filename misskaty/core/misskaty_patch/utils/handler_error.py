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
import contextlib
import os
import typing
import logging
import pyrogram
import traceback
from datetime import datetime
from misskaty.vars import LOG_CHANNEL


async def handle_error(
    error, m: typing.Union[pyrogram.types.Message, pyrogram.types.CallbackQuery]
):
    """
    ### `handle_error`
    - A Function to Handle the Errors in Functions.
    - This Sends the Error Log to the Log Group and Replies Sorry Message for the Users.
    - This is Helper for all of the functions for handling the Errors.

    - Parameters:
      - error:
        - The Exceptation.

      - m (`pyrogram.types.Message` or `pyrogram.types.CallbackQuery`):
        - The Message or Callback Query where the Error occurred.

    #### Exapmle
        .. code-block:: python
            import pyrogram

            app = tgClient(pyrogram.Client())

            @app.command("start")
            async def start(client, message):
            try:
                await message.reply_text("Hi :D') # I intentionally made an bug for Example :/
            except Exceptation as e:
                return await handle_error(e, message)
    """

    logging = logging.getLogger(__name__)
    logging.exception(traceback.format_exc())

    day = datetime.now()
    tgl_now = datetime.now()
    cap_day = f"{day.strftime('%A')}, {tgl_now.strftime('%d %B %Y %H:%M:%S')}"

    with open(f"crash_{tgl_now.strftime('%d %B %Y')}.txt", "w+", encoding="utf-8") as log:
        log.write(traceback.format_exc())
        log.close()
    if isinstance(m, pyrogram.types.Message):
        with contextlib.suppress(Exception):
            await m.reply_text(
                "An Internal Error Occurred while Processing your Command, the Logs have been sent to the Owners of this Bot. Sorry for Inconvenience"
            )
            await m._client.send_document(
                LOG_CHANNEL, f"crash_{tgl_now.strftime('%d %B %Y')}.txt", caption=f"Crash Report of this Bot\n{cap_day}"
            )
    if isinstance(m, pyrogram.types.CallbackQuery):
        with contextlib.suppress(Exception):
            await m.message.delete()
            await m.message.reply_text(
                "An Internal Error Occurred while Processing your Command, the Logs have been sent to the Owners of this Bot. Sorry for Inconvenience"
            )
            await m.message._client.send_document(
                LOG_CHANNEL, f"crash_{tgl_now.strftime('%d %B %Y')}.txt", caption=f"Crash Report of this Bot\n{cap_day}"
            )
    os.remove(f"crash_{tgl_now.strftime('%d %B %Y')}.txt")
    return True