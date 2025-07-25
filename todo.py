from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "supersecretkey"

client = MongoClient("mongodb://localhost:27017/")
db = client.todo_db
users = db.users
tasks = db.tasks

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if users.find_one({'username': username}):
            flash("Username already exists!")
        else:
            users.insert_one({'username': username, 'password': password})
            flash("Registered! Please login.")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('todo'))
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/todo', methods=['GET', 'POST'])
def todo():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        task = request.form['task']
        tasks.insert_one({'username': session['username'], 'task': task, 'completed': False})

    pending = list(tasks.find({'username': session['username'], 'completed': False}))
    completed = list(tasks.find({'username': session['username'], 'completed': True}))
    return render_template('todo.html', pending=pending, completed=completed)

@app.route('/complete/<task_id>')
def complete(task_id):
    tasks.update_one({'_id': ObjectId(task_id)}, {'$set': {'completed': True}})
    return redirect(url_for('todo'))

@app.route('/delete/<task_id>')
def delete(task_id):
    tasks.delete_one({'_id': ObjectId(task_id)})
    return redirect(url_for('todo'))

if __name__ == '__main__':
    app.run(debug=True)
