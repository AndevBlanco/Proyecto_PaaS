from flask import Flask
import database, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'

@app.route("/test")
def test():
    print(os.getenv("DB_URI"))
    database.db.collection.insert_one({"name": "John"})
    return "Connected to the data base!"