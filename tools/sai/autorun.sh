#!/bin/bash

# Check for virtual environment directory, if not present, create it
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Check if `pip` is installed and upgrade it to the latest version
pip install --upgrade pip

# Install dependencies from the requirements.txt file
pip install -r requirements.txt

clear
# Run the main.py Python script
python3 main.py
