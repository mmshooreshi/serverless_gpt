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
from roles import roles
context=roles['helpful_assistant']+"\n\n"+roles['persian_rules']

class Prompts:
    def __init__(self):
        self.msg_list = []        
        self.messages =  [
        {"role": "user", "content": context},
        {"role": "assistant", "content": f"{LANGUAGE_TABLE[chat_language]}"}
        ]

        self.messagesTk= [50,0]

        self.msg_list.append(f"AI:{LANGUAGE_TABLE[chat_language]}")
	    
    def add_msg(self, new_msg):
        if len(self.messages) >= MSG_LIST_LIMIT:
            self.remove_msg()
        self.msg_list.append(new_msg)
	
    def remove_msg(self):
        self.msg_list.pop(0)
	
    def generate_prompt(self):
        return '\n'.join(self.msg_list)	
	
    totalBefore=0
    def update_messages(self, role, content, usage=None):
        self.messages.append({"role": role, "content": content})
        
        if role == "assistant" and usage is not None:
            addedTokens = usage['total_tokens'] - self.messagesTk[-1]
            self.messagesTk.append(addedTokens)
        else:
            self.messagesTk.append(0)

    def shorten(self,prompt_tokens, completion_tokens, total_tokens):
        excessive_tokens_count= total_tokens-4096
        indice_to_remove=[]
        for index, value in enumerate(self.messages):
            if(excessive_tokens_count==0):
                break
            if(index ==0):
                pass
            else:
                if(self.messagesTk[index]/excessive_tokens_count < 1.1):
                    indice_to_remove.append(index)
                    excessive_tokens_count -= self.messagesTk[index]
                else:
                    truncating_position = (self.messagesTk[index] / excessive_tokens_count)*1.3*len(self.messages[index]['content'])
                    excessive_tokens_count = 0
                    self.messages[index]['content'] = self.messages[index]['content'][truncating_position:]
        if(len(indice_to_remove)):
             for i, value in enumerate(indice_to_remove):
                self.messages.pop(value)
                self.messagesTk.pop(value)

        

class ChatGPT:  
    def __init__(self):
        self.prompt = Prompts()
        self.model = os.getenv("OPENAI_MODEL", default = "text-davinci-003")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default = 0.5))
        self.frequency_penalty = float(os.getenv("OPENAI_FREQUENCY_PENALTY", default = 0))
        self.presence_penalty = float(os.getenv("OPENAI_PRESENCE_PENALTY", default = 0))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default = 250))
	
    def get_response(self):

        whileOverride=0
        while(not whileOverride):
            response = openai.ChatCompletion.create(
	                model="gpt-3.5-turbo-0301",
                    messages=self.prompt.messages,
	                temperature=self.temperature,
	                frequency_penalty=self.frequency_penalty,
	                presence_penalty=self.presence_penalty,
	                max_tokens=self.max_tokens
                    )
        
            usage = response['usage']
            content = response['choices'][0]['message']['content']

            if(usage['total_tokens']>4090):
                self.prompt.shorten(usage['prompt_tokens'],usage['completion_tokens'],usage['total_tokens'])
            else:
                whileOverride=1

        self.prompt.update_messages("assistant",content,usage)
        
        # response = openai.Completion.create(
	    #         model=self.model,
	    #         prompt=self.prompt.generate_prompt(),
	    #         temperature=self.temperature,
	    #         frequency_penalty=self.frequency_penalty,
	    #         presence_penalty=self.presence_penalty,
	    #         max_tokens=self.max_tokens
        #         )
        
        print("___________")        
        print(response['choices'][0]['message']['content'].strip())
        print("___________")      

        print("___________")        
        print(response)
        print("___________")        

        print("___________")        

        print("\n \n \n",f"{len(self.prompt.messages)}","\n \n \n")
        print("___________")        
        print("___________")        
        print("self.prompt.messages: \n \n \n",self.prompt.messages)
        print("___________")        
        
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

    ai_reply_response = chatgpt.get_response() 
    breakTxt="\n_____ \n _____\n"
    update.message.reply_text(ai_reply_response + breakTxt+ "\n ".join(chatgpt.prompt.messages)+breakTxt+ "\n ".join(chatgpt.prompt.msg_list)+breakTxt+ "\n ".join(chatgpt.prompt.messagesTk))
    

# New a dispatcher for bot
dispatcher = Dispatcher(bot,None)

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == "__main__":
    # Running server
    app.run(debug=True)