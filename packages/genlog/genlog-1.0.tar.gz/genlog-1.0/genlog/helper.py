#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : helper.py
@desc    :
            1）指定造数据的 client 的个数
            2）指定 client 造数据的时间间隔（秒）
            3）指定需要收集的用户最大数目
            4）指定 flume 的 host:port
@time    : 18-3-18 下午12:10
"""

import argparse
import sys

from __init__ import __description__, __version__
from exception import *

class Helper:

    def __init__(self):
        self._client_num = 100
        self._interval = 0
        self._user_num = 10000
        self._remote_host_list = []
        self._show = False


    def help(self):
        parser = argparse.ArgumentParser(description=__description__)
        parser.add_argument('-v', '--version', action='store_true', help='output version and exit')

        parser.add_argument('-n', '--client_num', type=int, default=888, help='the num of client that generate logs')
        parser.add_argument('-i', '--interval', type=int, default=60000,
                            help='the time(ms) that a client show wait before next generating logs')
        parser.add_argument('-u', '--user_num', type=int, default=10000, help='the num of user that will be collected')
        parser.add_argument('-l', '--remote_host_list', default="0.0.0.0:2018,0.0.0.0:2019,0.0.0.0:2020,0.0.0.0:2021",
                            help='remote host list that we send logs to (format: ip:port,ip:port...)')
        parser.add_argument('-s', '--show', action='store_true', help='show send logs info')

        # get arguments
        args = parser.parse_args()

        if args.version:
            print('genlog: ', __version__)
            sys.exit(0)

        def get_ip_port(host):
            try:
                ip =  host.split(':')[0]
                port = host.split(':')[1]
                return (ip, port)
            except IndexError:
                raise WrongFormatError("与标准格式ip:port不一致")

        if args.remote_host_list:
            host_list = args.remote_host_list.split(',')
            try:
                self._remote_host_list = [get_ip_port(host) for host in host_list]
            except WrongFormatError as e:
                print(e)
                sys.exit(1)

        if args.show:
            self._show = True

        if args.interval < 1000:
            print('interval must greater than 1000(ms)')
            sys.exit(2)

        self._client_num, self._interval, self._user_num = args.client_num, args.interval, args.user_num


    @property
    def client_num(self):
        return self._client_num

    @property
    def interval(self):
        return self._interval

    @property
    def user_num(self):
        return self._user_num

    @property
    def remote_host_list(self):
        return self._remote_host_list

    @property
    def show(self):
        return self._show
