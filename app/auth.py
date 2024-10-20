from flask import render_template, request, jsonify, redirect, url_for, session, flash
from flask import current_app as app
from werkzeug.security import check_password_hash, generate_password_hash

# AUTH VIEWS    
def register():
    if 'role' in session and session['role'] == 'admin':
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = request.form['role']

            hashed_password = generate_password_hash(password)

            user_data = {
                'username': username,
                'password': hashed_password,
                'role': role
            }
            app.db.users.insert_one(user_data)

            return redirect(url_for('main.success'))

        return render_template('register.html')
    else:
        return redirect(url_for('main.login'))

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = app.db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('main.index'))

        flash('Invalid username or password', 'error')

    return render_template('login.html')

def logout():
    session.clear()
    return redirect(url_for('main.login'))

def success():
    return "Registration successful!"