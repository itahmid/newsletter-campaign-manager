from flask import Blueprint, request, redirect, url_for, \
    render_template, session
from pipmail.sql import get_sql, get_index
from pipmail.helpers import login_required, collect_form_items

mod = Blueprint('users', __name__)



@mod.route('/users', defaults={'page': 0})
@mod.route('/page/<int:page>')
@login_required
def index(page):
    users = get_rows(model='users', page=page) 
    return render_template('users/index.html', users=users, page=page)
