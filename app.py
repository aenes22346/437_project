from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, session
from pymongo import MongoClient
from flask_bcrypt import Bcrypt 
import jwt
from datetime import datetime, timedelta
from functools import wraps
from jwt.exceptions import ExpiredSignatureError

app = Flask(__name__)

def get_database():

    CONNECTION_STRING = "mongodb+srv://437_project:sifre437sifre@cluster0.i2wjyyr.mongodb.net/test"

    client = MongoClient(CONNECTION_STRING)


    return client['db']

app.config["JWT_SECRET_KEY"] = 'secret'
app.config["SECRET_KEY"] = 'secret2'

db = get_database()

collection_name = db["users"]


bcrypt = Bcrypt(app)



def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):


        try:


            token = session['set_token']

        except KeyError:  #gives exception when token == None


            return render_template('error.html', error = 'Token is missing') # Output: KeyError: 'set_token' when session popped


        try:

            data = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=['HS256'])


            #if datetime.fromtimestamp(data['exp']) < datetime.utcnow():    this line is an alternative to check token valid time and current time however it is better to use jwt's own token checker

        except jwt.ExpiredSignatureError:    #this is a typical exception for expired dated token


            return render_template('error.html', error = 'Token is invalid')

        return f(*args, **kwargs)

    return decorator




@app.route("/", methods=['GET', 'POST'])
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
                'exp' : datetime.utcnow() + timedelta(seconds = 10)
                }, app.config["JWT_SECRET_KEY"])

                session['set_token'] = access_token

                session['set_user'] = username

                result = {'username': username, 'token': access_token}

                return render_template("success.html", result = result)

            else:


                message = "Wrong password or username"
                return render_template("signin.html", message = message)

@app.route("/api/v2/customer/profile", methods=['GET'])

@token_required     #this decorator uses for catching token and session exceptions when user requests to above route

def profile():

        user_profile = collection_name.find_one({'username': session['set_user']}, projection={"exp": 0, "cc_num": 0, "cvc": 0, "payment": 0, "_id": 0}) #protection line of excessive data exposure

        return make_response(render_template('profile.html', user_profile = user_profile))   # returns a html page and user information as json



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



@app.route("/logout", methods=['POST'])
def logout():


    session.pop('set_user', None)
    session.pop('set_token', None)

    message = "You are now logged out go to signin page"
    return message



if __name__ == '__main__':
    app.run(debug = False)