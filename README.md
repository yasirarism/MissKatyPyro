<h1 align="center">
  <p align="center"><img src="https://socialify.git.ci/yasirarism/MissKatyPyro/image?description=1&font=Raleway&forks=1&issues=1&language=1&logo=https%3A%2F%2Fi.ibb.co%2FPrNF7HY%2Fphoto-2022-12-02-22-04-51.jpg&name=1&owner=1&pulls=1&stargazers=1&theme=Dark" alt="Cover Image" width="650"></p>
  <p align="center"><b>MissKaty Bot based on Pyrogram</b></p>
</h1>

## NOTES
This repo has some small bugs and i dont have time to fix it. If you can help me, please open pull request (PR).

## Demo
You can check demo this repo in this bot [MissKatyPyro](https://t.me/MissKatyRoBot)

## Features and Give Support
* Please open this web https://yasirpedia.eu.org/ to know about me or support me.

## Variables

### Required Variables
* `BOT_TOKEN`: Create a bot using [@BotFather](https://t.me/BotFather), and get the Telegram API token.
* `API_ID`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `API_HASH`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `DATABASE_URI`: [mongoDB](https://www.mongodb.com) URI. Get this value from [mongoDB](https://www.mongodb.com). For more help watch this [video](https://youtu.be/1G1XwEOnxxo)
* `DATABASE_NAME`: Name of the database in [mongoDB](https://www.mongodb.com). For more help watch this [video](https://youtu.be/1G1XwEOnxxo)
* `LOG_CHANNEL` : A channel to log the activities of bot. Make sure bot is an admin in the channel.
* `USER_SESSION` : Session string for Userbot.
### Optional Variables
Check by yourself in config files.

## Deploy (Must Use Docker to Run This Bot, since i had make it built in all requirements)

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
```
sudo docker stop <pid>

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
Selling The Codes To Other People For Money Is *Strictly Prohibited*. God always sees you.
