from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from pymongo import MongoClient
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt 
from flask_jwt_extended import (create_access_token)

app = Flask(__name__)

def get_database():

    CONNECTION_STRING = "mongodb+srv://437_project:sifre437sifre@cluster0.i2wjyyr.mongodb.net/test"

    client = MongoClient(CONNECTION_STRING)


    return client['db']

app.config["JWT_SECRET_KEY"] = 'secret'
db = get_database()

collection_name = db["users"]


bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route("/signin", methods=['GET', 'POST'])
def signin():
    if (request.method == 'GET'):
        return render_template('signin.html')

    else:

        username = request.form.get('username')
        password =  request.form.get('password')

        response = collection_name.find_one({'username':username})

        if response:


            if bcrypt.check_password_hash(response['password'], password):

                access_token = create_access_token(identity = {
				'username': response['username'],
				'password': response['password'],
				})


                result = {'username': username, 'token': access_token}



                result_json = jsonify(result)



                return make_response(result_json, 200)





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