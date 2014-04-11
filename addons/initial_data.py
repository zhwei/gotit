#!/usr/bin/env python
# -*- coding: utf-8 -*-

from redis2s import rds

data_dict = {

    'admin_weibo_id' : 2674044833,
    'log_file_path' : None,
    'mongoexport_path': None,
}


def init_data():

    for key in data_dict:

        value = data_dict[key]
        if value is None:
            value = raw_input("{} :".format(key))

        rds.set(key, value)

    print('ok')

if __name__ == '__main__':
    init_data()
