import os
from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_pymongo import PyMongo
from flask_cors import CORS
import json
import bcrypt

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')
CORS(app)

app.config["MONGO_URI"] = "mongodb://localhost:27017/quizdb"
mongo = PyMongo(app)

# Load questions from JSON files
with open('questions/history.json', 'r') as f:
    history_questions = json.load(f)
with open('questions/science.json', 'r') as f:
    science_questions = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = mongo.db.users
        username = request.form['username']
        password = request.form['password']
        existing_user = users.find_one({'username': username})

        if existing_user is None:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'username': username, 'password': hashed_pw})
            session['username'] = username
            return redirect(url_for('quiz'))

        return render_template('signup.html', error="User already exists")
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        users = mongo.db.users
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({'username': username})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['username'] = username
            return redirect(url_for('quiz'))

        return render_template('signin.html', error="Invalid credentials")
    return render_template('signin.html')

# Sign out route
@app.route('/signout', methods=['POST'])
def signout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/quiz')
def quiz():
    if 'username' in session:
        return render_template('quiz.html')
    return redirect(url_for('signin'))

@app.route('/api/questions/<topic>', methods=['GET'])
def get_questions(topic):
    if topic == 'history':
        return jsonify(history_questions)
    elif topic == 'science':
        return jsonify(science_questions)
    else:
        return jsonify({"message": "Topic not found"}), 404



if __name__ == '__main__':
    app.run(debug=True)
