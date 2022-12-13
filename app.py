from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://437_project:sifre437sifre@cluster0.i2wjyyr.mongodb.net/test"


mongodb_client = PyMongo(app)
db = mongodb_client.db

@app.route("/")
def index():
    return "Hello"



if __name__ == '__main__':
    app.run(debug = True)