import requests
import configtest

def send_telegram_message(text):
    bot_token = configtest.TelegramBotToken  # retrieve Telegram Bot Token from secret manager
    chat_id = configtest.TelegramChatId  # retrieve Telegram Chat ID from secret manager

    max_chars = 4096
    for i in range(0, len(text), max_chars):
        chunk = text[i:i+max_chars]
        send_message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(send_message_url, data={"chat_id": chat_id, "text": chunk})
