#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : client.py
@desc    : 将日志信息发送到相应的flume agent
@time    : 18-3-16 上午11:48
"""

import json
import socket
import time
from datetime import datetime
from random import randint, randrange

from genlog.conf import *

class Client:
    def __init__(self, remote_host):
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.remote_host = remote_host

    def send_log_to_flume(self):
        for i in range(randint(100,1000)):
            self.send_log()

    def send_log(self):
        log_data = self.gen_log().encode("utf-8")
        try:
            self.client_sock.sendto(log_data, self.remote_host)
            if verbose:
                print(log_data)
        except socket.gaierror:
            print("Name or service not known")
           # sys.exit(1)
        except OverflowError as e:
            print(e)
            # print('port must be 0-65535')
           # sys.exit(2)

    def gen_log(self):
        user_id = randint(1, user_num)
        day = datetime.now().strftime("%Y-%m-%d")
        begintime = int(round(time.time()))
        # 每 10 分钟收集一次信息
        endtime = begintime + interval
        data = []
        # 随机生成用户使用的APP信息
        active_time = 0
        for i in range(randint(1, used_app_num)):
            try:
                active_time = randint(1000, interval-active_time)
            except ValueError:
                break
            package_info = {
                "package": packages[randrange(package_num)],
                "activetime": randint(6000, interval)
            }
            data.append(package_info)

        user_behavior_log = {
            "userId": user_id,
            "day": day,
            "begintime": begintime,
            "endtime": endtime,
            "data": data
        }
        return json.dumps(user_behavior_log)
