from flask import Flask, render_template
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://437_project:sifre437sifre@cluster0.i2wjyyr.mongodb.net/test"


mongodb_client = PyMongo(app)
db = mongodb_client.db

@app.route("/signin")
def login():
    return render_template('signin.html')


@app.route("/signup")
def register():
    return render_template('signup.html')



if __name__ == '__main__':
    app.run(debug = True)