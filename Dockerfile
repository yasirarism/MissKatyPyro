# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2022-12-01 09:12:27
# * @lastModified  2022-12-01 09:27:31
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved

# Base Docker
FROM yasirarism/misskaty-docker:latest

ENV HOSTNAME yasirvps
COPY . .
# Set CMD Bot
CMD ["bash", "start.sh"]
