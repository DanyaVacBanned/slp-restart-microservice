import logging
import os

import time

import subprocess
import requests

from dotenv import load_dotenv

from tgbot import TgBot

logging.basicConfig(
    level=logging.ERROR, 
    filename="latest.log", 
    filemode="a", 
    format="%(asctime)s %(levelname)s %(message)s"
)

def get_site_status(
        url: str, 
        restart_script_path: str,
        tg_chat_id: str,
        tg_bot_token: str
        ):
    response = requests.get(url)
    if response.status_code in [504, 500]:
        try:
            if response.status_code == 500:
                alert_message = "slp упал со статусом 500, пробую рестарnтнуть.."
            else:
                alert_message = "slp упал со статусом 504, произвожу рестарт..."
            TgBot.send_message(
                chat_id=tg_chat_id,
                bot_token=tg_bot_token,
                message_text = alert_message
            )
            subprocess.Popen(["bash -c " + restart_script_path], shell=True, stdout=subprocess.PIPE)
            time.sleep(60)
            second_response = requests.get(url)
            if second_response.status_code == 200:

                TgBot.send_message(
                    chat_id=tg_chat_id,
                    bot_token=tg_bot_token,
                    message_text=f"Рестарт прошёл успешно"
                )
            else:
                TgBot.send_message(
                    chat_id=tg_chat_id,
                    bot_token=tg_bot_token,
                    message_text=f"Рестарт не помог, собираю логи"
                )
                app_output = subprocess.run(['docker', 'logs', 'app'], stdout=subprocess.PIPE)
                time.sleep(5)
                nginx_output = subprocess.run(['docker', 'logs', 'nginx'], stdout=subprocess.PIPE)
                TgBot.send_message(
                    chat_id=tg_chat_id,
                    bot_token=tg_bot_token,
                    message_text=f"Логи приложения:\n{app_output.stdout.decode('utf-8')}"  
                )
                TgBot.send_message(
                    chat_id=tg_chat_id,
                    bot_token=tg_bot_token,
                    message_text=f"Логи Nginx:\n{nginx_output.stdout.decode('utf-8')}"  
                )
        except Exception as ex:
            TgBot.send_message(
                chat_id=tg_chat_id,
                bot_token=tg_bot_token,
                message_text=f"Что-то пошло не так:\n{ex}"
            )
            

def site_status_monitoring(
        url: str, 
        restart_script_path: str,
        tg_chat_id: str,
        tg_bot_token: str
    ):
    while True:
        try:
            get_site_status(url, restart_script_path, tg_chat_id, tg_bot_token)
            time.sleep(60*15)
        except Exception as ex:
            TgBot.send_message(
                chat_id=tg_chat_id,
                bot_token=tg_bot_token,
                message_text=f"Что-то пошло не так:\n{ex}"
            )

def main():
    load_dotenv()
    url = os.getenv('url')
    restart_script_path = os.getenv('restart_script_path')
    tg_chat_id = os.getenv("tg_chat_id")
    tg_bot_token = os.getenv("tg_bot_token")
    site_status_monitoring(url, restart_script_path, tg_chat_id, tg_bot_token)

if __name__ == "__main__":
    main()
