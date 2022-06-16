if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://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@github.com/yasirarism/MissKatyPyro.git /YasirBot
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /YasirBot
fi
cd /YasirBot
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 -m bot
