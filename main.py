import logging, os
import telegram
from flask import Flask, request
from telegram.ext import Dispatcher, MessageHandler, Filters, CommandHandler
import openai
import telegram
from prompts import Prompts, context, LANGUAGE_TABLE
from chatgpt import ChatGPT
	
openai.api_key = os.getenv("OPENAI_API_KEY") 
chat_language = os.getenv("INIT_LANGUAGE", default = "fa") 
	
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial Flask app
app = Flask(__name__)

# Initial bot by Telegram access token
bot = telegram.Bot(token=telegram_bot_token)
chatgpt = ChatGPT()

@app.route('/callback', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'

def reply_handler(bot, update):
    """Reply message."""
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    chatgpt.prompt.add_msg(update.message.text)
    chatgpt.prompt.update_messages("user", update.message.text)

    ai_reply_response = chatgpt.get_response()

    update.message.reply_text(ai_reply_response)

def clear_handler(bot, update):
    """Clear message."""
    chatgpt.prompt.msg_list = []
    chatgpt.prompt.messages = [
        {"role": "user", "content": context},
        {"role": "assistant", "content": f"{LANGUAGE_TABLE[chat_language]}"}
    ]

    chatgpt.prompt.messagesTk = [50, 0]
    update.message.reply_text('cleared!')

def start_handler(bot, update):
    update.message.reply_text('Hello! I am Chat-GPT, a chatbot powered by OpenAI GPT-3. Input your query and I will answer it.')

# New a dispatcher for bot
dispatcher = Dispatcher(bot, None)

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))
# Add handler for /clear command
dispatcher.add_handler(CommandHandler('clear', clear_handler))

# Add handler for /start command
dispatcher.add_handler(CommandHandler('start', start_handler))

if __name__ == "__main__":
    # Running server
    app.run(debug=True)