if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/EvamariaTG/EvaMaria.git /EvaMaria
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /YasirBot
fi
cd /YasirBot
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 -m bot
