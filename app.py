from flask import Flask, render_template, jsonify, request, redirect, url_for, json
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

@app.route("/signin", methods=['GET', 'POST'])
def signin():
    if (request.method == 'GET'):
        return render_template('signin.html')

    else:

        return render_template('signin.html')


@app.route("/success", methods=['GET'])
def success():
    return render_template('success.html')


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if (request.method == 'POST'):
        username = request.form.get('username')
        name = request.form.get('name')
        surname = request.form.get('surname')
        password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')


        user_found = collection_name.find_one({"username": username})

        if user_found == None:


            user_input = {'username': username, 'name': name, 'surname': surname, 'password': password}


            collection_name.insert_one(user_input)



            return redirect(url_for("success"))

        else:


            message = "There is already a user with: " + username + "please try another username"
            return render_template("signup.html", message = message)
    else:

        return render_template('signup.html')



if __name__ == '__main__':
    app.run(debug = True)