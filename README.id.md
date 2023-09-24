# MissKatyPyro

<!--Badges-->
![MIT License][license-shield] ![Repository Size][repository-size-shield] ![Issue Closed][issue-closed-shield]

<!--Project Title Image-->
<p align="center">
  <img src="https://repository-images.githubusercontent.com/433350689/26cb713b-43c3-4dec-94cb-6c80599547e8" width="200" height="200"/>
</p>

<!--Project Buttons-->
 [![Readme in Indonesian][readme-ko-shield]][readme-ko-url] [![View Demo][view-demo-shield]][view-demo-url] [![Report bug][report-bug-shield]][report-bug-url] [![Request feature][request-feature-shield]][request-feature-url]

<!--Table of Contents-->
# Table of Contents
- [[1] About MissKaty](#1-about-misskaty)
- [[2] Framework Tools And Server That Used To Build This Bot](#2-framework-tools-and-server-that-used-to-build-this-bot)
- [[3] Donation](#3-donation)
- [[4] Notes](#4-notes)
- [[5] Features](#5-features)
- [[6] Variables](#6-variables)
- [[7] Deploying Tutorial](#7-deploy-recommended-using-dockerdocker-compose)
  - [Build And Run Using Legacy Method](#build-and-run-using-legacy-method)
  - [Build And Run Using Docker](#build-and-run-using-docker)
  - [Build And Run The Docker Image Using docker-compose](#build-and-run-the-docker-image-using-docker-compose)
- [[8] Credits](#8-thanks-to)
- [[9] Disclaimer](#8-disclaimer)

# [1] About MissKaty
*MissKaty* adalah Bot Telegram yang dibuat menggunakan Python dan library Pyrogram. Banyak fitur yang berguna untuk kita gunakan. Saya berharap suatu saat jika project ini dihentikan, ada yang melanjutkan atau mengembangkannya lagi. Saya memberi nama MissKaty karena saya suka kucing, hewan lucu yang suka bermain dan bersahabat dengan manusia.

## [2] Framework Tools And Server That Used To Build This Bot
 🌱 PyroFork v2.x.x (Fork Pyrogram dengan Dukungan Topik dan Beberapa Patch)<br>
 🌱 Dukungan Python 3.11<br>
 🌱 MongoDB sebagai Database<br>
 🌱 PyKeyboard for Building Pagination<br>
 🌱 VS Code<br>
 🌱 VPS/Server With Docker Support (Recommended)<br>

## [3] Donation
*Khusus Indonesia Saja:*<br>
 🌱 [QRIS][qris-url]<br>

*Untuk Semua Negara:*<br>
 🌱 [Paypal][paypal-url]<br>

## [4] Notes
Jika Anda ingin membantu saya memperbaiki beberapa kesalahan di bot saya, Anda dapat membuat PR ke repo ini. Saya sangat senang jika Anda dapat membantu saya. Anda juga dapat memberikan dukungan kepada saya untuk membeli server.

## [5] Features

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

## [6] Variables

### Variabel yang Diperlukan
* `BOT_TOKEN`: Buat bot menggunakan [@BotFather](https://t.me/BotFather), dan dapatkan token Telegram API.
* `API_ID`: Dapatkan value ini dari [telegram.org](https://my.telegram.org/apps)
* `API_HASH`: Dapatkan value ini dari [telegram.org](https://my.telegram.org/apps)
* `DATABASE_URI`: [mongoDB](https://www.mongodb.com) URI. Dapatkan value ini dari [mongoDB](https://www.mongodb.com). Untuk bantuan lebih lanjut, tonton [video] ini(https://youtu.be/1G1XwEOnxxo)
* `LOG_CHANNEL` : Channel untuk mencatat aktivitas bot. Pastikan bot adalah admin di channel.

### Variabel Opsional
* `USER_SESSION` : String session untuk Userbot.
* `DATABASE_NAME`: Nama database di MongoDB
* `COMMAND_HANDLER`: Daftar perintah handler bot dipisahkan dengan spasi. Contoh: `. !` > jadi bot akan merespon dengan `.cmd` atau `!cmd`
* `SUDO`: User ID yang memiliki akses ke bot, dipisahkan dengan spasi
* `OPENAI_API`: Dapatkan dari Web OpenAI
* `CURRENCY_API`: Dapatkan API Key di https://app.exchangerate-api.com/sign-up

## [7] Tutorial Deploy (Recommended using Docker/Docker Compose)

#### Bangun Dan Jalankan Menggunakan Metode Lama
- Pastikan versi python minimum adalah 3.8 untuk mencegah beberapa error. Periksa dengan perintah ini:
```
python3 --version
```
- Instal semua dependensi yang membutuhkan bot untuk dijalankan. *(memerlukan akses root, Anda dapat melewati ini jika server Anda tidak memiliki akses root tetapi beberapa plugin tidak berfungsi)*
```
apt update -y & apt install libjpeg-dev zlib1g-dev libwebp-dev python3-pip python3-lxml git wget curl lokal ffmpeg tzdata neofetch mediainfo speedtest-cli -y
```
- Instal requirements.txt, jika menggunakan python 3.11, Anda harus menggunakan opsi venv saat menginstal.<br/>
*Python < 3.10*
```
pip3 install -r requirements.txt
```
*Python 3.11*
```
Install venv dari terminal server kamu
pip3 install -r requirements.txt
```
- Atur config environment saat menjalankan bot dan jangan lupa isi semua value yang wajib di isi.
- Jalankan Bot
```
bash start.sh
```

#### Build And Run Using Docker

- Mulai daemon Docker (Lewati jika sudah berjalan):
```
sudo dockerd
```
- Build Docker image:
```
sudo docker build . -t misskaty
```
- Jalankan Docker image:
```
sudo docker run misskaty
```
- Untuk Menghentikan image:
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
 - Terima kasih Kepada Allah Swt.
 - Terima kasih Kepada Dan [Pyrogram Library](https://github.com/pyrogram/pyrogram).
 - Terima kasih Kepada [The Hamker Cat](https://github.com/TheHamkerCat) Untuk Kode WilliamButcher.
 - Terima kasih Kepada [Team Yukki](https://github.com/TeamYukki) Untuk Kode AFK Bot.
 - Terima kasih Kepada [Wrench](https://github.com/EverythingSuckz) Untuk Beberapa Kode.
 - Terima kasih Kepada [AmanoTeam](https://github.com/AmanoTeam) Untuk Template MultiBahasa.
 - Dan Semua Orang Yang Membantuku Dalam Hidupku...
Jika kode Anda digunakan dalam repo ini dan ingin memberikan kredit, silakan buka masalah..

## [9] Disclaimer
[![GNU Affero General Public License 2.0](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.en.html#header)    
Dilisensikan di bawah [GNU AGPL 2.0.](https://github.com/yasirarism/MissKatyPyro/blob/master/LICENSE)
PERINGATAN: Menjual Kode Kepada Orang Lain Demi Uang *Dilarang Keras*. Tuhan selalu melihatmu dimanapun kamu berada.

<!--Url for Badges-->
[license-shield]: https://img.shields.io/github/license/yasirarism/MissKatyPyro?labelColor=D8D8D8&color=04B4AE
[repository-size-shield]: https://img.shields.io/github/repo-size/yasirarism/MissKatyPyro?labelColor=D8D8D8&color=BE81F7
[issue-closed-shield]: https://img.shields.io/github/issues-closed/yasirarism/MissKatyPyro?labelColor=D8D8D8&color=FE9A2E

<!--Url for Buttons-->
[readme-ko-shield]: https://img.shields.io/badge/-readme%20in%20Indonesian-2E2E2E?style=for-the-badge
[view-demo-shield]: https://img.shields.io/badge/-%F0%9F%98%8E%20view%20demo-F3F781?style=for-the-badge
[view-demo-url]: https://t.me/MissKatyPyro
[report-bug-shield]: https://img.shields.io/badge/-%F0%9F%90%9E%20report%20bug-F5A9A9?style=for-the-badge
[report-bug-url]: https://github.com/yasirarism/MissKatyPyro/issues
[request-feature-shield]: https://img.shields.io/badge/-%E2%9C%A8%20request%20feature-A9D0F5?style=for-the-badge
[request-feature-url]: https://github.com/yasirarism/MissKatyPyro/issues

<!--URLS-->
[readme-ko-url]: README.md
[kofi-url]: https://ko-fi.com/yasirarism
[paypal-url]: https://paypal.me/yasirarism
[qris-url]: https://img.yasirweb.eu.org/file/2acf7698f300ef3d9138f.jpg
[sociabuzz-url]: https://sociabuzz.com/yasirarism/tribe
[saweria-url]: https://saweria.co/yasirarism
[trakteer-url]: https://trakteer.id/yasir-aris-sp7cn