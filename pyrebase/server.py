from flask import Flask, render_template, request, session
import requests, pyrebase, json, os

app = Flask(__name__)

firebaseConfig = {
    apiKey: "API_KEY",
	authDomain: "PROJECT_ID.firebaseapp.com",
	databaseURL: "https://PROJECT_ID.firebaseio.com",
	projectId: "PROJECT_ID",
	storageBucket: "PROJECT_ID.appspot.com",
	messagingSenderId: "SENDER_ID",
	appId: "APP_ID",
	measurementId: "G-MEASUREMENT_ID"
}

firebase = pyrebase.initialize_app(firebaseConfig)

auth = firebase.auth()
db = firebase.database()

#-- LOG --#

@app.route('/')
def ini():
    return render_template('index.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/main.html', methods=['POST'])
def main():
    error = None
        
    try:
        user = auth.sign_in_with_email_and_password(request.form['email'], request.form['pass'])
        user_info=auth.get_account_info(user['idToken'])

        session['user'] = user['idToken']

        if (str(user_info['users'][0]['emailVerified']) == "False"):
            error = 'EMAIL_NOT_VERIFIED'
            return render_template('index.html', error=error)

        name = db.child("users").child(user['localId']).child('name').get().val()
        return render_template('main.html', name=name)

    except requests.exceptions.HTTPError as e:
        error = json.loads(e.strerror)['error']['message']
        print(error)
        
    return render_template('index.html', error=error)

@app.route('/logout.html')
def logout():
    error = None

    try:
        session.pop('user')
        return render_template('logout.html')

    except requests.exceptions.HTTPError as e:
        error = json.loads(e.strerror)['error']['message']
        print(error)
        
    return render_template('main.html', error=error)

#-- REGISTRO --#

@app.route('/regist.html')
def registry():
    return render_template('regist.html')

@app.route('/verify.html', methods=['POST'])
def verify():
    error = None
    
    try:
        user = auth.create_user_with_email_and_password(request.form['email'], request.form['pass'])
        userInfo = {
            'name' : request.form['name'],
            'email' : request.form['email']
        }
        db.child("users").child(user['localId']).set(userInfo)

        auth.send_email_verification(user['idToken'])
        return render_template('verify.html')

    except requests.exceptions.HTTPError as e:
        error = json.loads(e.strerror)['error']['message']
        print(error)

    return render_template('regist.html', error=error)

#-- CAMBIO DE CONTRASEÑA --#

@app.route('/passChange.html')
def regist():
    return render_template('passChange.html')

@app.route('/passCheck.html', methods=['POST'])
def passCheck():
    error = None

    try:
        auth.send_password_reset_email(request.form['email'])
        return render_template('passCheck.html')

    except requests.exceptions.HTTPError as e:
        error = json.loads(e.strerror)['error']['message']
        print(error)

    return render_template('passChange.html', error=error)

#-- RUN --#

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(port=3000, debug=True)