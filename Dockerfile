# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2022-12-01 09:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved

# Base Docker Using Debian 12 (Bookworm), Python 3.11.4 and Built In Pip
## With Built in Pip Package
FROM yasirarism/misskaty-docker:latest
## Without Built in Pip Package
# FROM yasirarism/misskaty-docker:free

# Set Hostname
ENV HOSTNAME yasir-server
# Copy Files
COPY . .
# Instal pip package
# RUN pip3 install --no-cache-dir -r requirements.txt
# Set CMD Bot
CMD ["bash", "start.sh"]
