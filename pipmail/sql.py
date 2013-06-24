from flask.ext.mysql import MySQL
from models import User, List, Newsletter, Template
import time
mysql = MySQL()


def get_sql():
    conn = mysql.get_db()
    cur = conn.cursor()
    return conn, cur

def insert_row(tbl, form, cur):
    cols = []
    vals = []
    for k, v in form.iteritems():
        if (v != '' and k[len(k) - 3:] != 'sel'):
            cols.append(k)
            vals.append(v)
    vals.append(int(time.time()))
    vals = tuple(vals)
   
    r_ops = ','.join(['%s' for x in xrange(len(cols)+1)])
    cols = ','.join(cols)
    #vals = ','.join(vals)
    qry_base =  """INSERT INTO {tbl}({cols},date_added) VALUES {r_ops}""".format(tbl=tbl, cols=cols, r_ops=r_ops)
    print qry_base
    print vals
    cur.execute(qry_base, vals)
    #cur.execute(qry)
    # cur.execute(qry_base, (vals)

def get_rows(_ids=None, **kwargs):
    conn, cur = get_sql()
    model = kwargs.get('model')
    _id = kwargs.get('id')
    page = kwargs.get('page')
    _models = {'users':User, 'lists':List, 'newsletters':Newsletter, 'templates':Template}
    if not _ids:
        offset = 0
        if page > 0:
            offset = (page * 15)
        cur.execute("""SELECT id FROM %s
                    ORDER BY date_added
                    DESC LIMIT 15 OFFSET %s""" % (model, offset))
        _ids = cur.fetchall()
    return [_models.get(model)(conn, cur, i[0]).info for i in _ids]



    

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