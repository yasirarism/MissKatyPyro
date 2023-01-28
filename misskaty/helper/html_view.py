import base64, json, os
from .tools import get_random_string
from .http import http
from misskaty import GH_TOKEN

hmtl_content = """
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{fileName}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" />
    <link
        href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap"
        rel="stylesheet" />
    <link rel="stylesheet" href="https://pro.fontawesome.com/releases/v5.10.0/css/all.css" />
    <style>
        * {
            font-family: "Ubuntu", sans-serif;
            list-style: none;
            text-decoration: none;
            outline: none !important;
            color: white;
            overflow-wrap: anywhere;
        }
        body {
            background-color: #0D1117;
        }
        .container {
            margin: 0vh 1vw;
            margin-bottom: 1vh;
            padding: 1vh 3vw;
            display: list-item;
            flex-direction: column;
            border: 2px solid rgba(255, 255, 255, 0.11);
            border-radius: 20px;
            background-color: #161b22;
            align-items: center;
        }
        .container.center {
            text-align: center;
        }
        .container.start {
            text-align: start;
        }
        .rfontsize {
            font-size: 1rem;
        }
        .forhover:hover {
            filter: invert(0.3);
        }
        .dlinks {
            margin-top: 2.5vh;
            display: inline-block;
        }
    </style>
</head>
<body>
{msg}
</body>
</html>
"""

html_template = """
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" />
    <link
        href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap"
        rel="stylesheet" />
    <link rel="stylesheet" href="https://pro.fontawesome.com/releases/v5.10.0/css/all.css" />
    <style>
        * {
            font-family: "Ubuntu", sans-serif;
            list-style: none;
            text-decoration: none;
            outline: none !important;
            color: white;
            overflow-wrap: anywhere;
        }
        body {
            background-color: #0D1117;
        }
        .container {
            margin: 0vh 1vw;
            margin-bottom: 1vh;
            padding: 1vh 3vw;
            display: list-item;
            flex-direction: column;
            border: 2px solid rgba(255, 255, 255, 0.11);
            border-radius: 20px;
            background-color: #161b22;
            align-items: center;
        }
        .container.center {
            text-align: center;
        }
        .container.start {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }
        .rfontsize {
            font-size: 1rem;
        }
        .withhover:hover {
            filter: invert(0.3);
        }
        .topmarginxl {
            margin-top: 2.5vh;
            display: inline-block;
        }
        .topmarginsm {
            margin-top: 1vh;
            display: inline-block;
        }
    </style>
</head>
<body>
{msg}
</body>
</html>
"""
async def postToWeb(file, name):
    fpath = base64.b64encode(open(file, "rb").read())

    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {GH_TOKEN}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {"message":"Added new HTML File","committer":{"name":"Yasir Aris M","email":"mail@yasir.eu.org"},"content": f"{fpath.decode('ascii')}"}

    response = await http.put(f"https://api.github.com/repos/yasirarism/HTMLPaste/contents/{name}", headers=headers, data=json.dumps(data))
    return f"https://yasirarism.github.io/HTMLPaste/{name}"

async def getMediaWeb(title, text):
    msg = ""
    fname = get_random_string(7)
    msg += '<span class="container center rfontsize">' \
                          f'<h4>MediaInfo From {title}</h4></span>'
    msg += '<span class="container center rfontsize">' \
                          f'<b>MediaInfo</b></span>'
    msg += '<span class="container start rfontsize">' \
                              f"<div>{text}</div></span>"
    with open(f"{fname}.html", 'w', encoding='utf-8') as f:
        f.write(msg)
    res = await postToWeb(f"{fname}.html", fname)
    os.remove(f"{fname}.html")
    return res
