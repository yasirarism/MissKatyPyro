from flask import Flask, request
from bot import app, user

web = Flask(__name__)


@web.route('/')
async def homepage():
    return "Hai guys.."


@web.route('/me')
async def me():
    return str(await user.get_me())


if __name__ == "__main__":
    web.run()