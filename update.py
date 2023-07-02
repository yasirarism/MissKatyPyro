import logging
import os
import subprocess
import time

import dotenv
import requests
from git import Repo

LOGGER = logging.getLogger(__name__)

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
        subprocess.run(["rm", "-rf", ".git"])

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
    # time.sleep(6)
    # update = subprocess.run(['pip3', 'install', '-U', '-r', 'requirements.txt'])
    # if update.returncode == 0:
    #    LOGGER.info("Successfully update package pip python")
    # else:
    #    LOGGER.warning("Unsuccessfully update package pip python")
else:
    LOGGER.warning(
        "UPSTREAM_REPO_URL or UPSTREAM_REPO_BRANCH is not defined, Skipping auto update"
    )
