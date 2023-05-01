#!/bin/bash

# Activate the virtual environment for the app
source ../../../svenv/bin/activate

# Run the app
python code_summarize.py

# Deactivate the virtual environment
deactivate
