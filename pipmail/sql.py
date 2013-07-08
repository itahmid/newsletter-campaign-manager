from flask.ext.mysql import MySQL
from models import Newsletter, List, Template
from time import time
mysql = MySQL()


def get_sql():
    conn = mysql.get_db()
    cur = conn.cursor()
    return conn, cur


def insert_row(tbl, form_items, conn, cur):
    r_ops = ','.join(['%s' for x in xrange(len(form_items.keys()))])
    cols = ','.join(form_items.keys())
    vals = tuple(form_items.values())
    qry = "INSERT INTO %s(%s) VALUES(%s)" % (tbl, cols, r_ops)
    try:
        cur.execute(qry, vals)
        conn.commit()
        cur.execute('SELECT last_insert_id()')
        _id = cur.fetchall()[0][0]
    except Exception, e:
        print e
        conn.rollback()
        return None
    return _id


def update_row(tbl, form_items, conn, cur, _id):
    for k, v in form_items.iteritems():
        print k, v
    _new = ', '.join(['%s=%s' % (k,v) for k, v in form_items.iteritems()])
    #vals = tuple(form_items.values())
    # cols = ','.join(['%s=%%s' % (col for col in form_items.keys(), val for val in form])
    qry = "UPDATE newsletter SET %s WHERE %s_id = %s" % (_new, tbl, _id)
    print qry
    try:
        cur.execute(qry)
        conn.commit()
        cur.execute('SELECT last_insert_id()')
        _id = cur.fetchall()[0][0]
        print _id
    except Exception, e:
        print e
        conn.rollback()
        return None
    print _id
    return _id


def get_index(model, page):
    conn, cur = get_sql()
    _models = {'list':List, 'newsletter':Newsletter, 'template':Template}
    offset = 0
    if page > 0:
        offset = (page * 15)
    cur.execute("""SELECT %s_id FROM %s
                ORDER BY date_added
                DESC LIMIT 15 OFFSET %s""" % (model, model, offset))
    _ids = cur.fetchall()
    return [_models.get(model)(conn, cur, i[0]).info for i in _ids]

def get_staff(conn, cur):
    cur.execute('SELECT name, email FROM staff')
    return cur.fetchall()

def get_companies(conn, cur):
    cur.execute('SELECT company_id, name FROM company')
    return cur.fetchall()

#def get_row_index(**kwargs):




    

# def get_all_rows(**kwargs):
#     conn, cur = get_sql()
#     model = kwargs.get('model')
#     _id = kwargs.get('id')
#     page = kwargs.get('page')
#     current_lists = None

#     offset = 0
#     if page > 0:
#         offset = (page * 15)
#     cur.execute("""SELECT id FROM %s
#                 ORDER BY date_added
#                 DESC LIMIT 15 OFFSET %s""" % (model, offset))
#     res = cur.fetchall()

#     if model == 'users':
#         users = [User(conn, cur, usr[0]).info for usr in res]
#         return users

#     if model == 'lists':
#         lists = [List(conn, cur, lst[0]).info for lst in res]
#         if _id:
#             current_lists = Newsletter(conn, cur, nid).list_ids
#             current_lists = [list_id.encode('utf8').replace(',', '')
#                                 for list_id in current_lists]
#             for lst in lists:
#                 if lst.id in current_lists:
#                     lst.action = 'remove_from'
#                 else:
#                     lst.action = 'add_to'
#         return lists, current_lists

#     if model == 'newsletters':
#         newsletters = [Newsletter(conn, cur, nltr[0]).info for nltr in res]
#         return newsletters

def get_search_index():
    conn, cur = get_sql()
    print args

#     SELECT * FROM `myTable` WHERE (`title` LIKE '%hello%' OR `title` LIKE '%world%') LIMIT numberOfValues,startingAtRowNumber


# for arg in request.args:
#     query.append('