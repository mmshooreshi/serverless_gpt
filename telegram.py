import os, telegram

class Telegram:
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    def __init__(self,telegram_bot_token):
        self.bot = telegram.Bot(token=telegram_bot_token)
    
    def send_chat_action(self, chat_id, action):
        self.bot.send_chat_action(chat_id=chat_id, action=action)
