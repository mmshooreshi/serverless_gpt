#!/bin/bash
# This script stops a Python program named telegram_message_parser.py

# Find the PID of the process
pid=$(ps -ef | grep "main.py" | grep -v grep | awk '{print $2}')

if [ -z "$pid" ]; then
  echo "Bot is not running"
else
  # Terminate the process
  kill $pid
  echo "Bot has been terminated"
fi