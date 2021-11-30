FROM python:3.9-slim-buster

RUN apt update && apt upgrade -y
RUN apt install ffmpeg -y && apt install mediainfo -y
COPY requirements.txt /requirements.txt

RUN cd /
RUN pip3 install -U pip && pip3 install -U -r requirements.txt
RUN mkdir /EvaMaria
WORKDIR /EvaMaria
CMD ["python3", "bot.py"]
