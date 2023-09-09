import os
import subprocess
from logging import INFO, StreamHandler, basicConfig, getLogger, handlers

import dotenv
import requests
from git import Repo

if os.path.exists("MissKatyLogs.txt"):
    with open("MissKatyLogs.txt", "r+") as f:
        f.truncate(0)

basicConfig(
    level=INFO,
    format="[%(levelname)s] - [%(asctime)s - %(name)s - %(message)s] -> [%(module)s:%(lineno)d]",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        handlers.RotatingFileHandler("MissKatyLogs.txt", mode="w+", maxBytes=5242880, backupCount=1),
        StreamHandler(),
    ],
)

LOGGER = getLogger("MissKaty")

ENV_URL = os.environ.get("ENV_URL")
try:
    if len(ENV_URL) == 0:
        raise TypeError
    try:
        res = requests.get(ENV_URL)
        if res.status_code == 200:
            with open("config.env", "wb+") as f:
                f.write(res.content)
        else:
            LOGGER.error(f"config.env err: {res.status_code}")
    except Exception as e:
        LOGGER.error(f"ENV_URL: {e}")
except:
    pass

dotenv.load_dotenv("config.env", override=True)

UPSTREAM_REPO_URL = os.environ.get("UPSTREAM_REPO_URL")
UPSTREAM_REPO_BRANCH = os.environ.get("UPSTREAM_REPO_BRANCH")

if all([UPSTREAM_REPO_URL, UPSTREAM_REPO_BRANCH]):
    if os.path.exists(".git"):
        subprocess.run(["rm", "-rf", ".git"], check=True)

    try:
        repo = Repo.init()
        origin = repo.create_remote("upstream", UPSTREAM_REPO_URL)
        origin.fetch()
        repo.create_head(UPSTREAM_REPO_BRANCH, origin.refs[UPSTREAM_REPO_BRANCH])
        repo.heads[UPSTREAM_REPO_BRANCH].set_tracking_branch(
            origin.refs[UPSTREAM_REPO_BRANCH]
        )
        repo.heads[UPSTREAM_REPO_BRANCH].checkout(True)
        ups_rem = repo.remote("upstream")
        ups_rem.fetch(UPSTREAM_REPO_BRANCH)
        LOGGER.info(f"Successfully update with latest branch > {UPSTREAM_REPO_BRANCH}")
    except Exception as e:
        LOGGER.error(e)
        pass
else:
    LOGGER.warning(
        "UPSTREAM_REPO_URL or UPSTREAM_REPO_BRANCH is not defined, Skipping auto update"
    )
