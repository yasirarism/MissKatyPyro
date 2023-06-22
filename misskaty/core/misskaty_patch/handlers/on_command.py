import typing

import pyrogram

from misskaty.vars import COMMAND_HANDLER


class Command:
    def on_cmd(
        self,
        command: typing.Union[str, list],
        pm_only: typing.Union[bool, bool] = False,
        group_only: typing.Union[bool, bool] = False,
        self_admin: typing.Union[bool, bool] = False,
        self_only: typing.Union[bool, bool] = False,
        handler: typing.Optional[list] = None,
        filter: typing.Union[pyrogram.filters.Filter, pyrogram.filters.Filter] = None,
        *args,
        **kwargs,
    ):
        """
        ### `tgEasy.tgClient.command`
        - A decorater to Register Commands in simple way and manage errors in that Function itself, alternative for `@pyrogram.Client.on_message(pyrogram.filters.command('command'))`
        - Parameters:
        - command (str || list):
            - The command to be handled for a function

        - group_only (bool) **optional**:
            - If True, the command will only executed in Groups only, By Default False.

        - pm_only (bool) **optional**:
            - If True, the command will only executed in Private Messages only, By Default False.

        - self_only (bool) **optional**:
            - If True, the command will only excute if used by Self only, By Default False.

        - handler (list) **optional**:
            - If set, the command will be handled by the specified Handler, By Default `Config.HANDLERS`.

        - self_admin (bool) **optional**:
            - If True, the command will only executeed if the Bot is Admin in the Chat, By Default False

        - filter (`~pyrogram.filters`) **optional**:
            - Pyrogram Filters, hope you know about this, for Advaced usage. Use `and` for seaperating filters.

        #### Example
        .. code-block:: python
            import pyrogram
            from tgEasy import tgClient

            app = tgClient(pyrogram.Client())

            @app.command("start", group_only=False, pm_only=False, self_admin=False, self_only=False, pyrogram.filters.chat("777000") and pyrogram.filters.text)
            async def start(client, message):
                await message.reply_text(f"Hello {message.from_user.mention}")
        """
        if handler is None:
            handler = COMMAND_HANDLER
        if filter:
            if self_only:
                filter = pyrogram.filters.command(command, prefixes=handler) & filter & pyrogram.filters.me
            else:
                filter = pyrogram.filters.command(command, prefixes=handler) & filter & pyrogram.filters.me
        else:
            if self_only:
                filter = pyrogram.filters.command(command, prefixes=handler) & pyrogram.filters.me
            else:
                filter = pyrogram.filters.command(command, prefixes=handler)

        def wrapper(func):
            async def decorator(client, message: pyrogram.types.Message):
                if self_admin and message.chat.type != pyrogram.enums.ChatType.SUPERGROUP:
                    return await message.reply_text("This command can be used in supergroups only.")
                if self_admin:
                    me = await client.get_chat_member(message.chat.id, (await client.get_me()).id)
                    if me.status not in (
                        pyrogram.enums.ChatMemberStatus.OWNER,
                        pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                    ):
                        return await message.reply_text("I must be admin to execute this Command")
                if group_only and message.chat.type != pyrogram.enums.ChatType.SUPERGROUP:
                    return await message.reply_text("This command can be used in supergroups only.")
                if pm_only and message.chat.type != pyrogram.enums.ChatType.PRIVATE:
                    return await message.reply_text("This command can be used in PMs only.")
                try:
                    await func(client, message)
                except pyrogram.errors.exceptions.forbidden_403.ChatWriteForbidden:
                    await client.leave_chat(message.chat.id)
                except BaseException as exception:
                    return await handle_error(exception, message)

            self.__client__.add_handler(pyrogram.handlers.MessageHandler(callback=decorator, filters=filter))
            return decorator

        return wrapper
