# a) Install dependencies
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

# b) Run all necessary parts of the codebase
export FLASK_APP=app.py
flask run
