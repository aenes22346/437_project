from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, session
from pymongo import MongoClient
from flask_bcrypt import Bcrypt 
import jwt
from datetime import datetime, timedelta
from functools import wraps
from jwt.exceptions import ExpiredSignatureError
from bson.objectid import ObjectId
import json

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
    if (request.method == 'GET'):        #This get request is for seeing the page when "/" endpoint triggered
        return render_template('signin.html')   #then we see the sigin page automatically

    else:
        #due to usage of form request from html request.form.get is used
        username = request.form.get('username')
        password =  request.form.get('password')

        #with getting username input collection in the database will be checking
        response = collection_name.find_one({'username':username})

        if response:     #if response true which means user is found


            if bcrypt.check_password_hash(response['password'], password):   #then password checking will be needed

                access_token = jwt.encode({     #after successfully entered correct credentials token will be created for client
                'username': username,
                'exp' : datetime.utcnow() + timedelta(seconds = 10)
                }, app.config["JWT_SECRET_KEY"])

                #session attribute of flask will be used during the client logins, token and its username stored in session
                session['set_token'] = access_token     

                session['set_user'] = username


                return render_template("success.html", result = username)    #we do not pass token to the client because token inside the responding data is not a good idea

            else:


                message = "Wrong password or username"
                return render_template("signin.html", message = message)

@app.route("/api/v2/customer/profile", methods=['GET'])

@token_required     #this decorator uses for catching token and session exceptions when user requests to above route

def profile():

        user_profile = collection_name.find_one({'username': session['set_user']}, projection={"exp": 0, "cc_num": 0, "cvc": 0, "payment": 0, "_id": 0, "password": 0, "name": 0, "surname": 0}) #protection line of excessive data exposure

        ''' VULNERABLE LINES WAS COMMENTED

        user_profile = collection_name.find_one({'username': session['set_user']})

        object_id = ObjectId(user_profile['_id'])    #114-115 lines is for getting rid of "Object of type ObjectId is not JSON serializable" error, database returns unique id which is in bson library
        user_profile['_id'] = json.dumps(str(object_id))

        '''

        return make_response(render_template("profile.html", user_profile = user_profile))  # returns a html page and all user information as json



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

            #according to collected data from client above user input will be inserted to database
            collection_name.insert_one(user_input)



            return redirect(url_for("signin"))
        #if user is found error message will be shown into register page
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