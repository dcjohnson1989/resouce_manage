import sqlite3
import json

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify

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
	cur = g.db.execute('select id, name, brand, quantity, expire_date, storage, price from resource_list order by id desc')
	resource = [dict(id=row[0], name=row[1], brand=row[2], quantity=row[3], expire_date=row[4], storage=row[5], price=row[6]) for row in cur.fetchall()]
	return render_template('show_resource.html', resource=json.dumps(resource, ensure_ascii=False))

@app.route('/import_resource', methods=['GET','POST'])
def import_entry():
	if not session.get('logged_in'):
		abort(401)
	if request.method == "POST":
		db = get_db()	
		data_list = request.get_json()
		for data in data_list:
			print data
			name = data['name']
			brand =  data['brand']
			quantity = data['quantity']
			import_date = data['import_date']
			expire_date = data['expire_date']
			storage = data['storage']
			total_price = data['resource_price']
			db.execute('insert into import_list (name, brand, quantity, import_date, expire_date, storage, total_price) values (?, ?, ?, ?, ?, ?, ?)', [name, brand, quantity, import_date, expire_date, storage, total_price])
		db.commit()
		flash('New entry was successfully posted')
		return redirect(url_for('import_entry'))
	elif request.method == "GET":
		db = get_db()
		if request.args.get("date") == None:
			cur = db.execute('select import_date from import_list order by id desc limit 1')
			expected_date = cur.fetchall()[0][0]
		else:
			expected_date = request.args.get("date")
		print expected_date
		cur_get = db.execute('select id, name, brand, quantity, import_date, expire_date, storage, total_price from import_list where import_date ="%s"' %expected_date)
		import_resource = [dict(id=row[0], name=row[1], brand=row[2], quantity=row[3], import_date=row[4], expire_date=row[5], storage=row[6], price=row[7]) for row in cur_get.fetchall()]
		return render_template('import_resource.html', import_resource=json.dumps(import_resource, ensure_ascii=False))


@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	if request.method == "POST":	
		db = get_db()
		print "Johnson"
		name = request.form['name']
		brand =  request.form['brand']
		quantity = request.form['quantity']
		expire_date = request.form['expire_date']
		storage = request.form['storage']
		price = request.form['price']
		print price
		db.execute('insert into resource_list (name, brand, quantity, expire_date, storage, price) values (?, ?, ?, ?, ?, ?)', [name, brand, quantity, expire_date, storage, price])
		db.commit()
		flash('New entry was successfully posted')
		return redirect(url_for('show_entries'))

@app.route('/edit', methods=['POST'])
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
	price = request.form['price']

	db.execute('update resource_list set name = "%s", brand = "%s", quantity = "%s", expire_date = "%s", storage = "%s", price = "%s" where id = "%s"' %(name, brand, quantity, expire_date, storage, price, item_id))
	db.commit()
	flash('Edit entry was successfully')
	return redirect(url_for('show_entries'))

@app.route('/delete', methods=['POST'])
def delete_entry():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	item_id = request.form['id']
	db.execute('delete from resource_list where id = "%s"' %item_id)
	db.commit()
	flash('Delete %s entry successfully' %item_id)
	return redirect(url_for('show_entries'))

@app.route('/add_recipe', methods= ['POST'])
def add_recipe():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	dessert = request.form['dessert']
	resource_list = request.form.getlist('option_list')
	quantity_list = request.form.getlist('quantity')
	for i in range(len(resource_list)):
		db.execute('insert into recipe_list (dessert, resource_id, quantity) values (?, ?, ?)', [dessert, resource_list[i], quantity_list[i]])
		db.commit()
	flash('Add Dessert %s recipe successfully' %dessert)
	return redirect(url_for('show_recipe'))

@app.route('/edit_recipe', methods=['POST'])
def edit_recipe():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	dessert = request.form['dessert']
	resource_list = request.form.getlist('option_list')
	quantity_list = request.form.getlist('quantity')
	for i in range(len(resource_list)):
		db.execute('update recipe_list set resource_id = "%s", quantity = "%s" where dessert = "%s"' %(resource_list[i], quantity_list[i], dessert))
		db.commit()
	flash('edit Dessert %s recipe successfully' %dessert)
	return redirect(url_for('show_recipe'))

@app.route('/show_recipe', methods = ['GET'])
def show_recipe():
	cur = g.db.execute('select resource_list.id, resource_list.name, resource_list.brand, resource_list.price, recipe_list.dessert, recipe_list.quantity from resource_list inner join recipe_list on  resource_list.id = recipe_list.resource_id')
	query_result = [dict(id=row[0], name=row[1], brand=row[2], price=row[3], dessert=row[4], quantity=row[5]) for row in cur.fetchall()]
	recipe_list = dict()
	for i in query_result:
		print i
		dessert_value = i.get('dessert') 
		i.pop('dessert')
		if dessert_value in recipe_list:
			recipe_list[dessert_value].append(i)
			print "test"
		else:
			recipe_list.update({dessert_value:[i]})
	cur = g.db.execute('select id, name, brand, price from resource_list order by id desc')
	option_list = [dict(id=row[0], name=row[1], brand=row[2], price=row[3]) for row in cur.fetchall()]
	print option_list
	return render_template('show_recipe.html', recipe_list = recipe_list, option_list= option_list)

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