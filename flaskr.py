import sqlite3

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

DATABASE = 'resource.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def get_db():
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

@app.route('/')
def show_entries():
	cur = g.db.execute('select id, name, brand, quantity, expire_date, storage from resource_list order by id desc')
	resource = [dict(id=row[0], name=row[1], brand=row[2], quantity=row[3], expire_date=row[4], storage=row[5]) for row in cur.fetchall()]
	return render_template('show_resource.html', resource=resource)

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	name = request.form['name']
	brand =  request.form['brand']
	quantity = request.form['quantity']
	expire_date = request.form['expire_date']
	storage = request.form['storage']

	db.execute('insert into resource_list (name, brand, quantity, expire_date, storage) values (?, ?, ?, ?, ?)', [name, brand, quantity, expire_date, storage])
	db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

@app.route('/edit', methods=['PUT'])
def edit_entry():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	item_id = request.form['id']
	name = request.form['name']
	brand =  request.form['brand']
	quantity = request.form['quantity']
	expire_date = request.form['expire_date']
	storage = request.form['storage']

	db.execute('update resource_list set name = "%s", brand = "%s", quantity = "%s", expire_date = "%s", storage = "%s" where id = "%s"' %(name, brand, quantity, expire_date, storage, item_id))
	db.commit()
	flash('Edit entry was successfully')
	return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('login_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))

if __name__ == '__main__':
	app.run()