from functools import wraps
from flask import redirect, session
import datetime


def allowed_file(filename, exts):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in exts


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        else:
            return func(*args, **kwargs)
    return wrapper


def unix_to_local(timestamp):
    ts = int(timestamp)
    _time = datetime.datetime.fromtimestamp(
        ts).strftime('%Y-%m-%d %I:%M:%S')
    return _time


def get_sql(mysql):
    conn = mysql.get_db()
    cur = conn.cursor()
    return conn, cur

#make a uniform search function for both controllers
# def search():
#     keywords = request.form['keywords']
#     db = get_db()
#     cur = db.execute("""SELECT paste_id, title, paste_text, date_str
# FROM pastes WHERE paste_text LIKE '%?%'""",
#                         (keywords,))
#     result = fetch_result(cur.fetchall())

#     return render_template("search.html", results=result)
