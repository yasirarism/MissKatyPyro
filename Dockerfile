FROM alpine:latest

LABEL maintainer "mail@yasir.eu.org"
LABEL org.opencontainers.image.description "MissKaty-Docker"

# Setup Working Directory
WORKDIR /MissKaty
RUN chmod 777 /MissKaty
ENV TZ="Asia/Jakarta"

# Installing basic packages
RUN apk update && apk upgrade && \
    apk add --update \
    sudo py3-wheel musl-dev musl python3 \
    python3-dev musl-locales lshw \
    py3-pip py3-lxml \
    xz curl pv jq ffmpeg parallel \
    neofetch git make g++ gcc automake \
    autoconf mediainfo bash \
    musl-utils tzdata gcompat \
    alpine-sdk libffi-dev py3-virtualenv libffi \
    dpkg cmake unzip && rm -rf /var/cache/apk/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Setup Language Environments
ENV LANG="en_US.UTF-8" LANGUAGE="en_US:en" LC_ALL="en_US.UTF-8"
RUN echo 'export LC_ALL=en_US.UTF-8' >> /etc/profile.d/locale.sh && \
    sed -i 's|LANG=C.UTF-8|LANG=en_US.UTF-8|' /etc/profile.d/locale.sh && \
    cp /usr/share/zoneinfo/Asia/Jakarta /etc/localtime

COPY . .
CMD ["python3", "-m", "bot"]
