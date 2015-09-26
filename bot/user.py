import sqlite3
from hashlib import sha1


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class User(object):

    def __init__(self, database):
        self.conn = sqlite3.connect(database)
        self.conn.row_factory = dict_factory
        #CREATE TABLE user (id int, mode varchar(30),zoom int,format varchar(30),language varchar(10))
    def get_user(self, id):
        shaid = sha1(str(id)).hexdigest()
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM user WHERE shaid = ? LIMIT 1", (shaid,))
        data = cur.fetchone()
        cur.close()
        if data is None:
            return self.get_defaultconfig()
        else:
            if 'lang' not in data:
                data['lang'] = 'en'
                data['lang_set'] = True
            if data['lang'] is None:
                data['lang'] = 'en'
                data['lang_set'] = False
            return data

    def set_field(self, id, field, value):
        shaid = sha1(str(id)).hexdigest()
        cur = self.conn.cursor()
        cur.execute("SELECT count(shaid) as count FROM user WHERE shaid = ?", (shaid,))
        num = cur.fetchone()
        if num['count'] == 0:
            cur.execute("INSERT INTO user (shaid,{0}) VALUES (?,?)".format(field), (shaid, value))
        else:
            cur.execute("UPDATE user SET {0} = ? WHERE shaid = ? ".format(field), (value, shaid))
        self.conn.commit()
        cur.close()
        return cur.rowcount != 0

    def get_defaultconfig(self):
        return {'lang': 'en', 'mode': 'normal'}

    def close(self):
        self.conn.close()
