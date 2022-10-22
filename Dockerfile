# Base Docker
FROM ubuntu:22.10

# Setup Working Directory
WORKDIR /MissKaty
RUN chmod 777 /MissKaty

# Installing basic packages
RUN apt-get update -y && apt install python3-pip ffmpeg neofetch mediainfo -y

# Install Requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
# Set CMD Bot
CMD ["python3", "-m", "bot"]
