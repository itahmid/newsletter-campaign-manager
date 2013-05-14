from flask import Blueprint, render_template, request


mod = Blueprint('messages', __name__)


@mod.route('/create_message', methods=['GET', 'POST'])
def create_message():
    nid = request.args.get('nid')
    if not nid:
        nid = 0
    msg = request.args.get('msg')
    print msg
    return render_template('messages/details.html', nid=nid)


@mod.route('/edit_message', methods=['GET', 'POST'])
def edit_message():
    editing = True

    nid = request.args.get('nid')
    if not nid:
        nid = 0
    if request.method == 'POST':
        for k,v in request.args.iteritems():
            print k, v
    msg = request.args.get('msg')
    print msg
    return render_template('messages/details.html', editing=True,nid=nid)
