from flask import Flask, request
from bot import app, user

web = Flask(__name__)


@web.route('/')
async def homepage():
    return str(await app.get_me())


if __name__ == "__main__":
    app.start()
    user.start()
    web.run()