from subprocess import run as srun 
import logging, os

LOGGER = logging.getLogger(__name__)

UPSTREAM_REPO_URL = os.environ.get("UPSTREAM_REPO_URL", "")
if len(UPSTREAM_REPO_URL) == 0:
   UPSTREAM_REPO_URL = None

UPSTREAM_REPO_BRANCH = os.environ.get("UPSTREAM_REPO_BRANCH", "")
if len(UPSTREAM_REPO_BRANCH) == 0:
    UPSTREAM_REPO_BRANCH = "master"

if UPSTREAM_REPO_URL is not None:
    if os.path.exists('.git'):
        srun(["rm", "-rf", ".git"])

    update = srun([f"git init -q \
                     && git config --global user.email mail@yasir.eu.org \
                     && git config --global user.name yasirarism \
                     && git add . \
                     && git commit -sm update -q \
                     && git remote add origin {UPSTREAM_REPO_URL} \
                     && git fetch origin -q \
                     && git reset --hard origin/{UPSTREAM_REPO_BRANCH} -q"], shell=True)

    if update.returncode == 0:
        LOGGER.error('Successfully updated with latest commit from UPSTREAM_REPO')
    else:
        LOGGER.error('Something went wrong while updating, check UPSTREAM_REPO if valid or not!')