from flask import Flask
from threading import Thread #Server runs on separate thread from bot so they both can run at the same time
#keepAlive.py helps bot run on a web server so that the bot itself doesn't shut down to due how replit rules work

app = Flask('')

@app.route('/')
def home():
    return "Hello there! I'm still alive!" #Little message for anyone who somehow decies to visit this web server

def run():
    app.run(host = '0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()