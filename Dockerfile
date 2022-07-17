FROM python:3.10-slim-buster

RUN apt update -y
RUN apt install mediainfo neofetch ffmpeg -y
WORKDIR /MissKaty
RUN chmod 777 /MissKaty

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["bash", "start.sh"]
