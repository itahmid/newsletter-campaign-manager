from flask import Blueprint, request, redirect, url_for, abort, \
    render_template, session
from pipmail.helpers import login_required, unix_to_local, get_sql


mod = Blueprint('manage', __name__)


user model maybe?
@mod.route('/manage')
@login_required
def index():
    conn, cur = get_sql(mysql)
    cur.execute("""SELECT * FROM users"""
    return render_template('manage/index.html')
