from flask.ext.mysql import MySQL
from models import Newsletter, List, User
mysql = MySQL()


def get_sql():
    conn = mysql.get_db()
    cur = conn.cursor()
    return conn, cur


def get_index(**kwargs):
    conn, cur = get_sql()
    cntrlr = kwargs.get('cntrlr')
    _id = kwargs.get('id')
    page = kwargs.get('page')
    current_lists = None
    offset = 0
    if page > 0:
        offset = (page * 15)
    cur.execute("""SELECT id FROM %s
                ORDER BY date_added
                DESC LIMIT 15 OFFSET %s""" % (cntrlr, offset))
    res = cur.fetchall()
    if cntrlr == 'lists':
        lists = [List(conn, cur, lst[0]).info for lst in res]
        if _id:
            current_lists = Newsletter(conn, cur, nid).list_ids
            current_lists = [list_id.encode('utf8').replace(',', '')
                                for list_id in current_lists]
            for lst in lists:
                if lst.id in current_lists:
                    lst.action = 'remove_from'
                else:
                    lst.action = 'add_to'
        return lists, current_lists
    if cntrlr == 'newsletters':
        newsletters = [Newsletter(conn, cur, nltr[0]).info for nltr in res]
        return newsletters
    if cntrlr == 'users':
        users = [User(conn, cur, user[0]).info for user in res]
        return users

def get_search_index():
    conn, cur = get_sql()
    print args

#     SELECT * FROM `myTable` WHERE (`title` LIKE '%hello%' OR `title` LIKE '%world%') LIMIT numberOfValues,startingAtRowNumber


# for arg in request.args:
#     query.append('