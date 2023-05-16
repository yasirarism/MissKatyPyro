<p align="center">
<img src="https://repository-images.githubusercontent.com/433350689/26cb713b-43c3-4dec-94cb-6c80599547e8" width="200" height="200"/>
</p>
<p align="center">
  <a href="#"><img src="http://readme-typing-svg.herokuapp.com?color=d1fa02&center=true&vCenter=true&multiline=false&lines=Welcome+To+MissKaty+Repository" alt="">
</p>
<p align="center">
<a href="#"><img title="Creator" src="https://img.shields.io/badge/Creator-MissKaty-red.svg?style=for-the-badge&logo=github"></a>
</p>
<p align="center">
<a href="https://github.com/yasirarism?tab=followers"><img title="Followers" src="https://img.shields.io/github/followers/yasirarism?color=green&style=flat-square"></a>
<a href="https://github.com/yasirarism/MissKatyPyro/stargazers/"><img title="Stars" src="https://img.shields.io/github/stars/yasirarism/MissKatyPyro?color=white&style=flat-square"></a>
<a href="https://github.com/yasirarism/MissKatyPyro/network/members"><img title="Forks" src="https://img.shields.io/github/forks/yasirarism/MissKatyPyro?color=yellow&style=flat-square"></a>
<a href="https://github.com/yasirarism/MissKatyPyro/watchers"><img title="Watching" src="https://img.shields.io/github/watchers/yasirarism/MissKatyPyro?label=Watchers&color=red&style=flat-square"></a>
<a href="https://github.com/yasirarism/MissKatyPyro"><img title="Open Source" src="https://badges.frapsoft.com/os/v2/open-source.svg?v=103"></a>
<a href="https://github.com/yasirarism/MissKatyPyro/"><img title="Size" src="https://img.shields.io/github/repo-size/yasirarism/MissKatyPyro?style=flat-square&color=darkred"></a>
<a href="https://hits.seeyoufarm.com"><img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fyasirarism%2FMissKatyPyro%2Fhit-counter&count_bg=%2379C83D&title_bg=%23555555&icon=probot.svg&icon_color=%2304FF00&title=hits&edge_flat=false"/></a>
<a href="https://github.com/yasirarism/MissKatyPyro/graphs/commit-activity"><img height="20" src="https://img.shields.io/badge/Maintained-Yes-green.svg"></a>&nbsp;&nbsp;
</p>

## FRAMEWORK & TOOLS THAT USED IN THIS CODE
 🌱 PyroFork v2.x.x (Fork of Pyrogram with Topics Support and Some Patch)<br>
 🌱 Python 3.11<br>
 🌱 MongoDB as Database<br>
 🌱 PyKeyboard for Building Pagination<br>
 🌱 VS Code<br>

## NOTES
If you want help me fixing some error in my bot, you can make pull request to this repo. I'm very glad if you can help me.

## Demo
You can check demo this repo in this bot [MissKatyPyro](https://t.me/MissKatyRoBot)

## Features and Give Support

| FEATURE MY BOT |🌱|
| ------------- | ------------- |
| Basic Admin Feature |✔️|
| AFK Feature |✔️|
| Downloader FB, TikTok and YT-DLP Support  |✔️|
| MultiLanguage Support (Still Beta) |⚠️|
| NightMode  |✔️|
| ChatBot based on OpenAI |✔️|
| MissKaty Mata |✔️|
| Inline Search  |✔️|
| Sticker Tools  |✔️|
| PasteBin Tools  |✔️|
| WebScraper (Pahe, MelongMovie, LK21, Terbit21, Kusonime, etc)  |✔️|
| IMDB Search With Multi Language Per User |✔️|
| GenSS From Media and MediaInfo Generator |✔️|
| And Many More.. |✔️|

* Please open this web https://yasirpedia.eu.org/ to know about me or support me.

## Variables

### Required Variables
* `BOT_TOKEN`: Create a bot using [@BotFather](https://t.me/BotFather), and get the Telegram API token.
* `API_ID`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `API_HASH`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `DATABASE_URI`: [mongoDB](https://www.mongodb.com) URI. Get this value from [mongoDB](https://www.mongodb.com). For more help watch this [video](https://youtu.be/1G1XwEOnxxo)
* `LOG_CHANNEL` : A channel to log the activities of bot. Make sure bot is an admin in the channel.

### Optional Variables
* `USER_SESSION` : Session string for Userbot.
* `DATABASE_NAME`: Name of the database in MongoDB
* `COMMAND_HANDLER`: List of handler bot command splitted by space. Ex: `. !` > so bot will respond with `.cmd` or `!cmd`
* `SUDO`: User ID that have access to bot, split by space
* `OPENAI_API`: Get it from OpenAI Web
* `CURRENCY_API`: Get API Key from https://app.exchangerate-api.com/sign-up

## Deploy (Recommended using Docker/Docker Compose)

#### Build And Run Using Legacy Method
- Make sure minimum python version is 3.8 to prevent some errors. Check it with this command:
```
python3 --version
```
- Install all dependency that needed bot to run. *(need root access, you can skip this if your server didn't have root access but some plugins will not work)*
```
apt update -y & apt install libjpeg-dev zlib1g-dev libwebp-dev python3-pip python3-lxml git wget curl ffmpeg locales tzdata neofetch mediainfo speedtest-cli -y
```
- Install requirements.txt, if using python 3.11, you need pass `--break-system-packages` parameter or use venv when install.<br/>
*Python < 3.10*
```
pip3 install -r requirements.txt
```
*Python 3.11*
```
pip3 install -r requirements.txt --break-system-packages
```
- Setting your config.env or via environment. Make sure you fill all required env.
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


## Thanks to 
 - Thanks To Allah Swt.
 - Thanks To Dan For His Awesome [Library](https://github.com/pyrogram/pyrogram).
 - Thanks To [The Hamker Cat](https://github.com/TheHamkerCat) For WilliamButcher Code.
 - Thanks To [Team Yukki](https://github.com/TeamYukki) For AFK Bot Code.
 - Thanks To [Wrench](https://github.com/EverythingSuckz) For Some Code.
 - Thanks To [AmanoTeam](https://github.com/AmanoTeam) For MultiLanguage Template.
 - And All People Who Help Me In My Life...
 If your code used in this repo and want to give credit please open issue..

## Disclaimer
[![GNU Affero General Public License 2.0](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.en.html#header)    
Licensed under [GNU AGPL 2.0.](https://github.com/yasirarism/MissKatyPyro/blob/master/LICENSE)
WARNING: Selling The Codes To Other People For Money Is *Strictly Prohibited*. God always sees you.
PERINGATAN: Dilarang memperjualbelikan script ini tanpa seijin pembuat script.
