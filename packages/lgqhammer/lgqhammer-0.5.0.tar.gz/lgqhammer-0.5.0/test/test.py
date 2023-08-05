# -*- coding=utf-8 -*-


import sys
import time
import logging
import os

sys.path.append(os.getcwd())
logging.basicConfig()
from hammer.sqlhelper import SqlHelper

db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'db': 'test',
}


def test_create_table():
    command = '''
            CREATE TABLE `test_test` (
          `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
          `name` varchar(10) DEFAULT NULL,
          `age` int(11) DEFAULT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8;
        '''
    sql.execute(command, True)


def test_select():
    command = ''''''


def test_insert():
    datas = [
        {
            'name': "a'b'c",
            'age': 1,
            'date': None,
        },
        {
            'name': 'a"b"c',
            'age': 1,
            'date': None,
        },
        {
            'name': 'a"b";\'c',
            'age': 1,
            'date': None,
        },
        {
            'name': "a\"blll\";\'c",
            'age': 1,
            'date': '2018',
        },
    ]

    sql.insert_datas(datas, table_name = 'test')


def test_update():
    datas = [
        {
            'id': 1,
            'name': "a'b'c",
            'age': 2,
            'date': None,
        },
        {
            'id': 2,
            'name': 'a"b"c',
            'age': 2,
            'date': None,
        },
        {
            'id': 3,
            'name': 'a"b";\'c',
            'age': 2,
            'date': None,
        },
        {
            'id': 4,
            'name': "a\"blll\";\'c",
            'age': 2,
            'date': '2018-01-02',
        },
    ]

    sql.update_datas(datas, table_name = 'test')


def test_is_exists():
    print(sql.is_exists('testdfads'))


def test_check_table_exists():
    print(sql.check_table_exists('test', db_name = 'tesdt'))


if __name__ == '__main__':
    sql = SqlHelper(**db_config)

    # test_insert()

    # test_update()
    # test_is_exists()
    # test_check_table_exists()

    datas = []
    for i in range(1, 3):
        data = {
            'id': i,
            'name': "vvv",
            'age': None,
            'date': None,
        }
        datas.append(data)
    print(datas)
    print(len(datas))
    start = time.time()
    # sql.insert_datas(datas, table_name = 'test')
    sql.update_datas(datas, table_name = 'test', update_keys = ['name', 'age'])
    print(time.time() - start)
