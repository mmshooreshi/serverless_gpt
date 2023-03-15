manual:
- Import required libraries:
    - logging: for logging messages
    - telegram: for interacting with Telegram API
    - os: for accessing environment variables
    - Flask: for building web applications
    - Dispatcher, MessageHandler, Filters, CommandHandler: for handling different types of messages and commands in Telegram bot
    - openai: for accessing OpenAI's GPT-3 API
    
- Set global variables:
    - MSG_LIST_LIMIT: for limiting the number of messages in the prompt list
    - LANGUAGE_TABLE: a dictionary mapping language codes to greeting messages
    - openai.api_key: authenticate with OpenAI's GPT-3 API using the API key stored in environment variables
    - chat_language: the language used for the initial greeting message
    
- Define Prompts class:
    - __init__: initialize the list of messages with the initial greeting message
    - add_msg: add a new message to the list of messages and remove the oldest message if the list exceeds the limit
    - remove_msg: remove the oldest message from the list of messages
   - generate_prompt: concatenate all messages in the list of messages to form the prompt
    - update_messages: add a new message to the list of messages and update the list of tokens used by each message (if the message is an AI response)
    - shorten: remove messages from the list of messages to reduce the total number of tokens used (if the total exceeds the limit)

- Define ChatGPT class:
    - __init__: initialize the Prompts object and set the parameters for generating responses using GPT-3 API (model, temperature, frequency penalty, presence penalty, max tokens)
    - get_response: generate a response using GPT-3 API based on the current prompt
    - add_msg: add a new message to the Prompts object

- Get Telegram bot token from environment variables

- Define Flask app

- Initialize Telegram bot using bot token

- Define handlers for different types of messages and commands:
    - reply_handler: generate a response using ChatGPT object and send the response to the user
    - clear_handler: clear the list of messages in the Prompts object
    - start_handler: send an initial
+____+_+_+_+_+_+_+____+
greeting message to the user when they start the bot

- Create a dispatcher object to handle incoming messages and commands

- Add the message and command handlers to the dispatcher object

- Start the Flask app to listen for incoming messages and commands

I hope this helps! Let me know if you have any questions or if there's anything else I can do for you.

_____________________
