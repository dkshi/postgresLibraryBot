from app import *
from telegram import *
import threading


class FlaskThread(threading.Thread):
    def run(self) -> None:
        app.run(host="127.0.0.1", port=8080)


class TelegramThread(threading.Thread):
    def run(self) -> None:
        bot.polling(none_stop=True)


if __name__ == "__main__":
    flask_thread = FlaskThread()
    bot_thread = TelegramThread()
    flask_thread.start()
    bot_thread.start()