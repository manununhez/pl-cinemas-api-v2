import requests
import json
from config import *
from flask import Flask
from cinema_scripts.kinoteka import backup_kinoteka

app = Flask(__name__)
    

session = requests.Session()  # Create a session object outside of functions

def load_cinema_data():
    with open('data/cinema_data.json', 'r') as file:
        cinema_data = json.load(file)
    return cinema_data

cinema_data = load_cinema_data()


@app.route("/collect-data")
def backup():
    # clean_tables()
    result = backup_kinoteka(session, cinema_data["KINOTEKA"])
    return result