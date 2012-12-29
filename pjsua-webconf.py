from __future__ import with_statement
from contextlib import closing

import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import os


DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD  = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
  return sqlite3.connect(app.config['DATABASE'])

def init_db():
  with closing(connect_db()) as db:
    with app.open_resource('schema.sql') as schema:
      db.cursor().executescript(schema.read())
    db.commit()

# App stuff
@app.before_request 
def before_request():
  g.db = connect_db()
  
@app.teardown_request
def teardown_request(exception):
  g.db.close()

@app.route('/')
def show_entries():
  cur = g.db.execute('select title, username, server, wait-time from entries order by id')
  entries = [dict(title=row[0], username=row[1], server=row[2], wait-time=row[3] ) for row in cur.fetchall()]
  return render_template('show_entries.html',entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
  if not session.get('logged_in'):
    abort(401)
  g.db.execute('insert into entries (title, username, password, server, wait-time) values(?, ?, ?, ?, ?)', [request.form['title'],request.form['text']])
  g.db.commit()
  flash('New entry successfuly posted')
  return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET','POST'])
def login():
  error = None
  if request.method == 'POST':
    if request.form['username'] != app.config['USERNAME']:
      error = 'Invalid Username'
    elif request.form['password'] != app.config['PASSWORD']:
      error = 'Invalid Password'
    else:
      session['logged_in'] = True
      flash('You were logged in!')
      return(redirect(url_for('show_entries')))

  return render_template('login.html', error=error)
  
  
  
@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  flash('You were logged out')
  return redirect(url_for('show_entries'))

if __name__ == "__main__":
  if not os.path.isfile(app.config['DATABASE']):
    init_db()
  app.run()
  
