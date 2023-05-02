#!/bin/bash

#get the path of the script
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
GRANDPARENTDIR=$(dirname "$(dirname "$SCRIPTPATH")")

#echo the path
echo "$GRANDPARENTDIR"

# Activate the virtual environment for the app, two levels up from the script locartion
source "$GRANDPARENTDIR/venv/bin/activate"

# Run the app in the script location
python "$SCRIPTPATH/app.py"

# Deactivate the virtual environment
deactivate
