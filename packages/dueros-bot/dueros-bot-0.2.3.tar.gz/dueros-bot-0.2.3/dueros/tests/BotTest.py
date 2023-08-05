#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# description:
# author:jack
# create_time: 2017/12/31

"""
    desc:pass
"""
import random
import hashlib

import time
import datetime
import json
import logging
from dueros.Bot import Bot
from dueros.card.TextCard import TextCard
import os
import hashlib
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('bot')
import sys

class BotTest(Bot):

    def launchRequest(self):
        return {
            'card': TextCard(r'欢迎使用家居控制!请告诉我您要查找什么智能设备，比如查找我的空调'),
            'outputSpeech': r'<speak>欢迎使用家居控制!请告诉我您要查找什么智能设备，比如查找我的空调</speak>'
        }

    def searchRequest(self):

        self.ask('deviceName')

        card = TextCard('您要查找什么智能设备呢? 比如"查找我的空调"')
        card.addCueWords("百度")
        card.addCueWords("百度")
        card.addCueWords("百度")
        card.setAnchor("http://www.baidu.com", "百度")
        return {
            'card': card,
            'outputSpeech': '<speak>您要查找什么智能设备呢? 比如"查找我的空调"</speak>'
        }

    def controlRequest(self):
        self.ask('deviceName')
        # deviceName = self.getSlots('deviceName')
        # print('deviceName %s' % (deviceName))
        return {
            'card': TextCard('请告诉您的指令，比如调小空调风速、设置温度为30度'),
            'outputSpeech': '请告诉您的指令，比如调小空调风速、设置温度为30度'
        }

    def inquiry(self):
        return {
            'card': TextCard('请告诉您的指令，比如调小空调风速、设置温度为30度'),
            'outputSpeech': '请告诉您的指令，比如调小空调风速、设置温度为30度'
        }

    def __init__(self, data):
        super(BotTest, self).__init__(data)

        self.addLaunchHandler(self.launchRequest)

        self.addIntentHandler('dueros.device_interface.smart_device.control', self.controlRequest)

        self.addIntentHandler('dueros.device_interface.smart_device.search', self.searchRequest)
        # self.addIntentHandler('inquiry', self.inquiry)
    pass

if __name__ == '__main__':

    def launchData():
        with open("./json/launch.json", 'r', encoding='utf-8') as load_f:
            return load_f.read()

    def searchData():
        with open("./json/search2.json", 'r', encoding='utf-8') as load_f:
            return load_f.read()

    def controlData():
        with open("./json/control.json", 'r', encoding='utf-8') as load_f:
            return load_f.read()


    def controlData2():
        with open("./json/a.json", 'r', encoding='utf-8') as load_f:
            return load_f.read()


    def tt(data):
        print(data)
    data = controlData()
    bot = BotTest(data)
    # bot.setCallBack(tt)
    bot.run()
    pass
