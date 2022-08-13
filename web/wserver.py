from flask import Flask, request
from bot import app

web = Flask(__name__)


@web.route('/')
async def homepage():
    return str(await app.get_me())


if __name__ == "__main__":
    web.run()