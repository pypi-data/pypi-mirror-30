#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : exception.py
@desc    : 定义一些简单的异常，用于友好地查错
@time    : 18-3-18 下午1:41 
"""

class WrongFormatError(Exception):
    def __init__(self, err_info):
        super().__init__(self)
        self.error_info = err_info

    def __str__(self):
        return self.error_info
