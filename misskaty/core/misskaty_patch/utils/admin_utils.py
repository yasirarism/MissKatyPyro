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


async def check_rights(
    chat_id: typing.Union[int, int],
    user_id: typing.Union[int, int],
    rights: typing.Union[str, list],
    client,
) -> bool:
    """
    ### `check_rights`
    - Checks the Rights of an User
    - This is an Helper Function for `adminsOnly`

    - Parameters:
    - chat_id (int):
        - The Chat ID of Which Chat have to check the Rights.

    - user_id (int):
        - The User ID of Whose Rights have to Check.

    - rights (str):
        - The Rights have to Check.

    - client (`pyrogram.Client`):
        - From which Client to Check the Rights.

    - Returns:
    - `True` if the User have the Right.
    - `False` if the User don't have the Right.

    #### Example
    .. code-block:: python
        import pyrogram

        app = pyrogram.Client()

        @app.command("ban", group_only=True, self_admin=True)
        async def ban(client, message):
        if not await check_rights(message.chat.id, message.from_user.id, "can_restrict_members"):
            return await message.reply_text("You don't have necessary rights to use this Command.")
        user = await get_user(message)
        await message.chat.kick_member(user.id)
    """
    try:
        user = await client.get_chat_member(chat_id, user_id)
    except Exception:
        return False
    if user.status == "user":
        return False
    if user.status in (
        pyrogram.enums.ChatMemberStatus.OWNER,
        pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
    ):
        permission = []
        if user.privileges.can_manage_chat:
            permission.append("can_manage_chat")

        if user.privileges.can_delete_messages:
            permission.append("can_delete_messages")

        if user.privileges.can_manage_video_chats:
            permission.append("can_manage_video_chats")

        if user.privileges.can_restrict_members:
            permission.append("can_restrict_members")

        if user.privileges.can_promote_members:
            permission.append("can_promote_members")

        if user.privileges.can_change_info:
            permission.append("can_change_info")

        if user.privileges.can_post_messages:
            permission.append("can_post_messages")

        if user.privileges.can_edit_messages:
            permission.append("can_edit_messages")

        if user.privileges.can_invite_users:
            permission.append("can_invite_users")

        if user.privileges.can_pin_messages:
            permission.append("can_pin_messages")

        if user.privileges.is_anonymous:
            permission.append("is_anonymous")

        if isinstance(rights, str):
            return rights in permission
        if isinstance(rights, list):
            for right in rights:
                return right in permission
    return False


async def is_admin(
    chat_id: typing.Union[int, str], user_id: typing.Union[int, str], client
) -> bool:
    """
    ### `is_admin`
    - A Functions to Check if the User is Admin or not

    - Parameters:
        - chat_id (int):
            - The Chat ID of Which Chat have to check the Admin Status.

        - user_id (int):
            - The User ID of Whose Admin Status have to Check.

        - client (`pyrogram.Client`):
            - From which Client to Check the Admin Status.

    - Returns:
        - `True` if the User is Admin.
        - `False` if the User is't Admin.
    #### Example
    .. code-block:: python
        import pyrogram

        app = pyrogram.Client()

        @app.command("ban", group_only=True, self_admin=True)
        @app.adminsOnly("can_restrict_members")
        async def ban(client, message):
            if await is_admin(message.chat.id, (await get_user(mesasge)).id):
                return await message.reply_text("You can't Ban Admins.")
            await message.chat.kick_member((await get_user(message)).id)
            await message.reply_text("User has been Banned.")
    """
    try:
        user = await client.get_chat_member(chat_id, user_id)
    except Exception:
        return False
    return user.status in (
        pyrogram.enums.ChatMemberStatus.OWNER,
        pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
    )
