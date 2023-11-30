#!/bin/bash

#get the path of the script
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
GRANDPARENTDIR=$(dirname "$(dirname "$SCRIPTPATH")")
#print each pasth
echo "$SCRIPT"
echo "$SCRIPTPATH"

#echo the path
echo "$GRANDPARENTDIR"

#see if path exists at $SCRIPTPATH/venv/bin/activate"
if [ -f "$SCRIPTPATH/venv/bin/activate" ]; then
    echo "venv exists"
else
    echo "venv does not exist"
    #create virtual environment
    python3 -m venv "$SCRIPTPATH/venv"
    #activate virtual environment
    source "$SCRIPTPATH/venv/bin/activate"
    #install requirements
    pip install -r "$SCRIPTPATH/requirements.txt"
    #deactivate virtual environment
    deactivate
fi

# Check if this script is in the bash profile
BASH_PROFILE_PATH=~/.bash_profile  # change this depending on shell
ALIAS_NAME="code_summarize"  # change this to name you want for the alias
ALIAS_COMMAND="alias $ALIAS_NAME='$SCRIPT'"
if grep -Fxq "$ALIAS_COMMAND" $BASH_PROFILE_PATH
then
    echo "Alias already exists in your bash profile"
else
    echo "Alias not found in your bash profile. Do you want to add it? (yes/no)"
    read user_input
    if [[ $user_input == 'yes' ]]
    then
        echo $ALIAS_COMMAND >> $BASH_PROFILE_PATH
        echo "Alias added. You might need to restart your terminal or run 'source $BASH_PROFILE_PATH'"
    else
        echo "Okay, not adding alias"
    fi
fi

# Activate the virtual environment for the app, two levels up from the script location
source "$SCRIPTPATH/venv/bin/activate"

# Run the app in the script location
python "$SCRIPTPATH/app.py"

# Deactivate the virtual environment
deactivate
