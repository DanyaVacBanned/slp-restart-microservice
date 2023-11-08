import requests


class TgBot:

    @classmethod
    def send_message(cls, message_text: str, chat_id: str, bot_token: str):
        method = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message_text}"
        requests.get(method)
