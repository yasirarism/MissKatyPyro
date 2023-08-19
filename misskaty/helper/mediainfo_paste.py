css = """
<style>
@font-face {
font-family: 'JetBrainsMono';
src: url('https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono/web/woff2/JetBrainsMono-Regular.woff2') format('woff2'),
url('https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono/web/woff/JetBrainsMono-Regular.woff') format('woff'),
url('https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono/ttf/JetBrainsMono-Regular.ttf') format('truetype');
font-weight: 400;
font-style: normal;
}
.loader-pulse {
  position: relative;
  bottom: 0.17rem;
  width: 25px;
  height: 25px;
  float: left;
  border-radius: 50%;
  background: #50fa7b;
  animation: load-pulse 1s infinite linear;
}
@keyframes load-pulse {
  0% {
    transform: scale(0.05);
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    transform: scale(0.5);
    opacity: 0;
  }
}
::-webkit-scrollbar {
    width: 3px;
    height: 3px;
}
::-webkit-scrollbar-corner ,
::-webkit-scrollbar-track {
    display: none;
}
::-webkit-scrollbar-thumb {
    border-radius: 8px;
    background-color: #50fa7b;
}
body {
background-color: #282a36;
font-family:  "Josefin Sans", sans-serif;
color: #f8f8f2;
overscroll-behaviour: contain;
}
code {
font-family: "Ubuntu mono", "Courier prime";
}
.container {
display: flex;
flex-direction: column;
}
.container.heading {
display: block;
text-align: center;
line-height: 20px;
flex-direction: column;
margin: auto;
margin-bottom: 50px;
padding: 20px 20px 20px 20px;
font-size: 1rem;
overflow: scroll;
background-color: rgba(255, 255, 255, 0.1);
border-radius: 7px;
border-style: dashed;
font-family: "Ubuntu mono", "Courier prime";
border: 2px solid rgba(255, 255, 255, 0.1);
}
.container.heading::-webkit-scrollbar {
display: none;
}
.container.subheading {
margin-left: 15px;
margin-bottom:15px;
padding-top: 10px; 
font-size: 1.4rem;
}
.container.infobox {
margin-bottom: 40px;
margin-left: 12px;
margin-right: 12px;
  
border-radius: 10px;
background:  rgba(255, 255, 255, 0.1);        
border: 2.5px solid rgba(255, 255, 255, 0.1);
padding: 10px 15px 15px 10px;
white-space: pre ;
overflow: scroll;
font-size: 0.9rem;
}
.subtitle {
display: grid;
grid-auto-flow: column;
grid-auto-columns:320px;
overflow-x: auto;
overscroll-behaviour-inline: contain;
margin-bottom: 40px;
margin-left: 7px;
margin-top: 12px;
}
.subtitle::-webkit-scrollbar {
display: none;
}
.container.subtitlebox {
margin-left: 5px;
margin-right: 15px;
margin-bottom: 0px;
border-radius: 10px; 
background: rgba(255, 255, 255, 0.1);          
border: 3px solid rgba(255, 255, 255, 0.1);
padding: 15px 15px 15px 10px;
white-space: nowrap;
overflow: scroll;
font-size: 0.9rem;
}
.icons {
float: left;
margin-left: 15px;
margin-right: 5px;
}
.footer {
position: fixed;
bottom: 0;
right: 0;
left: 0;
height: 32px;
width: 100%;
font-family: JetBrainsMono;
background-color: #212121;
}
.footer-text{
display: block;
justify-content: space-between;
font-size: 0.9rem;
padding-left: 0.7rem;
padding-right: 1.5rem;
padding-top: 0.25rem;
}
</style>
</head>
"""

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
    return css + html_msg


async def mediainfo_paste(text: str, title: str) -> str:
    html_content = html_builder(title, text)
    URL = "https://mediainfo-1-y5870653.deta.app/api"
    response = await fetch.post(URL, json={"content": html_content})
    return (
        f"https://mediainfo-1-y5870653.deta.app/{json.loads(response.content)['key']}"
    )
