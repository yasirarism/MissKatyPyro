FROM alpine:latest

LABEL maintainer "mail@yasir.eu.org"
LABEL org.opencontainers.image.description "MissKaty-Docker"

WORKDIR /MissKaty
RUN chmod 777 /MissKaty

ENV TZ="Asia/Jakarta"
RUN echo -e "\e[32m[INFO]: Installing basic packages.\e[0m" && \
    apk update && apk upgrade && \
    apk add --upgrade --no-cache \
    sudo py3-wheel musl-dev musl python3 \
    python3-dev busybox musl-locales github-cli lshw \
    py3-pip py3-lxml \
    xz curl pv jq ffmpeg parallel \
    neofetch git make g++ gcc automake \
    autoconf mediainfo bash \
    musl-utils tzdata gcompat \
    alpine-sdk libffi-dev py3-virtualenv libffi \
    dpkg cmake
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python3", "-m", "bot"]
