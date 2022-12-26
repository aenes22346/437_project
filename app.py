from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, session
from pymongo import MongoClient
from flask_bcrypt import Bcrypt 
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

def get_database():

    CONNECTION_STRING = "mongodb+srv://437_project:sifre437sifre@cluster0.i2wjyyr.mongodb.net/test"

    client = MongoClient(CONNECTION_STRING)


    return client['db']

app.config["JWT_SECRET_KEY"] = 'secret'
app.secret_key = 'secret2'

db = get_database()

collection_name = db["users"]


bcrypt = Bcrypt(app)


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

                access_token = jwt.encode({
                'username': username,
                'exp' : datetime.utcnow() + timedelta(minutes = 30)
                }, app.config["JWT_SECRET_KEY"])

                session['set_token'] = access_token

                session['set_exp'] = 1800

                session['set_user'] = username

                result = {'username': username, 'token': access_token}

                return make_response(render_template("success.html", result = result))

            else:


                message = "Wrong password or username"
                return make_response(render_template("signin.html", message = message))

@app.route("/api/v2/customer/profile", methods=['GET'])

def profile():

    now = datetime.utcnow()

    exp_time = now + timedelta(seconds=session['set_exp'])

    if now > exp_time:

        session.pop('set_user', None)
        session.pop('set_token', None)
        session.pop('set_exp', None)

        return make_response(jsonify({'msg': "token is not valid"}), 200)

    
    else:


        user_profile = collection_name.find_one({'username': session['set_user']}, projection={"adress": 0, "credit_number": 0, "cvc": 0, "_id": 0})

        return user_profile



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



            return redirect(url_for("signin"))

        else:


            message = "There is already a user with: " + username + "please try another username"
            return render_template("signup.html", message = message)
    else:

        return render_template('signup.html')



if __name__ == '__main__':
    app.run(debug = True)