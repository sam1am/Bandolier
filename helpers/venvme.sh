#see if a ./venv directory exists, if not make a new python environment and install requirements.txt
if [ ! -d "./venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Installing requirements..."
    source venv/bin/activate
    pip install -r requirements.txt
    echo "Done!"
fi
source venv/bin/activate
