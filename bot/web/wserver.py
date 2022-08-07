import threading
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "test"


threading.Thread(target=app.run, daemon=True).start()