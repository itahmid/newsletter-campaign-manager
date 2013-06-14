from flask import Blueprint, render_template, request
from pipmail.helpers import login_required


mod = Blueprint('contents', __name__)


@mod.route('/contents')
@login_required
def index():
    nid = request.args.get('nid')
    return render_template('contents/index.html', nid=nid)



# @mod.route('/create_message', methods=['GET', 'POST'])
# def create():
#     nid = request.args.get('nid')
#     if not nid:
#         nid = 0
#     msg = request.args.get('msg')
#     print msg
#     return render_template('contents/details.html', nid=nid)


# @mod.route('/edit_message', methods=['GET', 'POST'])
# def edit():
#     editing = True

#     nid = request.args.get('id')
#     if not nid:
#         nid = 0
#     if request.method == 'POST':
#         for k,v in request.args.iteritems():
#             print k, v
#     msg = request.args.get('msg')
#     print msg
#     return render_template('contents/details.html', editing=True,nid=nid)
