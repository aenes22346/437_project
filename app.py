from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt 

app = Flask(__name__)

def get_database():

    CONNECTION_STRING = "mongodb+srv://437_project:sifre437sifre@cluster0.i2wjyyr.mongodb.net/test"

    client = MongoClient(CONNECTION_STRING)


    return client['db']


db = get_database()

collection_name = db["users"]


bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route("/signin", methods=['GET'])
def login_get():
    return render_template('signin.html')

@app.route("/signin", methods=['POST'])
def login_post():
    return render_template('signin.html')


@app.route("/signup", methods=['GET'])
def signup_get():
    return render_template('signup.html')


@app.route("/signup", methods=['POST'])
def signup_post():

    username = request.get_json()['username']
    name = request.get_json()['name']
    surname = request.get_json()['surname']
    password = bcrypt.generate_password_hash(request.get_json()['password']).decode('utf-8')


    user_found = collection_name.find_one({"username": username})

    if user_found == None:


        user_input = {'username': username, 'name': name, 'password': password, 'surname': surname}


        collection_name.insert_one(user_input)



        return jsonify(username + " registered")

    else:


        return jsonify("There is already a user with: " + username)



if __name__ == '__main__':
    app.run(debug = True)