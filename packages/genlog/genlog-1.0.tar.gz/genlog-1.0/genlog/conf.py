#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : conf.py
@desc    : 相关的配置信息
@time    : 18-3-16 上午11:17 
"""

from helper import Helper

helper = Helper()
helper.help()

client_num = helper.client_num
interval = helper.interval
user_num = helper.user_num
remote_host_list = helper.remote_host_list
verbose = helper.show

used_app_num = 15           # 假设所有用户使用的app最多只有15个

flumes = [("0.0.0.0", 2018), ("0.0.0.0", 2019), ("0.0.0.0", 2020), ("0.0.0.0", 2021)]

packages = [
    "QQ",
    "WeChat",
    "AliPay",
    "TMall",
    "TaoBao",
    "TIM",
    "TouTiao",
    "TopBuzz",
    "UC Browser",
    "Netease Music",
    "JinDong",
    "Baidu",
    "Didi",
    "IMOOC",
    "Weibo",
    "WPS Office",
    "BiliBili",
    "Chrome",
    "Firefox",
    "iQIYi",
    "YouKu"
]

package_num = len(packages)
