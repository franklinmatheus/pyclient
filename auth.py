import functools
import json
import requests

from . import SERVER_ENDPOINT
from flask import (jsonify, Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth',__name__,url_prefix='/auth')

@bp.route('register', methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		username = request.form['username']
		name = request.form['name']
		password = request.form['password']
		
		data = '''{"name":"''' + name + '''","username":"''' + username + '''","password":"''' + password + '''","topics":[],"notifications":{"false":[],"true":[]}}'''
		to_send = json.loads(data)
		url = SERVER_ENDPOINT + 'signin'
		response = requests.post(url,json=to_send)

		return redirect(url_for('auth.login'))

	return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		error = None

		data = {'username':username,'password':password}
		#to_send = jsonify(data)
		url = SERVER_ENDPOINT + 'login'
		#response = requests.post(url,data=json.dumps(data))
		response = requests.post(url,json=data)
		print(response.text)

		if response.json()['result'] == 401:
			error = 'Invalid password or username'
		elif response.json()['result'] == 404:
			error = 'Username does not exist'

		if error is None:
			session.clear()
			session['user_id'] = username
			return redirect(url_for('index'))

		flash(error)

	return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
	user_id = session.get('user_id')
	if user_id is None:
		g.user = None
	else:
		response = requests.get(SERVER_ENDPOINT + user_id).json()
		print(response)
		if 'user' in response:
			g.user = response['user']
		else:
			g.user = None
			redirect(url_for('index'))

@bp.route('/logout')
def logout():
	requests.post(SERVER_ENDPOINT + session['user_id'] + '/logout')
	session.clear()
	return redirect(url_for('index'))

def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for('auth.login'))
		return view(**kwargs)
	return wrapped_view