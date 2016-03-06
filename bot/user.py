import psycopg2
from psycopg2.extras import DictCursor
from hashlib import sha1


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class User(object):

    def __init__(self, host, database, user, password):
        self.conn = psycopg2.connect(database=database, user=user, password=password, host=host)

        #CREATE TABLE users (id int, mode varchar(30),zoom int,format varchar(30),language varchar(10))

    def get_user(self, identifier, group=False):
        shaid = sha1(str(identifier)).hexdigest()
        cur = self.conn.cursor(cursor_factory=DictCursor)
        if group:
            cur.execute('SELECT * FROM groups WHERE shaid = %s LIMIT 1', (shaid,))
        else:
            cur.execute('SELECT * FROM users WHERE shaid = %s LIMIT 1', (shaid,))
        d = cur.fetchone()
        cur.close()
        data = dict()
        if d is None:
            return self.get_defaultconfig()
        else:
            data.update(d)
            if 'lang' not in d:
                data['lang'] = 'en'
                data['lang_set'] = False
            else:
                data['lang_set'] = True
            if data['lang'] is None:
                data['lang'] = 'en'
                data['lang_set'] = False
            return data

    def set_field(self, identifier, field, value, group=False):
        shaid = sha1(str(identifier)).hexdigest()
        cur = self.conn.cursor(cursor_factory=DictCursor)
        if group:
            cur.execute("SELECT count(shaid) as count FROM groups WHERE shaid = %s", (shaid,))
        else:
            cur.execute("SELECT count(shaid) as count FROM users WHERE shaid = %s", (shaid,))
        num = cur.fetchone()
        if num['count'] == 0:
            if group:
                cur.execute("INSERT INTO groups (shaid,{0}) VALUES (%s,%s)".format(field), (shaid, value))
            else:
                cur.execute("INSERT INTO users (shaid,{0}) VALUES (%s,%s)".format(field), (shaid, value))
        else:
            if group:
                cur.execute("UPDATE groups SET {0} = %s WHERE shaid = %s ".format(field), (value, shaid))
            else:
                cur.execute("UPDATE users SET {0} = %s WHERE shaid = %s ".format(field), (value, shaid))
        self.conn.commit()
        cur.close()
        return cur.rowcount != 0

    def get_defaultconfig(self):
        return {'lang': 'en', 'mode': 'normal', 'lang_set': False, 'onlymentions': True}

    def close(self):
        self.conn.close()
