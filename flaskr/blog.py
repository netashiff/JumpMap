from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

from flaskr.foliummaps import create_map_html
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
jumpMapDB = client['JumpMap']
bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()

    start_coords = (25.775084, -80.1947)
    folium_map = create_map_html(start_coords)

    return render_template('blog/index.html', folium_map=folium_map)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
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
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
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
        db = get_db()
        error = None

        if not Zone_name:
            Zone_name = 'Zone_name is required.'

        if error is None:
            print("no error")
            try:
                Dropzone_collection = jumpMapDB['Dropzones']
                DZ_info = {"Zone_name": Zone_name,
                               "State": State,
                               "City": City,
                               "Latitude": Latitude,
                               "Longitude": Longitude,
                               "img": img}
                               #This line doesnt work -> , "Date Created": datetime.datetime.utcnow()}
                document =Dropzone_collection.insert_one(DZ_info).inserted_id
                print(jumpMapDB.list_collection_names())
            except db.IntegrityError:
                error = f"Dropzone {Zone_name} is already registered."
            else:
                return redirect(url_for("blog.index"))

        flash(error)

    return render_template('blog/New_dropzone.html')


#try to input the new jump
@bp.route('/newjump', methods=('GET', 'POST'))
@login_required
def add_Jump():
    if request.method == 'POST':
        title = request.form['name']
        location = request.form['location']
        Partners = request.form['Partners']
        Dive_date = request.form['Dive_date']
        color = request.form['colors']
        #reccomendation = request.form['reccomendation']
        img = request.form['img']
        db = get_db()
        error = None

        #Get username
        from flaskr.auth import get_logged_in_user
        username = get_logged_in_user()

        if not username:
            username = 'username is required.'

        if error is None:
            try:
                print(username)
                userJumpsCollection = jumpMapDB[str(username)]
                DZ_info = {"Name": title,
                           "Username": username,
                            "Location": location,
                           "Partners": Partners,
                           "Dive_date": Dive_date,
                           "Color": color,
                           "img": img}
                           #, "Date Created": datetime.datetime.utcnow()
                document = userJumpsCollection.insert_one(DZ_info).inserted_id
                print(jumpMapDB.list_collection_names())

            except db.IntegrityError:
                error = f"username {username} is already registered."
            else:
                return redirect(url_for("blog.index"))

        flash(error)

    return render_template('blog/New_jump.html')
