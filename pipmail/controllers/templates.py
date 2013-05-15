from flask import Blueprint, render_template, current_app


mod = Blueprint('templates', __name__)


@mod.route('/templates')
def index():
    return render_template('templates/index.html')

# @mod.route('/create_template', methods=['GET', 'POST'])
# @login_required
# def create_template():
#     '''Create a new template'''
#     errors = None
#     conn, cur = get_sql()
#     if request_method == 'POST':
#         errors = collect_form_errors(request.form, 'campaigns')
#         if not errors:
#             try:
#                 cur.execute("""INSERT INTO newsletters(code, name, author,
#                             company, from_name, from_email, replyto_email,
#                             date_added, date_sent, priority, unsub)
#                             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#                             """, (
#                             request.form.get('code'),
#                             request.form.get('subject'),
#                             session.get('current_user'),
#                             request.form.get('company'),
#                             request.form.get('from_name'),
#                             request.form.get('from_email'),
#                             request.form.get('replyto_email'),
#                             int(time.time()),
#                             0,
#                             request.form.get('priority'),
#                             request.form.get('unsub', 0),
#                             )
#                             )
#                 conn.commit()
#                 cur.execute('SELECT last_insert_id()')
#                 nid = cur.fetchall()[0][0]
#             except Exception, err:
#                 conn.rollback()
#                 return render_template('error.html', error=err)
#             return redirect(url_for('subscribers.index', nid=nid))

#     return render_template('campaigns/details.html', companies=companies,
#                            staff=staff, errors=errors, editing=False)