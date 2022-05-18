# Source https://github.com/yourtulloh/Gist-Telegram-Bot
from os import remove
from re import compile as compiles
from requests import post, delete
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot import app
from info import COMMAND_HANDLER

class Github_Gist: # Learn class for first time, PR if bad or want to improve

    def __init__(self, title: str = "", description: str = "", is_secret: bool = False): # All Params For Custom, Maybe Later
        self.api = "https://api.github.com/gists"
        self.token = "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" # Github Token with Gist Create Permission
        self.title = title
        self.description = description
        self.secret = is_secret
        self.username = app.get_me().username
        if not self.title:
            self.title = f"Gist Paste by @{self.username}"
        if not self.description:
            self.description = f"Github Gist created by @{self.username} from Telegram"


    def create(self, text: str) -> dict:
        data = {
            "description": self.description,
            "public": self.secret,
            "files": {
                self.title: {
                    "content": text
                    }
                }
            }
        headers = {
            "Authorization": f"token {self.token}",
            "Content-Type": "application/json"
        }
        resp = post(self.api, headers=headers, data=dumps(data))
        if any(x == resp.status_code for x in [200, 201]):
            resp = resp.json()
            if not resp.get('message'):
                result = {
                    "url": resp.get('html_url'),
                    "raw": list(resp.get('files').values())[0].get('raw_url').replace(' ', '%20')
                }
                return result
            else:
                raise Exception(f"ERROR : {resp.get('message')}")
        else:
            raise Exception(f"ERROR : Failed To Create Github Gist")

    def delete(self, ids: str) -> str:
        headers = {
            "Authorization": f"token {self.token}"
        }
        resp = delete(self.api + '/' + ids, headers=headers)
        if resp.ok:
            return "Success Delete Gist With ID {}".format(ids)
        else:
            raise Exception(f"ERROR : Failed To Delete Github Gist")


# Size Checker for Limit
def humanbytes(size: int):
    """Convert Bytes To Bytes So That Human Can Read It"""
    if not isinstance(command, int):
        try:
            size = int(size)
        except ValueError:
            size = None
    if not size:
        return "0 B"
    size = int(size)
    power = 2**10
    raised_to_pow = 0
    dict_power_n = {
        0: "",
        1: "K",
        2: "M",
        3: "G",
        4: "T",
        5: "P",
        6: "E",
        7: "Z",
        8: "Y"
    }
    while size > power:
        size /= power
        raised_to_pow += 1
    try:
        real_size = str(round(size,
                              2)) + " " + dict_power_n[raised_to_pow] + "B"
    except KeyError:
        real_size = "Can't Define Real Size !"
    return real_size

# Pattern if extension supported, PR if want to add more
pattern = compiles(r"^text/|json$|yaml$|xml$|toml$|x-sh$|x-shellscript$")

@app.on_message(filters.command(["paste"], COMMAND_HANDLER))
async def create(_, message):
    reply = message.reply_to_message
    target = str(message.command[0]).split("@", maxsplit=1)[0]
    if not reply and len(message.command) < 2:
        return await message.reply_text(
            f"**Reply To A Message With /{target} or with command**"
        )

    msg = await message.reply_text("`Pasting to Github Gist...`")
    data = ''
    limit = 1024 * 1024
    if reply and reply.document:
        if reply.document.file_size > limit:
            return await msg.edit(
                f"**You can only paste files smaller than {humanbytes(limit)}.**"
            )
        if not pattern.search(reply.document.mime_type):
            return await msg.edit("**Only text files can be pasted.**")
        file = await reply.download()
        try:
            with open(file, "r") as text:
                data = text.read()
            remove(file)
        except UnicodeDecodeError:
            try:
                remove(file)
            except:
                pass
            return await msg.edit('`File Not Supported !`')
    elif reply and (reply.text or reply.caption):
        data = reply.text or reply.caption
    elif not reply and len(message.command) >= 2:
        data = message.text.split(None, 1)[1]

    if message.from_user:
        if message.from_user.username:
            uname = f"@{message.from_user.username}"
        else:
            uname = f'[{message.from_user.first_name}](tg://user?id={message.from_user.id})'
    else:
        uname = message.sender_chat.title

    try:
        resp = Github_Gist.create(data)
        url = resp.get("url")
        raw = resp.get("raw")
    except Exception as e:
        await msg.edit(f"`{e}`")
        return

    if not url:
        return await msg.edit("Text Too Short Or File Problems")
    button = []
    if raw is not None:
        button.append([
            InlineKeyboardButton("Open Link", url=url),
            InlineKeyboardButton("Raw Link", url=raw)
        ])
    else:
        button.append([InlineKeyboardButton("Open Link", url=url)])
    button.append([
        InlineKeyboardButton("Share Link",
                             url=f"https://telegram.me/share/url?url={url}")
    ])

    pasted = f"**Here's your Github Gist URL successfully pasted.\n\nPaste by {uname}**"
    await msg.edit(pasted, reply_markup=InlineKeyboardMarkup(button))

@app.on_message(filters.command(["delgist"], COMMAND_HANDLER) & filters.user(617426792))
async def delete(_, message):
    try:
        ids = message.command[1]
    except IndexError:
        return await message.reply_text(f"**/{message.command[0]} GIST_ID**",
                                        quote=True)

    try:
        result = Github_Gist.delete(ids)
    except Exception as e:
        result = str(e)

    return await message.reply_text(result)
