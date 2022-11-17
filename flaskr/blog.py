from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

from flaskr.foliummaps import create_map_html
from pymongo import MongoClient
import datetime

from flaskr.auth import *

client = MongoClient('mongodb://localhost:27017')
jumpMapDB = client['JumpMap']
bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    start_coords = (25.775084, -80.1947)
    folium_map = create_map_html(start_coords)

    return render_template('blog/index.html', posts=posts, folium_map=folium_map)

@bp.route('/newblogpost', methods=('GET', 'POST'))
@login_required
def newblogpost():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('blog.index'))

    return render_template('blog/newblogpost.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, description, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, description = ?'
                ' WHERE id = ?',
                (title, description, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

@bp.route('/newdropzone', methods=('GET', 'POST'))
@login_required
def add_dropzone():
    if request.method == 'POST':
        Zone_name = request.form['Zone_name']
        State= request.form['State']
        City = request.form['City']
        Latitude = request.form['Latitude']
        Longitude = request.form['Longitude']
        img = request.form['img']
        error = None

        if not Zone_name:
            Zone_name = 'Dropzone name is required.'

        if error is None:
            Dropzone_collection = jumpMapDB['Dropzones']
            DZ_info = {"Zone_name": Zone_name,
                               "State": State,
                               "City": City,
                               "Latitude": Latitude,
                               "Longitude": Longitude,
                               "img": img,
                               "Date Created": datetime.datetime.utcnow()}
            document = Dropzone_collection.insert_one(DZ_info).inserted_id
            print(jumpMapDB.list_collection_names())
            return redirect(url_for("blog.index"))

        flash(error)

    return render_template('blog/New_dropzone.html')


#Input a new jump
@bp.route('/newJump', methods=('GET', 'POST'))
@login_required
def add_jump():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        username = request.form['username']
        location = request.form['location']
        partners = request.form['partners']
        jump_number = request.form['Jump_number']
        dive_date = request.form['Dive_date']
        recommendation = request.form['recommendation']
        db = get_db()
        error = None

        if not username:
            username = 'username is required.'

        if error is None:
            userJumps_collection = jumpMapDB[username]
            jump_info = {"Title": title,
                        "Description": description,
                        "Username": username,
                        "Location": location,
                        "Partners": partners,
                        "Jump_number": jump_number,
                        "Dive_date": dive_date,
                        "Recommendation": recommendation,
                        "Date Created": datetime.datetime.utcnow()}
            document = userJumps_collection.insert_one(jump_info).inserted_id
            print(jumpMapDB.list_collection_names())
            return redirect(url_for('blog.index'))

    return render_template('blog/newjump.html')
