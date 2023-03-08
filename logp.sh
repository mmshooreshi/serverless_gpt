#!/bin/bash

LOG_FILE="bot.log"

# Check if the current user has write access to the log file
if [ ! -w "$LOG_FILE" ]; then 
  # Change the permissions to allow the current user to write to the log file
  chmod u+w "$LOG_FILE"
fi

# Start the Telegram bot and redirect the output to the log file
nohup python3 main.py > "${LOG_FILE}" 2>&1 | tee -a ${LOG_FILE} &



# Check if the bot has started successfully
if [ $? -eq 0 ]; then
  echo "Bot has been started successfully"
else
  echo "Failed to start bot. Check the logs in ${LOG_FILE} for more information."
fi