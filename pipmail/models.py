from helpers import unix_to_local
import MySQLdb

class Base(object):
    """
    Returns a dict() object that represents a record
    """
    def __init__(self, conn, cur, _id):
        self.conn = conn
        self.cur = cur
        self._id = _id

    def get_result_dict(self, tbl):
        dict_cur = self.conn.cursor(MySQLdb.cursors.DictCursor)
        dict_cur.execute("SELECT * FROM %s WHERE %s_id = %s" % (tbl, tbl, self._id))
        return dict_cur.fetchall()[0]


class User(Base):
    """
    Returns a user record containing:
        {
            user_id : int,
            name : str,
            email : str,
            password : str,
            date_added : int,
            last_login : int
        }
    """
    def __init__(self, conn, cur, _id):
        super(User, self).__init__(conn, cur, _id)
        self.record = self.get_result_dict('user')
        self.record['last_login'] = unix_to_local(self.record['last_login'])


class List(Base):
    """
    Returns a list record containing:
        {
            list_id: int,
            name : str,
            description: str,
            date_added : int,
            author : str,
            last_login : int
        }
    """
    def __init__(self, conn, cur, _id):
        super(List, self).__init__(conn, cur, _id)
        self.record = self.get_result_dict('list')
        self.record['recipients'] = self.get_recips(count=True)
        self.record['date_added'] = unix_to_local(self.record['date_added'])

    def get_recips(self, count=False):
        recip_ids = []
        self.cur.execute("SELECT recipient_id, list_idsFROM recipient WHERE list_ids != '0'")
        res = self.cur.fetchall()
        for i in res:
            list_ids = [_id.encode('utf8') for _id in i[1].split(',')]
            if str(self.record['list_id']) in list_ids:
                recip_ids.append(int(i[0]))
        recip_count = len(recip_ids)
        if count:
            return recip_count
        format_strings = ','.join(['%s'] * recip_count)
        try:
            self.cur.execute("""SELECT first_name, last_name, email
                                FROM recipient
                                WHERE id IN (%s)""" %
                             format_strings,
                             tuple(recip_ids))
            res = self.cur.fetchall()
            cols = tuple([d[0].decode('utf8') for d in self.cur.description])
            return [dict(zip(cols, res)) for res in self.cur]
        except:
            return None


class Newsletter(Base):
    """
    Returns a newsletter record containing:
        {
            newsletter_id: int,
            code : str,
            subject: str,
            date_added : int,
            date_sent : int,
            author : str,
            company : int, (should considering changing maybe)
            from_name : str,
            from_email: str,
            replyto_email : str,
            list_ids : str (convert to list),
            unsub : int (consider changing to "unsub_link")
        }
    """
    def __init__(self, conn, cur, _id):
        super(Newsletter, self).__init__(conn, cur, _id)
        self.record = self.get_result_dict('newsletter')
        self.record['date_added'] = unix_to_local(self.record['date_added'])
        self.record['list_ids'] = self.record['list_ids'].encode('ascii', 'ignore').split(',')
        self.record['company'] = self.get_company_name()
        self.record['recipients'] = 0

    def get_company_name(self):
        self.cur.execute("""SELECT name FROM company
                        WHERE company_id = %s""" % self.record['company'])
        comp = self.cur.fetchall()[0][0]
        if comp == 0:
            comp = 'N/A'
        return comp

    def get_recip_count(self):
        recip_count = 0
        for _id in self.record['list_ids']:
            self.cur.execute("""SELECT COUNT(id)
                                FROM recipient
                                WHERE list_id = %s""" % _id)
            recip_count += self.cur.fetchall()[0][0]
        return recip_count


class Recipient(Base):
    """
    Returns a recipient record containing:
        {
            recipient_id: int,
            first_name : str, (consider changing to just name or changing other tables for consistency)
            last_name: str,
            email : str,
            date_added: int,
            list_ids : str (convert to list)
        }

    """
    def __init__(self, conn, cur, _id):
        super(Recipient, self).__init__(conn, cur, _id)
        self.record = self.get_result_dict('recipient')
        self.record['date_added'] = unix_to_local(self.record['date_added'])    

#class Template(Base):
