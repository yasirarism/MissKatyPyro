import os
import asyncio
from html_telegraph_poster import TelegraphPoster
from typing import Tuple
import shlex


def post_to_telegraph(a_title: str, content: str) -> str:
    """Create a Telegram Post using HTML Content"""
    post_client = TelegraphPoster(use_api=True)
    auth_name = "MissKaty Bot"
    post_client.create_api_token(auth_name)
    post_page = post_client.post(
        title=a_title,
        author=auth_name,
        author_url="https://www.yasir.my.id",
        text=content,
    )
    return post_page["url"]


async def run_subprocess(cmd):
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    return await process.communicate()


async def get_media_info(file_link):
    ffprobe_cmd = [
        "ffprobe",
        "-headers",
        "IAM:''",
        "-i",
        file_link,
        "-v",
        "quiet",
        "-of",
        "json",
        "-show_streams",
        "-show_format",
        "-show_chapters",
        "-show_programs",
    ]
    data, err = await run_subprocess(ffprobe_cmd)
    return data


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """run command in terminal"""
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


# Solves ValueError: No closing quotation by removing ' or " in file name
def safe_filename(path_):
    if path_ is None:
        return
    safename = path_.replace("'", "").replace('"', "")
    if safename != path_:
        os.rename(path_, safename)
    return safename
