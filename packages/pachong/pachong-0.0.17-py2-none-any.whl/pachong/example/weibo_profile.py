#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/29/18
# @File  : [pachong] weibo_profile.py


from __future__ import absolute_import
from __future__ import unicode_literals

from crawler import Weibo
from database.mongodb import MongoDB
from fetcher import Requests

project = 'wanghong'
# project = 'test'
input_ = 'taobaouser_from_weibo'
fetcher = Requests()

username = '0012028475117'
# username = '0016095945117'

crawler = Weibo(project, input_, fetcher=fetcher, Database=MongoDB) \
    .login(username, 'Cc19900201')
    # .import_input(input_list=['1866833821'], update=True)
    # .import_input(filepath='profile', update=True)\


crawler.crawl('profile')
