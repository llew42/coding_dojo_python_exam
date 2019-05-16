from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = "Shhh be bary bary quiet, I'm hunting wabbit"

bcrypt = Bcrypt(app)
present = datetime.now()

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/register', methods = ['POST'])
def register_user():
  if len(request.form['fname']) < 2:
    flash('Your first name must be at least 2 characters')
    return redirect('/')
  if len(request.form['lname']) < 2:
    flash('Your last name must be at least 2 characters')
    return redirect('/')
  if not EMAIL_REGEX.match(request.form['email']):
    flash('Invalid email address')
    return redirect('/')
  db = connectToMySQL('python_exam')
  query = 'SELECT * FROM users WHERE email = %(em)s'
  data = {
    'em': request.form['email']
  }
  duplicate_email_check = db.query_db(query, data)
  if len(duplicate_email_check) != 0:
    flash('Email address already in use')
    return redirect('/')
  if len(request.form['pw']) < 8:
    flash('Your password must be at least 8 characters')
    return redirect('/')
  if request.form['pw'] != request.form['pw_confirm']:
    flash('Your passwords must match')
    return redirect('/')
  else:
    pw_hash = bcrypt.generate_password_hash(request.form['pw'])
    query = 'INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(pw)s, NOW(), NOW());'
    data = {
      'fn': request.form['fname'],
      'ln': request.form['lname'],
      'em': request.form['email'],
      'pw': pw_hash
    }
    result = mysql.query_db(query, data)
    print(result)
    session['userid'] = result
    session['first_name'] = request.form['fname']
    flash("You've been successfully registered")
    return redirect('/dashboard')

@app.route('/login', methods = ['POST'])
def login():
  db = connectToMySQL('python_exam')
  query = 'SELECT * FROM users WHERE email = %(em)s'
  data = {
    'em': request.form['em']
  }
  result = db.query_db(query, data)
  print(request.form)
  if result:
    if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
      session['userid'] = result[0]['id']
      session['first_name'] = result[0]['first_name']
      flash('Welcome back')
      return redirect('/dashboard')
  flash("You could not be logged in")
  return redirect('/')

@app.route('/dashboard')
def dashboard():
  db = connectToMySQL('python_exam')
  if 'userid' not in session:
    flash("You must be logged in to view this page")
    return redirect('/')
  else:
    query = 'SELECT * FROM trips WHERE users_id = %(id)s ORDER BY created_at DESC;'
    data = {
      'id': session['userid'],
    }
    trips = db.query_db(query, data)
    print(trips)
    return render_template('dashboard.html', all_trips = trips)

@app.route('/trips/new')
def new_trips():
  return render_template('new_trips.html')

@app.route('/new_trips', methods = ['POST'])
def create_new_trip():
  print(request.form)
  if len(request.form['destination']) < 3:
    flash("Please enter at least 3 characters for your destination")
    return redirect('/trips/new')
  if len(request.form['plan']) < 3:
    flash("Please enter at least 3 characters for your plan")
    return redirect('/trips/new')
  if len(request.form['sdate']) < 1:
    flash("Please select a trip start date")
    return redirect('/trips/new')
  if len(request.form['edate']) < 1:
    flash("Please select a trip end date")
    return redirect('/trips/new')
  else:
    db = connectToMySQL('python_exam')
    query = 'INSERT INTO trips (users_id, destination, start_date, end_date, plan) VALUES (%(uid)s, %(des)s, %(sd)s, %(ed)s, %(pl)s);'
    data = {
      'uid': session['userid'],
      'des': request.form['destination'],
      'sd': request.form['sdate'],
      'ed': request.form['edate'],
      'pl': request.form['plan']
    }
    print(request.form)
    db.query_db(query, data)
    return redirect('/dashboard')

@app.route('/trips/edit/<id>', methods = ['GET', 'POST'])
def edit_trips(id):
  if request.method == 'GET':
    db = connectToMySQL('python_exam')
    query = 'SELECT * FROM trips WHERE id = %(id)s;'
    data = {
      'id': id,
    }
    edit_trip = db.query_db(query, data)
    return render_template('edit_trips.html', edit_trip = edit_trip)
    print(request.form)
  elif request.method == 'POST':
      if len(request.form['destination']) < 3:
        flash("Please enter at least 3 characters for your destination")
        return redirect('/trips/edit/' + str(id))
      if len(request.form['plan']) < 3:
        flash("Please enter at least 3 characters for your plan")
        return redirect('/trips/edit/' + str(id))
      if len(request.form['sdate']) < 1:
        flash("Please select a trip start date")
        return redirect('/trips/edit/' + str(id))
      if len(request.form['edate']) < 1:
        flash("Please select a trip end date")
        return redirect('/trips/edit/' + str(id))
      else:
        db = connectToMySQL('python_exam')
        query = 'UPDATE trips SET users_id=%(uid)s, destination=%(des)s, start_date=%(sd)s, end_date=%(ed)s, plan=%(pl)s WHERE id = %(id)s;'
        data = {
          'uid': session['userid'],
          'des': request.form['destination'],
          'sd': request.form['sdate'],
          'ed': request.form['edate'],
          'pl': request.form['plan'],
          'id': id
        }
        print(request.form)
        db.query_db(query, data)
        return redirect('/dashboard')

@app.route('/trips/<id>')
def trips(id):
  db = connectToMySQL('python_exam')
  query = 'SELECT users.first_name, trips.id, trips.start_date, trips.end_date, trips.created_at, trips.updated_at, trips.plan, trips.destination FROM trips JOIN users ON users.id = trips.users_id WHERE trips.id = %(id)s;'
  data = {
    'id': id,
  }
  trips = db.query_db(query, data)
  return render_template('trips.html', all_trips = trips)

@app.route('/logout')
def logout():
  print(session)
  session.clear()
  flash("You've been logged out")
  return redirect('/')

@app.route('/delete/<id>')
def delete(id):
  db = connectToMySQL('python_exam')
  query = 'DELETE FROM trips WHERE id = %(id)s;'
  data = {
    'id': id,
  }
  db.query_db(query, data)
  return redirect('/dashboard')

if __name__ == "__main__":
  app.run(debug=True)
