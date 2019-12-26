#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor
@author: Xiaodong Wang
@details: level总共分5个级别：debug < info< warning< error< critical
"""
import logging
from logging import handlers
from config_default import configs
import os
import threading

class Logger(object):
    """日志配置类。
        构造函数参数包含：
            filename: 日志保存位置
            level: 日志输出到屏幕的等级
            saveLevel: 日志保存到文件中的等级
            when: 日志保存到文件中的间隔的时间单位
            backCount: 日志保存到文件中的备份文件的个数
            fmt: 日志的输出格式
    Attributes:
        logger: 该类所维护的一个Logger实例。该类实例化并命名为log(举例子，该名称可以自定义)后，可以如下方法进行使用：
        log.logger.debug('debug')
        log.logger.info('info')
        log.logger.warning('警告')
        log.logger.error('报错')
        log.logger.critical('严重')
    """
    _instance_lock = threading.Lock()  #线程锁，使得该log可以应用于多线程环境
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#日志级别关系映射

    def __init__(self,filename,level='info',saveLevel='warning',when='midnight',backCount=10,fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(self.level_relations.get('debug'))#设置日志级别
        sh = logging.StreamHandler()  #往屏幕上输出
        sh.setFormatter(format_str)   #设置屏幕上显示的格式
        sh.setLevel(self.level_relations.get(level))
        th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器
        # 实例化TimedRotatingFileHandler
        # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setLevel(self.level_relations.get(saveLevel))  # 输入文件默认warning类型的日志
        th.setFormatter(format_str)#设置文件里写入的格式
        #加入日志过滤的handlers
        if not self.logger.hasHandlers():     #for spyder
            self.logger.addHandler(sh) #把对象加到logger里
            self.logger.addHandler(th)

    def __new__(cls, *args, **kwargs):    #保证该类只构造一次，以及线程安全的
        if not hasattr(Logger, "_instance"):
            with Logger._instance_lock:
                if not hasattr(Logger, "_instance"):
                    Logger._instance  = super().__new__(cls)
        return Logger._instance

LogDir = configs['LogDir'] #读取配置文件日志主目录
if not os.path.exists(LogDir):  #如果没有目录，则生成目录
    os.mkdir(LogDir)
LogName = configs['LogName'] #读取配置文件日志名字
LogLevel = configs['LogLevel'] #读取配置文件日志等级
saveLevel = configs['saveLevel'] #读取配置文件保存的日志等级
log = Logger(os.path.join(LogDir,LogName),level=LogLevel,saveLevel=saveLevel)   #该变量是其他文件引用是使用的变量名，已经按照配置文件config_default配置好了

if __name__ == '__main__':   #测试
#    log = Logger('all.log',level='debug')
    log.logger.debug('debug')
    log.logger.info('info')
    log.logger.warning('警告')
    log.logger.error('报错')
    log.logger.critical('严重')
#    Logger('error.log', level='error').logger.error('error')