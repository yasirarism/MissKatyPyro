from bot import web, app
import threading


@web.route("/")
def hello_world():
    return str(app.get_me())


threading.Thread(target=web.run, daemon=True).start()