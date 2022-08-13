from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def homepage():
    return "<h1>See mirror-leech-telegram-bot <a href='https://www.github.com/anasty17/mirror-leech-telegram-bot'>@GitHub</a> By <a href='https://github.com/anasty17'>Anas</a></h1>"


if __name__ == "__main__":
    app.run()