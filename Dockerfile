FROM python:3.9-slim-buster

RUN apt update && apt upgrade -y
RUN apt install ffmpeg -y && apt install mediainfo -y

COPY . /usr/YasirBot
WORKDIR /usr/YasirBot

RUN pip3 install -r requirements.txt

CMD ["python3", "bot.py"]
