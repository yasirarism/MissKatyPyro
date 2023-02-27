import requests
from subprocess import run as srun 
import logging, os, dotenv

LOGGER = logging.getLogger(__name__)

CONFIG_FILE_URL = os.environ.get("CONFIG_FILE_URL", "")
try:
    if len(CONFIG_FILE_URL) == 0:
        raise TypeError
    try:
        res = requests.get(CONFIG_FILE_URL)
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

UPSTREAM_REPO = os.environ.get('UPSTREAM_REPO', '')
if len(UPSTREAM_REPO) == 0:
   UPSTREAM_REPO = None

UPSTREAM_BRANCH = os.environ.get("UPSTREAM_BRANCH", "")
if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = "master"

if UPSTREAM_REPO is not None:
    if os.path.exists('.git'):
        srun(["rm", "-rf", ".git"])

    update = srun([f"git init -q \
                     && git config --global user.email mail@yasir.eu.org \
                     && git config --global user.name yasirarism \
                     && git add . \
                     && git commit -sm update -q \
                     && git remote add origin {UPSTREAM_REPO} \
                     && git fetch origin -q \
                     && git reset --hard origin/{UPSTREAM_BRANCH} -q"], shell=True)

    if update.returncode == 0:
        LOGGER.error('Successfully updated with latest commit from UPSTREAM_REPO')
    else:
        LOGGER.error('Something went wrong while updating, check UPSTREAM_REPO if valid or not!')