from flask import (
    Blueprint, render_template)

from flaskr.db import get_db

from flaskr.auth import login_required

bp = Blueprint('addjump', __name__)

@bp.route('/addjump')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    return render_template('blog/newjump.html')