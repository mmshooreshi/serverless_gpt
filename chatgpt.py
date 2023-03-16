import os
from openai2 import OpenAI
from prompts import Prompts

class ChatGPT:  
    def __init__(self):
        self.prompt = Prompts()
    
    def get_response(self):
        openai = OpenAI(self.prompt.messages)
        while_override = 0
        while not while_override:
            response = openai.get_response()
            usage = response['usage']
            content = response['choices'][0]['message']['content']

            if usage['total_tokens'] > 4090:
                self.prompt.shorten(usage['prompt_tokens'], usage['completion_tokens'], usage['total_tokens'])
            else:
                while_override = 1

        self.prompt.update_messages("assistant", content, usage)

        return response['choices'][0]['message']['content'].strip()

    def add_msg(self, text):
        self.prompt.add_msg(text)