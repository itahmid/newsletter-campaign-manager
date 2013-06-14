from flask.ext.mysql import MySQL
from models import User, List, Newsletter, Template
mysql = MySQL()


def get_sql():
    conn = mysql.get_db()
    cur = conn.cursor()
    return conn, cur


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