#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Default configurations.
'''

import os

__author__ = 'Xiaodong Wang'

configs = {
    'LogDir':os.path.join('.','log'),  #日志保存的目录
    'LogName':'theLog.log',   #日志的名称
    'LogLevel':'info',       #日志的屏幕输出等级
    'saveLevel':'warning'       #日志的保存等级
}