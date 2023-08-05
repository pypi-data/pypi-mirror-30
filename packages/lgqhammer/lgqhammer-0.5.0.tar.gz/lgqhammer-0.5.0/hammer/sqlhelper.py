# -*- coding=utf-8 -*-

import pymysql


# db_config_temp
# db_config = {
#     'host': 'localhost',
#     'port': 3306,
#     'user': 'root',
#     'password': '123456',
#     'db': 'test',
# }
class SqlHelper(object):
    def __init__(self, **db_config):
        self.connection = pymysql.connect(cursorclass = pymysql.cursors.DictCursor, **db_config)
        self.db_name = db_config.get('db')

    def execute(self, command, args = None, commit = True):
        with self.connection.cursor() as cursor:
            cursor.execute(command, args)

        if commit:
            self.connection.commit()

    def select_db(self, db_name):
        self.db_name = db_name
        self.connection.select_db(db_name)

    def insert_datas(self, datas, table_name, db_name = None, commit = True):
        if len(datas) <= 0:
            return False

        keys = list(datas[0].keys())
        val_param = []
        for i, data in enumerate(datas):
            s = '(' + ",".join(["{0!r}".format(d if d is not None else '') for d in data.values()]) + ')'
            val_param.append(s)
        val_param = ','.join(val_param)
        key_param = ",".join(keys)

        if db_name is None:
            db_name = self.db_name

        command = """INSERT IGNORE INTO {db_name}.{table_name} ({keys}) values {val}""". \
            format(table_name = table_name, keys = key_param, val = val_param, db_name = db_name)
        with self.connection.cursor() as cursor:
            cursor.execute(command)
            if commit:
                self.connection.commit()
            return True

    def update_datas(self, datas, table_name, update_keys = list([]), db_name = None, commit = True):
        if len(datas) <= 0:
            return False
        keys = list(datas[0].keys())
        val_param = []
        for i, data in enumerate(datas):
            s = '(' + ",".join(["{0!r}".format(d if d is not None else '') for d in data.values()]) + ')'
            val_param.append(s)
        val_param = ','.join(val_param)
        key_param = ",".join(keys)
        update_param = ', '.join(['%s=VALUES(%s)' % (k, k) for k in update_keys])

        if db_name is None:
            db_name = self.db_name

        command = """INSERT IGNORE INTO {db_name}.{table_name} ({keys}) values {val} ON DUPLICATE KEY UPDATE {update}""". \
            format(table_name = table_name, keys = key_param, val = val_param, db_name = db_name, update = update_param)
        with self.connection.cursor() as cursor:
            cursor.execute(command)
            if commit:
                self.connection.commit()
            return True

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

    def query(self, command):
        with self.connection.cursor() as cursor:
            cursor.execute(command)
            data = cursor.fetchall()
            return data

    def query_one(self, command):
        with self.connection.cursor() as cursor:
            cursor.execute(command)
            data = cursor.fetchone()
            return data

    def is_exists(self, table_name):
        command = "SHOW TABLES LIKE '%s'" % table_name
        with self.connection.cursor() as cursor:
            cursor.execute(command)
            data = cursor.fetchone()
            return True if data is not None else False

    def check_table_exists(self, table_name, db_name = None):
        if db_name is None:
            db_name = self.db_name

        command = """SELECT * FROM information_schema.tables WHERE table_schema = '{db_name}' AND table_name = '{table_name}';""".format(
            db_name = db_name, table_name = table_name)
        with self.connection.cursor() as cursor:
            cursor.execute(command)
            data = cursor.fetchone()
            return True if data is not None else False
