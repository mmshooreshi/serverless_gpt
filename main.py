# -*- coding: utf-8 -*-

import logging

import telegram
import os
from flask import Flask, request
from telegram.ext import Dispatcher, MessageHandler, Filters, CommandHandler


#################
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


chat_language = os.getenv("INIT_LANGUAGE", default="fa")

MSG_LIST_LIMIT = int(os.getenv("MSG_LIST_LIMIT", default=20))
LANGUAGE_TABLE = {
    "zh": "哈囉！",
          "en": "Hello!",
    "jp": "こんにちは",
    "fa": "درود!"
}

context = """
JUST OUTPUT GANTT CHART FORMAT | 
This Gantt chart provides a detailed and tidy plan for the purpose described in the [AI_EXTRA] and related specific practical tasks in the following. The plan is not a general timeplan. its specific at it most detailed version it can be. The plan is designed to cover the most important aspects of Vue.js in a step-by-step manner, with each task building on the previous one. Just send output as mermaid in markdown without code blocks or backticks, without anything else. This is an example working nicely, make sure to send output just in this format styling:

```
example 1
gantt
title AI TEMP: Create Video
section 5 tasks/1 week
Task 1 :a1, 2023-09-14, 7d
Task 2 :a2, 2023-09-14, 7d
Task 3 :a3, 2023-09-14, 7d
Task 4 :a4, 2023-09-14, 7d
Task 5 :a5, 2023-09-14, 7

example 2
gantt
title 30-day IELTS Preparation Plan
dateFormat YYYY-MM-DD
section Reading
Practice tests 1-5 :a1, 2023-03-01, 10d
Focus on difficult areas :after a1 , 10d
Practice tests 6-10 :after a2, 10d
section Writing
Practice tests 1-5 :a3, 2023-03-11, 10d
Focus on difficult areas :after a3, 10d
Practice tests 6-10 :after a4, 10d
section Speaking
Speaking practice 1-5 :a5, 2023-03-21, 10d
Focus on difficult areas :after a5, 10d
Speaking practice 6-10 :after a6, 10d
section Listening
Practice tests 1-5 :a7, 2023-03-31, 10d
Focus on difficult areas :after a7, 10d
Practice tests 6-10 :after a8, 10d

example 3
gantt
title 30-day IELTS Preparation Plan
dateFormat YYYY-MM-DD
section Reading 
Practice tests 1-5 :a1, 2023-03-01, 10d 
Focus on difficult areas :after a1 , 10d 
Practice tests 6-10 :after a2, 10d 
section Writing 
Practice tests 1-5 :a3, 2023-03-11, 10d 
Focus on difficult areas :after a3, 10d 
Practice tests 6-10 :after a4, 10d 
section Speaking 
Speaking practice 1-5 :a5, 2023-03-21, 10d 
Focus on difficult areas :after a5, 10d 
Speaking practice 6-10 :after a6, 10d 
section Listening 
Practice tests 1-5 :a7, 2023-03-31, 10d 
Focus on difficult areas :after a7, 10d 
Practice tests 6-10 :after a8, 10d
```

+ rule 1:  dont use ":" in the section names, as it gets errors.

+ rule 2:  make sure you use todays date as 2023/03/14. 

+ rule 3: make sure you ideate specific tasks wanted from you as exact and as full-detailed as possible. with comprehensive expert-minded wisdom.

+ rule 4: make sure you just output the gantt chart in markdown format without anything needed to be rendered other than react-mermaid2. 

+ rule 5: make sure to remove characters of   from first and end

+ rule 6: you output must bring as many micro-tasks as possible and expand any expandable scope and be very very in detail about the tasks. to impress any single person out there.

-- -- -- -- -- -- -- -- -- -- -- --
You have to output only --> [Gantt task-plan in mermaid.js]

[AI_EXTRA]: 
Purpose: Web Development with Vue.js
Time: 28 days
Total Actions: 32

the following is user's message to update the [AI_EXTRA]"""


class Prompts:
    def __init__(self):
        self.msg_list = []
        self.messages = [
            {"role": "system", "content": context},
            {"role": "assistant",
                "content": f"{LANGUAGE_TABLE[chat_language]}"}
        ]

        self.messagesTk = [50, 0]

        self.msg_list.append(f"AI:{LANGUAGE_TABLE[chat_language]}")

    def add_msg(self, new_msg):
        if len(self.messages) >= MSG_LIST_LIMIT:
            self.remove_msg()
        self.msg_list.append(new_msg)

    def remove_msg(self):
        self.msg_list.pop(0)

    def generate_prompt(self):
        return '\n'.join(self.msg_list)

    totalBefore = 0

    def update_messages(self, role, content, usage=None):
        self.messages.append({"role": role, "content": content})

        if role == "assistant" and usage is not None:
            addedTokens = usage['total_tokens'] - self.messagesTk[-1]
            self.messagesTk.append(addedTokens)
        else:
            self.messagesTk.append(0)

    def shorten(self, prompt_tokens, completion_tokens, total_tokens):
        excessive_tokens_count = total_tokens-4096
        indice_to_remove = []
        for index, value in enumerate(self.messages):
            if (excessive_tokens_count == 0):
                break
            if (index == 0):
                pass
            else:
                if (self.messagesTk[index]/excessive_tokens_count < 1.1):
                    indice_to_remove.append(index)
                    excessive_tokens_count -= self.messagesTk[index]
                else:
                    truncating_position = (
                        self.messagesTk[index] / excessive_tokens_count)*1.3*len(self.messages[index]['content'])
                    excessive_tokens_count = 0
                    self.messages[index]['content'] = self.messages[index]['content'][truncating_position:]
        if (len(indice_to_remove)):
            for i, value in enumerate(indice_to_remove):
                self.messages.pop(value)
                self.messagesTk.pop(value)


class ChatGPT:
    def __init__(self):
        self.prompt = Prompts()
        self.model = os.getenv("OPENAI_MODEL", default="text-davinci-003")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default=0.5))
        self.frequency_penalty = float(
            os.getenv("OPENAI_FREQUENCY_PENALTY", default=0))
        self.presence_penalty = float(
            os.getenv("OPENAI_PRESENCE_PENALTY", default=0))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default=250))

    def get_response(self):

        whileOverride = 0
        while (not whileOverride):
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

            if (usage['total_tokens'] > 4090):
                self.prompt.shorten(
                    usage['prompt_tokens'], usage['completion_tokens'], usage['total_tokens'])
            else:
                whileOverride = 1

        self.prompt.update_messages("assistant", content, usage)

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
        print("\n \n \n", f"{len(self.prompt.messages)}", "\n \n \n")
        print("self.prompt.messages: \n \n \n", self.prompt.messages)

        return response['choices'][0]['message']['content'].strip()

    def add_msg(self, text):
        self.prompt.add_msg(text)


#####################
telegram_bot_token = str(os.getenv("TELEGRAM_BOT_TOKEN"))


# Load data from config.ini file
# config = configparser.ConfigParser()
# config.read('config.ini')

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
    # text = update.message.text
    # update.message.reply_text(text)

    bot.send_chat_action(chat_id=update.message.chat_id,
                         action=telegram.ChatAction.TYPING)
    # 人類的問題 the question humans asked
    chatgpt.prompt.add_msg(update.message.text)
    chatgpt.prompt.update_messages("user", update.message.text)

    # ChatGPT產生的回答 the answers that ChatGPT gave
    ai_reply_response = chatgpt.get_response()

    # 用AI的文字回傳 reply the text that AI made
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
    update.message.reply_text(
        'Hello! I am Chat-GPT, a chatbot powered by OpenAI GPT-3. Input your query and I will answer it.')


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
