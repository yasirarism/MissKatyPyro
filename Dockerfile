FROM ubuntu:22.04
LABEL maintainer "mail@yasir.eu.org"
LABEL org.opencontainers.image.description "MissKaty-Docker"

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app
ENV DEBIAN_FRONTEND="noninteractive" TZ="Asia/Jakarta"
RUN apt update -y
RUN apt install mediainfo neofetch mkvtoolnix ffmpeg git python3-pip -y
RUN pip3 install -U -r requirements.txt
CMD ["python3", "-m", "bot"]
