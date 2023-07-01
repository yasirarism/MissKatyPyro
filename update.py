import logging
import os
import sys
from subprocess import run as srun

import requests
from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)

CONFIG_FILE_URL = os.environ.get("CONFIG_FILE_URL", "")
if len(CONFIG_FILE_URL) != 0:
    try:
        res = requests.get(CONFIG_FILE_URL)
        if res.status_code == 200:
            with open("config.env", "wb+") as c:
                c.write(res.content)
                LOGGER.info("Config env has successfully writed")
        else:
            LOGGER.info(
                f"config.env error: {res.status_code}\nMake sure ur config.env found in workdir, will continuing with config.env on workdir"
            )
    except Exception as e:
        LOGGER.error(f"Something wrong while downloading config.env > {str(e)}")
        sys.exit(0)

load_dotenv("config.env", override=True)

UPSTREAM_REPO_URL = os.environ.get("UPSTREAM_REPO_URL", "")
if len(UPSTREAM_REPO_URL) == 0:
    UPSTREAM_REPO_URL = None

UPSTREAM_REPO_BRANCH = os.environ.get("UPSTREAM_REPO_BRANCH", "")
if len(UPSTREAM_REPO_BRANCH) == 0:
    UPSTREAM_REPO_BRANCH = "master"

if UPSTREAM_REPO_URL is not None and UPSTREAM_REPO_BRANCH is not None:
    if os.path.exists(".git"):
        srun(["rm", "-rf", ".git"])
    update = srun(
        [
            f"git init -q \
                     && git config --global user.email mail@yasir.eu.org \
                     && git config --global user.name YasirArisM \
                     && git add . \
                     && git commit -sm update -q \
                     && git remote add origin {UPSTREAM_REPO_URL} \
                     && git fetch origin -q \
                     && git reset --hard origin/{UPSTREAM_REPO_BRANCH} -q"
        ],
        shell=True,
    )
    if update.returncode == 0:
        logging.info(
            f"Successfully updated with latest commit branch > {UPSTREAM_REPO_BRANCH}"
        )
    else:
        logging.error(
            f"Something went wrong while updating, check UPSTREAM_REPO_URL if valid or not! return code: {update.returncode}"
        )
        sys.exit(1)
