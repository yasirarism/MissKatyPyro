import json
import re

from .http import fetch


def html_builder(title: str, text: str) -> str:
    """
    Make proper html with css from given content.
    """

    heading = "<span class='container heading'><b>{content}</b></span>"
    subheading = "<span class='container subheading'><b>{content}</b></span>"
    infobox = "<span class='container infobox'>"
    subtitlebox = "<span class='container subtitlebox'>"
    icon = "<img class='icons' src={icon_url} width='35px' height='35px' alt='' >"
    html_msg = f"<body>{heading.format(content=title)}"

    for line in text.splitlines():
        if ":" not in line and bool(line):
            if "Text #" in line:
                if bool(re.search("Text #1$", line)):
                    subtitle_count = len(re.findall("Text #", text))
                    html_msg += icon.format(
                        icon_url="https://te.legra.ph/file/9d4a676445544d0f2d6db.png"
                    )
                    html_msg += subheading.format(
                        content=f"Subtitles ({subtitle_count} subtitle)"
                    )
                    html_msg += "<span  style='padding: 10px 0vw;'  class='subtitle'>"

            elif "General" in line:
                html_msg += icon.format(
                    icon_url="https://te.legra.ph/file/638fb0416f2600e7c5aa3.png"
                )
                html_msg += subheading.format(content="General")

            elif "Video" in line:
                html_msg += icon.format(
                    icon_url="https://te.legra.ph/file/fbc30d71cf71c9a54e59d.png"
                )
                html_msg += subheading.format(content="Video")

            elif "Audio" in line:
                html_msg += icon.format(
                    icon_url="https://te.legra.ph/file/a3c431be457fedbae2286.png"
                )
                html_msg += subheading.format(content=f"{line.strip()}")

            elif "Menu" in line:
                html_msg += "</span>"
                html_msg += icon.format(
                    icon_url="https://te.legra.ph/file/3023b0c2bc202ec9d6d0d.png"
                )
                html_msg += subheading.format(content="Chapters")

            else:
                html_msg += subheading.format(content=f"{line.strip()}")
            html_msg += subtitlebox if "Text #" in line else infobox

        elif ":" in line:
            if "Attachments" not in line and "ErrorDetectionType" not in line:
                html_msg += f"<div><code>{line.strip()}</code></div>"

        else:
            html_msg += "</span>"

    html_msg += "</span>"
    return html_msg


async def mediainfo_paste(text: str, title: str) -> str:
    html_content = html_builder(title, text)
    URL = "https://yasirr.eu.org/mediainfo"
    response = await fetch.post(URL, data={"content": html_content})
    return (
        f"https://yasirr.eu.org/mediainfo-{json.loads(response.content)['key']}"
    )
