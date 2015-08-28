import sqlite3


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
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM user WHERE id = ? LIMIT 1", (id,))
        data = cur.fetchone()
        cur.close()
        if data is None:
            return self.get_defaultconfig()
        else:
            if 'lang' not in data:
                data['lang'] ='en'
            if data['lang'] == None:
                data['lang'] = 'en'
            return data

    def set_field(self, id, field, value):
        cur = self.conn.cursor()
        cur.execute("SELECT count(id) as count FROM user WHERE id = ?", (id,))
        num = cur.fetchone()
        if num['count'] == 0:
            print "insert"
            cur.execute("INSERT INTO user (id,{0}) VALUES (?,?)".format(field), (id, value))
        else:
            cur.execute("UPDATE user SET {0} = ? WHERE id = ? ".format(field), (value, id))
        self.conn.commit()
        cur.close()
        return cur.rowcount != 0

    def get_defaultconfig(self):
        return {'lang': 'en','mode':'normal'}