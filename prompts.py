import os

MSG_LIST_LIMIT = int(os.getenv("MSG_LIST_LIMIT", default = 20))
LANGUAGE_TABLE = {
	  "zh": "哈囉！",
	  "en": "Hello!",
      "jp": "こんにちは",
      "fa": "درود!"
	}

context = "you are helpful assistant"

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
            added_tokens = usage['total_tokens'] - self.messagesTk[-1]
            self.messagesTk.append(added_tokens)
        else:
            self.messagesTk.append(0)
	
    def shorten(self, prompt_tokens, completion_tokens, total_tokens):
        excessive_tokens_count = total_tokens - 4096
        indices_to_remove = []
        for index, value in enumerate(self.messages):
            if excessive_tokens_count == 0:
                break
            if index == 0:
                pass
            else:
                if self.messagesTk[index] / excessive_tokens_count < 1.1:
                    indices_to_remove.append(index)
                    excessive_tokens_count -= self.messagesTk[index]
                else:
                    truncating_position = (self.messagesTk[index] / excessive_tokens_count) * 1.3 * len(self.messages[index]['content'])
                    excessive_tokens_count = 0
                    self.messages[index]['content'] = self.messages[index]['content'][:truncating_position]
        if len(indices_to_remove):
            for i, value in enumerate(indices_to_remove):
                self.messages.pop(value)
                self.messagesTk.pop(value)