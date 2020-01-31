virtualenv -p python3 ~/.virtualenvs/pytail
source ~/.virtualenvs/pytail/bin/activate
pip install -r requirements.txt
source .pythonpath
pytail -c sample.yaml