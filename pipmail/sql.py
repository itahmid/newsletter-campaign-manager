from flask.ext.mysql import MySQL
from models import Newsletter, List, Template, User
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
    cols = ', '.join(['%s=%%s' % k for k in form_items.iterkeys()])
    qry = "UPDATE %s SET %s WHERE %s_id = %%s" % (tbl, cols, tbl)
    vals = []
    for v in form_items.itervalues():
        try:
            v =  int(v)
        except:
            v = v.encode('ascii', 'ignore')
        vals.append(v)
    vals.append(int(_id))
    vals = tuple(vals)
    try:
        cur.execute(qry, vals)
        conn.commit()
    except Exception, e:
        print e
        conn.rollback()
        return None
    return _id


def get_index(model, page):
    conn, cur = get_sql()
    _models = {'list':List, 'newsletter':Newsletter, 'template':Template, 'user':User}
    offset = 0
    if page > 0:
        offset = (page * 15)
    cur.execute("""SELECT %s_id FROM %s
                ORDER BY date_added
                DESC LIMIT 15 OFFSET %s""" % (model, model, offset))
    _ids = cur.fetchall()
    #print len([_ids[0][0], conn, cur])

    return [_models.get(model)(conn, cur, i[0]).info for i in _ids]

def get_recip_index(list_id, page):
    conn, cur = get_sql()
    offset = 0
    if page > 0:
        offset = (page * 3)
    recip_ids = []
    cur.execute("""SELECT recipient_id, list_ids
                            FROM recipient
                            WHERE list_ids != '0'""")
    res = cur.fetchall()
    for i in res:
        list_ids = [_id.encode('utf8') for _id in i[1].split(',')]
        if str(list_id) in list_ids:
                recip_ids.append(str(i[0]))
    recip_count = len(recip_ids)
    if recip_count == 0:
        return None
    format_strings = ','.join(['%s'] * recip_count)
    base_qry = "SELECT first_name, last_name, email FROM recipient "
    qry_part1 = "WHERE recipient_id IN (%s) " % ','.join(recip_ids)
    qry_part2 = "ORDER BY date_added DESC LIMIT 3 OFFSET %s" % offset
    cur.execute(base_qry+qry_part1+qry_part2)
    res = cur.fetchall()
    cols = tuple([d[0].decode('utf8') for d in cur.description])
    return [dict(zip(cols, res)) for res in cur]

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