FROM ubuntu:22.04

LABEL maintainer "mail@yasir.eu.org"
LABEL org.opencontainers.image.description "MissKaty-Docker"

WORKDIR /MissKaty
RUN chmod 777 /MissKaty

ENV DEBIAN_FRONTEND="noninteractive" TZ="Asia/Jakarta"
RUN apt update -y
RUN apt install mediainfo neofetch mkvtoolnix ffmpeg git python3-pip -y
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python3", "-m", "bot"]
