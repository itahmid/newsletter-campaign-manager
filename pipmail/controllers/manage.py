from flask import Blueprint, request, redirect, url_for, \
    render_template, session
from pipmail.sql import get_sql, get_rows
from pipmail.helpers import login_required, collect_form_errors


mod = Blueprint('manage', __name__)



@mod.route('/manage', defaults={'page': 0})
@mod.route('/page/<int:page>')
@login_required
def index(page):
    users = get_rows(model='users', page=page) #rename cntrlr
    return render_template('manage/index.html', users=users, page=page)
