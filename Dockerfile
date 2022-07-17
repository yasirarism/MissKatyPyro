FROM python:3.10-slim-buster

RUN apt update && apt upgrade -y
RUN apt install git -y && apt install mediainfo -y && apt install ffmpeg -y

RUN pip3 install -r requirements.txt
CMD ["python3 -m bot"]
