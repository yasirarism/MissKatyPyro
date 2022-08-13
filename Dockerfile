FROM python:3.10-slim-buster

RUN apt update -y
RUN apt install mediainfo neofetch mkvtoolnix ffmpeg git -y
COPY requirements.txt /requirements.txt
RUN cd /
RUN pip3 install -U pip && pip3 install -U -r requirements.txt
RUN mkdir /MissKaty
WORKDIR /MissKaty
COPY start.sh /start.sh
CMD ["/bin/bash", "/start.sh"]
