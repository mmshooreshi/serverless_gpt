import os

class OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", default = "text-davinci-003")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", default = 0.5))
    frequency_penalty = float(os.getenv("OPENAI_FREQUENCY_PENALTY", default = 0))
    presence_penalty = float(os.getenv("OPENAI_PRESENCE_PENALTY", default = 0))
    max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default = 250))
    
    def __init__(self, messages):
        self.messages = messages
    
    def get_response(self):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            max_tokens=self.max_tokens
        )
        return response