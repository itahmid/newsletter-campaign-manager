from helpers import unix_to_local


class Base(object):
    '''Base class for models'''
    def __init__(self, conn, cur, _id):
        self.conn = conn
        self.cur = cur
        self.id = str(_id)

    def get_result_dict(self, tbl):
        self.cur.execute("SELECT * FROM %s WHERE id = %s" % (tbl, self.id))
        res = self.cur.fetchall()
        cols = tuple([d[0].decode('utf8') for d in self.cur.description[1:]])
        return dict(zip(cols, res[0][1:]))


class List(Base):
    '''Model for subscriber lists'''
    def __init__(self, conn, cur, _id):
        super(List, self).__init__(conn, cur, _id)
        self.id = str(_id)
        for k, v in self.get_result_dict('lists').iteritems():
            setattr(self, k, v)
        self.recip_count = self.get_recips(count=True)
        self.local_time = unix_to_local(self.date_added)

    def get_recips(self, count=False):
        recip_ids = []
        self.cur.execute("""SELECT id, list_ids
                            FROM recipients
                            WHERE list_ids != '0'""")
        res = self.cur.fetchall()
        for i in res:
            list_ids = [_id.encode('utf8') for _id in i[1].split(',')]
            if self.id in list_ids:
                recip_ids.append(int(i[0]))
        recip_count = len(recip_ids)
        if count:
            return recip_count
        format_strings = ','.join(['%s'] * recip_count)
        try:
            self.cur.execute("""SELECT first_name, last_name, email
                                FROM recipients
                                WHERE id IN (%s)""" %
                             format_strings,
                             tuple(recip_ids))
            res = self.cur.fetchall()
            cols = tuple([d[0].decode('utf8') for d in self.cur.description])
            return [dict(zip(cols, res)) for res in self.cur]
        except:
            return None


class Newsletter(Base):
    def __init__(self, conn, cur, _id):
        super(Newsletter, self).__init__(conn, cur, _id)
        self.id = str(_id)
        self.info = self.get_result_dict('newsletters')
        self.info['local_time'] = unix_to_local(self.info['date_added'])
        self.info['list_ids'] = self.info['list_ids'].encode('ascii', 'ignore').split(',')
        self.info['company'] = self.get_company_name()
        self.info['recip_count'] = 0

    def get_company_name(self):
        self.cur.execute("""SELECT name FROM companies
                        WHERE id = %s""" % self.info['company'])
        comp = self.cur.fetchall()[0][0]
        if comp == 0:
            comp = 'N/A'
        return comp

    def get_recip_count(self):
        recip_count = 0
        for _id in self.info['list_ids']:
            self.cur.execute("""SELECT COUNT(id)
                                FROM recipients
                                WHERE list_id = %s""" % _id)
            recip_count += self.cur.fetchall()[0][0]
        return recip_count


# class User(object):
#     '''Model for pipmail user'''
#     def __init__(self, conn, _id):
#         self.conn, self.cur = get_sql()
#         self.id = str(_id)
#         for k, v in self.get_result_dict().iteritems():
#             setattr(self, k, v)
#         self.local_time = unix_to_local(self.last_login)

#     def get_result_dict(self):
#         self.cur.execute("SELECT * FROM users WHERE id = %s" % self.id)
#         res = self.cur.fetchall()
#         cols = tuple([d[0].decode('utf8') for d in self.cur.description[1:]])
#         return dict(zip(cols, res[0][1:]))

#     def get_all_users(self):
#         self.cur.execute("SELECT * FROM users")
#         res = self.cur.fetchall()
#         cols = tuple([d[0].decode('utf8') for d in self.cur.description[1:]])
#         return dict(zip(cols, res[0][1:]))
