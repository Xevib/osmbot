import psycopg2
from psycopg2.extras import DictCursor
from hashlib import sha1


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class User(object):
    """
    Class that stores the user data into Postgres
    """
    def __init__(self, host, database, user, password, auto_init=True):
        """
        Class construcotr

        :param host: Postgres host
        :param database: Postgres database
        :param user: Postgres user
        :param password: Postgres password
        :param auto_init: Optional boolean to indicate if should do
        the auto init
        """

        self.conn = None

        if auto_init:
            self.init_user(host, database, user, password)

    def init_user(self, host, database, user, password):
        """
        Initializes connection into the database

        :param host: Database host
        :param database: Database name
        :param user: Database user
        :param password: Database password
        :return: None
        """
        self.conn = psycopg2.connect(
            database=database, user=user, password=password, host=host)

        # CREATE TABLE users (id int, mode varchar(30),
        # zoom int,format varchar(30),language varchar(10))

    def get_user(self, identifier, group=False):
        """
        Retrives the information from a user

        :param identifier: 
        :param group:
        :return:
        """
        shaid = sha1(str(identifier)).hexdigest()
        cur = self.conn.cursor(cursor_factory=DictCursor)
        if group:
            sql = 'SELECT * FROM groups WHERE shaid = %s LIMIT 1'
            cur.execute(sql, (shaid,))
        else:
            sql = 'SELECT * FROM users WHERE shaid = %s LIMIT 1'
            cur.execute(sql, (shaid,))
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
            sql = "SELECT count(shaid) as count FROM groups WHERE shaid = %s"
            cur.execute(sql, (shaid,))
        else:
            sql = "SELECT count(shaid) as count FROM users WHERE shaid = %s"
            cur.execute(sql, (shaid,))
        num = cur.fetchone()
        if num['count'] == 0:
            if group:
                sql = "INSERT INTO groups (shaid,{0}) VALUES (%s,%s)"
                cur.execute(sql.format(field), (shaid, value))
            else:
                sql = "INSERT INTO users (shaid,{0}) VALUES (%s,%s)"
                cur.execute(sql.format(field), (shaid, value))
        else:
            if group:
                sql = "UPDATE groups SET {0} = %s WHERE shaid = %s"
                cur.execute(sql.format(field), (value, shaid))
            else:
                sql = "UPDATE users SET {0} = %s WHERE shaid = %s"
                cur.execute(sql.format(field), (value, shaid))
        self.conn.commit()
        cur.close()
        return cur.rowcount != 0

    def get_defaultconfig(self):
        return {
            'lang': 'en',
            'mode': 'normal',
            'lang_set': False,
            'onlymentions': True
        }

    def close(self):
        self.conn.close()
