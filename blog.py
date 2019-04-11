import requests

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session
from werkzeug.exceptions import abort

from client.auth import login_required
from . import SERVER_ENDPOINT

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    posts = requests.get(SERVER_ENDPOINT).json()
    print(posts, 'posts')
    return render_template('blog/index.html',posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        topics = request.form['topics'].split(',')
        end = request.form['end']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            data = {"name":title,"description":body,"topics":topics,"author":session['user_id'],"end":end}
            requests.post(SERVER_ENDPOINT,json=data)
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

@bp.route('/addtopic', methods=('GET','POST'))
def addtopic():
    if request.method == 'POST':
        topic = request.form['topic']
        response = requests.post(SERVER_ENDPOINT + session['user_id'] + '/topics/' + topic)
        print(response)
        return redirect(url_for('blog.addtopic'))

    return render_template('blog/addtopic.html', topics=g.user['topics'])

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    return redirect(url_for('blog.index'))