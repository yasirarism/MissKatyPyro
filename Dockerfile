FROM alpine:latest

LABEL maintainer "mail@yasir.eu.org"
LABEL org.opencontainers.image.description "MissKaty-Docker"

WORKDIR /MissKaty
RUN chmod 777 /MissKaty

ENV TZ="Asia/Jakarta"
RUN apk update && apk add --no-cache mediainfo neofetch ffmpeg git python3-pip -y
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python3", "-m", "bot"]
