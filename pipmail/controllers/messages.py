from flask import Blueprint, render_template, request


mod = Blueprint('messages', __name__)


@mod.route('/messages')
def edit_message():
    nid = request.args.get('nid')
    if not nid:
        nid = None
    return render_template('messages/details.html', nid=nid)
