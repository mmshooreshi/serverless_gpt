# -*- coding: utf-8 -*-

import logging

import telegram, os
from flask import Flask, request
from telegram.ext import Dispatcher, MessageHandler, Filters



#################
import openai
	
openai.api_key = os.getenv("OPENAI_API_KEY") 


chat_language = os.getenv("INIT_LANGUAGE", default = "fa") 
	
MSG_LIST_LIMIT = int(os.getenv("MSG_LIST_LIMIT", default = 20))
LANGUAGE_TABLE = {
	  "zh": "哈囉！",
	  "en": "Hello!",
      "jp": "こんにちは",
      "fa": "درود!"
	}

context="""
You are a flirtatious and humorous assistant. Your task is to use creative and funny Persian language expressions and phrases to engage in a conversation and to answer questions. Make sure to be alluring and tantalizing, while using seductive language and open-ended questions. Show your love and appreciation to the person you are talking to by using literature and poems in Persian language. Make sure to use the most accurate grammar and Persian words, not Arabic words. Be funny, witty, and clever! Make sure to use correct grammar and be as creative as possible while also xpressing your affection to the person you are talking to.
سعی کن از ما استفاده نکنی و به جاش بگی من. سعی کن لحن خیلی محاوره‌ای داشته باشی
مثلا نباید بگی شما خوبید؟ باید بگی تو خوبی؟ یا مثلا نباید وقتی می‌خوای راجع به شخص مقابلت صحبت کنی جمع ببندیش. سعی کن کمترین حد از ضمیر ها رو استفاده کنی و همواره جدا کنی ضمیرها رو. مثلا هیچوقت نگو که که دنبال چه کمکن به جاش بگو اون ها دنبال چه کمکی هستن؟ یا دنبال چه کمکی ان؟ فهمیدی دوست من؟ بوس به کله‌ت پس.
به جای بمانیم و چیز های شبیهش باید بگی بمونیم. به جای خیلی خوشحالم که شنیدم باید بگی خیلی خوشحال شدم از شنیدنش.
به جای شاید حوصله‌ی همه‌ی ما سر برود باید بگویی شاید حوصله‌ی همه‌مون سر بره خب :( 
مراقب باش که شبیه این ها اشتباه نکنی
"""

class Prompts:
    def __init__(self):
        self.msg_list = []        
        self.messages =  [
        {"role": "user", "content": context},
        {"role": "assistant", "content": f"{LANGUAGE_TABLE[chat_language]}"}
        ]
        self.msg_list.append(f"AI:{LANGUAGE_TABLE[chat_language]}")
	    
    def add_msg(self, new_msg):
        if len(self.messages) >= MSG_LIST_LIMIT:
            self.remove_msg()
        self.msg_list.append(new_msg)
	
    def remove_msg(self):
        self.msg_list.pop(0)
	
    def generate_prompt(self):
        return '\n'.join(self.msg_list)	
	
    def update_messages(self,role,content):
        self.messages.append({"role": role, "content": content})
    

class ChatGPT:  
    def __init__(self):
        self.prompt = Prompts()
        self.model = os.getenv("OPENAI_MODEL", default = "text-davinci-003")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default = 0.5))
        self.frequency_penalty = float(os.getenv("OPENAI_FREQUENCY_PENALTY", default = 0))
        self.presence_penalty = float(os.getenv("OPENAI_PRESENCE_PENALTY", default = 0))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default = 250))
	
    def get_response(self):

        response = openai.ChatCompletion.create(
	            model="gpt-3.5-turbo-0301",
                messages=self.prompt.messages,
	            temperature=self.temperature,
	            frequency_penalty=self.frequency_penalty,
	            presence_penalty=self.presence_penalty,
	            max_tokens=self.max_tokens
                )
        self.prompt.update_messages("assistant",response['choices'][0]['message']['content'])
        
        # response = openai.Completion.create(
	    #         model=self.model,
	    #         prompt=self.prompt.generate_prompt(),
	    #         temperature=self.temperature,
	    #         frequency_penalty=self.frequency_penalty,
	    #         presence_penalty=self.presence_penalty,
	    #         max_tokens=self.max_tokens
        #         )
        
        print("ربات")        
        print(response['choices'][0]['message']['content'].strip())

        print("ربات : ")      
        print(response)
        print("\n \n \n",f"{len(self.prompt.messages)}","\n \n \n")
        print("self.prompt.messages: \n \n \n",self.prompt.messages)
        
        return response['choices'][0]['message']['content'].strip()
	
    def add_msg(self, text):
        self.prompt.add_msg(text)






#####################

telegram_bot_token = str(os.getenv("TELEGRAM_BOT_TOKEN"))



# Load data from config.ini file
#config = configparser.ConfigParser()
#config.read('config.ini')

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
    #text = update.message.text
    #update.message.reply_text(text)
    
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    chatgpt.prompt.add_msg(update.message.text) #人類的問題 the question humans asked
    chatgpt.prompt.update_messages("user",update.message.text)

    ai_reply_response = chatgpt.get_response() #ChatGPT產生的回答 the answers that ChatGPT gave
    
    update.message.reply_text(ai_reply_response) #用AI的文字回傳 reply the text that AI made

# New a dispatcher for bot
dispatcher = Dispatcher(bot,None)

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == "__main__":
    # Running server
    app.run(debug=True)