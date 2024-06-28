#! /bin/bash

echo "Installing venv"
echo "Press enter to continue" && read
pip3 install --upgrade pip
python3 -m venv .venv

echo "Using venv"
source .venv/bin/activate

echo "Installing requirements"
echo "Press enter to continue" && read
pip3 install -r requirements.txt

chmod +x app.config.sh
chmod +x s-run.sh

#