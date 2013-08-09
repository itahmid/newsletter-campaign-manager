from flask import Blueprint, render_template, request
from flask.ext.mail import Message
from pipmail.helpers import login_required


mod = Blueprint('deliveries', __name__)

@mod.route('/deliveries')
@login_required
def index():
    nid = request.args.get('nid')
    return render_template('deliveries/index.html', nid=nid)

def send_test(content, recipient):
    msg = Message("Test email",
                  sender="someone@somewhere.com",
                  recipients=[recipient])
    msg.html = content
    mail.send(msg)
