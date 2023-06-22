# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2022-12-01 09:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved

# Base Docker Using Ubuntu 23.04, Python 3.11 and Built In Pip
FROM yasirarism/misskaty-docker:latest

# Set Hostname
ENV HOSTNAME misskaty
# Copy Files
COPY . .
# Set CMD Bot
CMD ["bash", "start.sh"]