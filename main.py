import os

import time

import subprocess
import requests

import threading

from dotenv import load_dotenv

from tgbot import TgBot

def get_site_status(
        url: str, 
        restart_script_path: str,
        tg_chat_id: str,
        tg_bot_token: str
        ):
    response = requests.get(url)
    if response.status_code in [504, 500]:
        if response.status_code == 500:
            alert_message = "slp упал со статусом 500, пробую рестарнуть.."
        else:
            alert_message = "slp упал со статусом 504, произвожу рестарт..."
        TgBot.send_message(
            chat_id=tg_chat_id,
            bot_token=tg_bot_token,
            message_text = alert_message
        )
        subprocess.call([restart_script_path])


def site_status_monitoring(
        url: str, 
        restart_script_path: str,
        tg_chat_id: str,
        tg_bot_token: str
    ):
    while True:
        get_site_status(url, restart_script_path, tg_chat_id, tg_bot_token)
        time.sleep(60*15)

def main():
    load_dotenv()
    url = os.getenv('url')
    restart_script_path = os.getenv('restart_script_path')
    tg_chat_id = os.getenv("tg_chat_id")
    tg_bot_token = os.getenv("tg_bot_token")
    threading.Thread(
        target=site_status_monitoring, 
        args=(
            url, restart_script_path, tg_chat_id, tg_bot_token,
            )
        ).start()

if __name__ == "__main__":
    main()
