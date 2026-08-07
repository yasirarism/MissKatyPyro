# MissKatyPyro
```diff 
- I will not give any support to your fork, so try learn by yourself!! Don't contact me because of your fault.
```

<!--Badges-->
![MIT License][license-shield] ![Repository Size][repository-size-shield] ![Issue Closed][issue-closed-shield]

<!--Project Title Image-->
<p align="center">
  <img src="https://repository-images.githubusercontent.com/433350689/26cb713b-43c3-4dec-94cb-6c80599547e8" width="200" height="200"/>
</p>

<!--Project Buttons-->
 [![Readme in Indonesian][readme-ko-shield]][readme-ko-url] [![View Demo][view-demo-shield]][view-demo-url] [![Report bug][report-bug-shield]][report-bug-url] <!-- [![Request feature][request-feature-shield]][request-feature-url] -->

<!--Table of Contents-->
# Table of Contents
- [[1] About MissKaty](#1-about-misskaty)
- [[2] Framework Tools And Server That Used To Build This Bot](#2-framework-tools-and-server-that-used-to-build-this-bot)
- [[3] Support Creator](#3-donation)
- [[4] Notes](#4-notes)
- [[5] Features](#5-features)
- [[6] Variables](#6-variables)
- [[7] Deploying Tutorial](#7-deploy-recommended-using-dockerdocker-compose)
  - [Build And Run Using Legacy Method](#build-and-run-using-legacy-method)
  - [Build And Run Using Docker](#build-and-run-using-docker)
  - [Build And Run The Docker Image Using docker-compose](#build-and-run-the-docker-image-using-docker-compose)
- [[8] Credits](#8-thanks-to)
- [[9] Disclaimer](#8-disclaimer)
- [[10] Changelog](#10-changelog)

# [1] About MissKaty
*MissKaty* is a Telegram Bot built using Python and the Pyrogram library. Many useful features for us to use. I hope that one day this project will be discontinued, someone will continue or develop it again. I gave the name MissKaty because I like cats, a cute animal that likes to be played with and friendly with humans.

## [2] Framework Tools And Server That Used To Build This Bot
 🌱 KuriGram<br>
 🌱 Python 3.13 Support<br>
 🌱 MongoDB as Database<br>
 🌱 PyKeyboard for Building Pagination<br>
 🌱 VS Code<br>
 🌱 VPS/Server With Root and Docker Support (Recommended)<br>

## [3] Donation and Support
*For Indonesian Only and some supported country:*<br>
 🌱 [QRIS][qris-url]<br>

*For International Payment:*<br>
 🌱 [Paypal][paypal-url]<br>

## [4] Notes
If you want help me fixing some error in my bot, you can make pull request to this repo. I'm very glad if you can help me. You can also give support to me for buying server.

## [5] Features

| FEATURE MY BOT |🌱|
| ------------- | ------------- |
| Basic Admin Feature (ban, kick, mute, warn, promote, purge, dll) |✔️|
| AFK Feature |✔️|
| Downloader FB, TikTok and YT-DLP Support (AVC + AAC output) |✔️|
| YT Search & Quality Picker (resolution, bitrate, codec) |✔️|
| MultiLanguage Support (en-US, id-ID, id-JW, ru-RU) |✔️|
| NightMode  |✔️|
| ChatBot based on OpenAI and Google Bard |✔️|
| MissKaty Mata |✔️|
| Inline Search  |✔️|
| Sticker Tools  |✔️|
| PasteBin Tools  |✔️|
| WebScraper (Pahe, MelongMovie, LK21, Terbit21, Kusonime, etc)  |✔️|
| IMDB Search With Rich Message & Multi Language Per User |✔️|
| GenSS From Media and MediaInfo Generator (Partial Analysis, no full download) |✔️|
| And Many More.. |✔️|

## [6] Variables

### Required Variables
* `BOT_TOKEN`: Create a bot using [@BotFather](https://t.me/BotFather), and get the Telegram API token.
* `API_ID`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `API_HASH`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `DATABASE_URI`: [mongoDB](https://www.mongodb.com) URI. Get this value from [mongoDB](https://www.mongodb.com).
* `LOG_CHANNEL` : A channel to log the activities of bot. Make sure bot is an admin in the channel.

### Optional Variables
* `YT_COOKIES` : Get YT cookies using https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc?pli=1 and save cookies value on github gist. Copy raw url and fill in this vars.
* `USER_SESSION` : Session string for Userbot.
* `DATABASE_NAME`: Name of the database in MongoDB
* `PAYDISINI_KEY`: Api Key PayDisini
* `PAYDISINI_CHANNEL_ID`: Channel ID QRIS paydisini
* `COMMAND_HANDLER`: List of handler bot command splitted by space. Ex: `. !` > so bot will respond with `.cmd` or `!cmd`
* `SUDO`: User ID that have access to bot, split by space
* `OPENAI_API`: Create personal access token from github, and set as this env. Make sure you have access to Github Model.
* `GOOGLEAI_KEY`: Learn how to get api key from this https://ai.google.dev/tutorials/python_quickstart?hl=en.
* `CURRENCY_API`: Get API Key from https://app.exchangerate-api.com/sign-up
* `NINE_ROUTER_API_KEY`: API key for the [9Router](https://9router.yasirweb.eu.org) gateway used by `/ai` and `/ask` chatbot commands (OpenAI-compatible API). **Required for ChatBot plugin.**
* `NINE_ROUTER_BASE_URL`: 9Router base URL. Default `https://9router.yasirweb.eu.org/v1` (optional).
* `NINE_ROUTER_MODEL_AI`: Model used by `/ai`. Default `oc/mimo-v2.5-free` (optional).
* `NINE_ROUTER_MODEL_ASK`: Model used by `/ask` & guest mode. Default `oc/deepseek-v4-flash-free` (optional).

## [7] Tutorial Deploy (Recommended using Docker/Docker Compose)

#### Build And Run Using Legacy Method
- Make sure minimum python version is 3.8 and max python 3.12 to prevent some errors. Check it with this command:
```
python3 --version
```
- Install all dependency that needed bot to run. *(need root access, you can skip this if your server didn't have root access but some plugins will not work)*
```
apt update -y & apt install libjpeg-dev zlib1g-dev libwebp-dev python3-pip python3-lxml git wget curl ffmpeg locales tzdata neofetch mediainfo speedtest-cli -y
```
- Install requirements.txt, if using python => 3.11, you need use venv when install pip package.<br/>
*Python < 3.10*
```
pip3 install -r requirements.txt
```
*Python => 3.11*
```
python3 -m venv nama_venv
source nama_venv/bin/activate
pip3 install -r requirements.txt 
```
- Setting your config.env or via environment and dont forget fill all required value.
- Run Bot
```
bash start.sh
```

#### Build And Run Using Docker

- Start Docker daemon (Skip if already running):
```
sudo dockerd
```
- Build Docker image:
```
sudo docker build . -t misskaty
```
- Run the image:
```
sudo docker run misskaty
```
- To stop the image:
```
sudo docker ps
sudo docker stop <pid>
```

#### Build And Run The Docker Image Using docker-compose

- Install docker-compose
```
sudo apt install docker-compose
```
- Build and run Docker image or to view current running image:
```
sudo docker-compose up
```
- After editing files with nano for example (nano start.sh):
```
sudo docker-compose up --build
```
- To stop the running image:
```
sudo docker ps
```
```
sudo docker-compose stop <pid>
```

----


## [8] Thanks to 
 - Thanks To Allah Swt.
 - Thanks To Dan For [Pyrogram Library](https://github.com/pyrogram/pyrogram) as founder of pyrogram.
 - Thanks To Mayuri For [Pyrofork Library](https://github.com/Mayuri-Chan) as owner of pyrofork library.
 - Thanks To TeamDrivecok and SecretGroup TBK in Telegram.
 - Thanks To [The Hamker Cat](https://github.com/TheHamkerCat) For WilliamButcher Code.
 - Thanks To [Team Yukki](https://github.com/TeamYukki) For AFK Bot Code.
 - Thanks To [Wrench](https://github.com/EverythingSuckz) For Some Code.
 - Thanks To [AmanoTeam](https://github.com/AmanoTeam) For MultiLanguage Template.
 - And All People Who Help Me In My Life...
 If your code used in this repo and want to give credit please open issue..

## [9] Disclaimer
[![GNU Affero General Public License 2.0](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.en.html#header)    
Licensed under [GNU AGPL 2.0.](https://github.com/yasirarism/MissKatyPyro/blob/master/LICENSE)
WARNING: Selling The Codes To Other People For Money Is *Strictly Prohibited*. Or i will stop this project forever.

## [10] Changelog

### v2.17.0 (2026-08-07)
Built on top of the **Kurigram** fork (`KurimuzonAkuma/pyrogram`), which adds rich-message support (`InputRichMessage`, `rich_message` on send/edit) and `Client.get_file` with offset/limit for partial downloads.

**Refactor & performance**
- Moved root-level `utils.py` and `web/webserver.py` into the `misskaty` package (`helper/`, `core/`) so everything lives under one package.
- Single shared MongoDB connection (singleton + lazy init) instead of multiple `AsyncMongoClient` instances; removed circular imports between `database` and `misskaty`.
- Bootstrapping moved to `misskaty/core/bootstrap.py`; yt-dlp cookies are fetched asynchronously at startup (no more blocking `requests.get` on import).

**IMDb**
- Results are now delivered as **rich messages via edit** (`edit_message_text` + `rich_message`) instead of delete-then-send.
- Merged duplicated `imdbres_id`/`imdbres_en` callbacks into one builder with per-locale labels; fixed hidden-layout fields and mixed-language labels.

**Admin**
- Fixed real bugs (`contextlib` missing import, `FloodWait e.x`, `time_converter` returning a `Message`, wrong locale key) and hardened edge cases (channel replies, deleted accounts, missing `from_user`).
- Messages restyled with emoji + separators in all 4 locales.

**YT-DLP**
- Progress no longer jumps backwards on merged formats; shows elapsed time, ETA, speed and a monospace progress bar; detects the "Finalizing" phase.
- Captions use monospace blocks and mention the requester; title whitespace is normalized (no more double line breaks).
- `/ytdown` now requires a URL argument or a replied message containing a URL.
- Video output prefers **H.264 (AVC) video + AAC audio** (fallback to best available), audio extraction uses AAC.

**MediaInfo**
- **Partial analysis**: only the first/last 8 MiB are downloaded (`upload.getFile` offset/limit), so 2–4 GB files are analyzed in seconds; falls back to a full download automatically when the partial result is incomplete.

### v2.16.1 (previous)
- Fix: use plain emoji on nightmode button (premium-safe).

<!--Url for Badges-->
[license-shield]: https://img.shields.io/github/license/yasirarism/MissKatyPyro?labelColor=D8D8D8&color=04B4AE
[repository-size-shield]: https://img.shields.io/github/repo-size/yasirarism/MissKatyPyro?labelColor=D8D8D8&color=BE81F7
[issue-closed-shield]: https://img.shields.io/github/issues-closed/yasirarism/MissKatyPyro?labelColor=D8D8D8&color=FE9A2E

<!--Url for Buttons-->
[readme-ko-shield]: https://img.shields.io/badge/-readme%20in%20Indonesian-2E2E2E?style=for-the-badge
[view-demo-shield]: https://img.shields.io/badge/-%F0%9F%98%8E%20view%20demo-F3F781?style=for-the-badge
[view-demo-url]: https://t.me/MissKatyBot
[report-bug-shield]: https://img.shields.io/badge/-%F0%9F%90%9E%20report%20bug-F5A9A9?style=for-the-badge
[report-bug-url]: https://github.com/yasirarism/MissKatyPyro/issues
[request-feature-shield]: https://img.shields.io/badge/-%E2%9C%A8%20request%20feature-A9D0F5?style=for-the-badge
[request-feature-url]: https://github.com/yasirarism/MissKatyPyro/issues

<!--URLS-->
[readme-ko-url]: README.id.md
[kofi-url]: https://ko-fi.com/yasirarism
[paypal-url]: https://paypal.me/yasirarism
[qris-url]: https://img.yasirweb.eu.org/file/ee74ce527fb8264b54691.jpg
[mayar]: https://yasirarism.mayar.link/payme
[sociabuzz-url]: https://sociabuzz.com/yasirarism/tribe
[saweria-url]: https://saweria.co/yasirarism
[trakteer-url]: https://trakteer.id/yasir-aris-sp7cn

