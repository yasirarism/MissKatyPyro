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
import typing

import pyrogram


async def get_user(
    m: typing.Union[pyrogram.types.Message, pyrogram.types.CallbackQuery]
) -> pyrogram.types.User or bool:
    """
    ### `tgEasy.get_user`
    - Gets a User from Message/RepliedMessage/CallbackQuery
    - Parameters:
      - m (`~pyrogram.types.Message` || `~pyrogram.types.CallbackQuery`)
    - Returns:
      - `pyrogram.types.User` on Success
      - `False` on Error

    #### Example
        .. code-block:: python
            from tgEasy import get_user, command, adminsOnly

            @command("ban", group_only=True, self_admin=True)
            @adminsOnly("can_restrict_members")
            async def ban(client, message):
                user = await get_user(message)
                await message.chat.kick_member(user.id)
    """
    if isinstance(m, pyrogram.types.Message):
        message = m
        client = m._client
    if isinstance(m, pyrogram.types.CallbackQuery):
        message = m.message
        client = message._client
    if message.reply_to_message:
        if message.reply_to_message.sender_chat:
            return False
        return await client.get_users(message.reply_to_message.from_user.id)

    command = message.command[1] if len(message.command) > 1 else None
    if command and (command.startswith("@") or command.isdigit()):
        with contextlib.suppress(
            pyrogram.errors.exceptions.bad_request_400.UsernameNotOccupied,
            pyrogram.errors.exceptions.bad_request_400.UsernameInvalid,
            pyrogram.errors.exceptions.bad_request_400.PeerIdInvalid,
            IndexError,
        ):
            return await client.get_users(message.command[1])
    if message.entities:
        for mention in message.entities:
            if mention.type == "text_mention":
                user = mention.user.id
                break
        with contextlib.suppress(Exception):
            return await client.get_users(user)
    return False


async def get_user_adv(
    m: typing.Union[pyrogram.types.Message, pyrogram.types.CallbackQuery]
) -> pyrogram.types.User or bool:
    """
    ### `tgEasy.get_user_adv`
    - A Function to Get the User from the Message/CallbackQuery, If there is None arguments, returns the From User.
    - Parameters:
      - m (`pyrogram.types.Message` || `pyrogram.types.CallbackQuery`):
        - Message or Callbackquery.
    - Returns:
      - `pyrogram.types.User` on Success
      - `False` on Error

    #### Example
        .. code-block:: python
            from tgEasy import command, get_user_adv

            @command("id")
            async def id(client, message):
                user = await get_user_adv(message)
                await message.reply_text(f"Your ID is `{user.id}`")
    """
    if isinstance(m, pyrogram.types.Message):
        message = m
    if isinstance(m, pyrogram.types.CallbackQuery):
        message = m.message
    if message.sender_chat:
        return False
    with contextlib.suppress(IndexError, AttributeError):
        if len(message.command) > 1:
            if message.command[1].startswith("@"):
                return await get_user(message)
            if message.command[1].isdigit():
                return await get_user(message)
            if "text_mention" in message.entities:
                return await get_user(message)
            if "from_user" in str(message.reply_to_message):
                return await get_user(message)
    with contextlib.suppress(Exception):
        if "sender_chat" in str(message.reply_to_message):
            return False
        if "from_user" in str(message.reply_to_message):
            return await message._client.get_users(
                message.reply_to_message.from_user.id
            )
    return await message._client.get_users(message.from_user.id)
