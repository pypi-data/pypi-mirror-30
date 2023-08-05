#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : main.py
@desc    :
@time    : 18-3-16 上午11:38
"""

import asyncio

from genlog.client import *
from genlog.conf import *

def init_client():
    flume_num = len(flumes)
    return (Client(flumes[randint(0,flume_num-1)]) for i in range(100))

async def run(client):
    while True:
        client.send_log_to_flume()
        await asyncio.sleep(interval/1000)

def main():
    loop = asyncio.get_event_loop()
    tasks = [run(client) for client in init_client()]
    loop.run_until_complete(asyncio.wait(tasks))

if __name__ == "__main__":
    main()
