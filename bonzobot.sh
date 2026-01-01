#!/bin/bash
# Bonzobot Wrapper Script
# This script ensures the bot runs with the correct local libraries and Tesseract data.

# Get absolute path of the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set environment variables for local libraries
export LD_LIBRARY_PATH="$SCRIPT_DIR/local_libs/usr/lib:$LD_LIBRARY_PATH"
export TESSDATA_PREFIX="$SCRIPT_DIR/local_libs/usr/share/tessdata/"

# Run the requested script with the virtual environment
if [ "$#" -eq 0 ]; then
    echo "Usage: ./bonzobot.sh <script_name.py> [args...]"
    echo "Example: ./bonzobot.sh forex_bot.py"
    exit 1
fi

"$SCRIPT_DIR/venv/bin/python3" "$@"
