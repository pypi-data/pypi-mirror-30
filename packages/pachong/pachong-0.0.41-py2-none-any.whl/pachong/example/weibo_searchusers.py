#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/28/18
# @File  : [pachong] weibo_searchusers.py


from __future__ import absolute_import
from __future__ import unicode_literals

from pachong.crawler import Weibo
from pachong.database.mongodb import MongoDB
from pachong.fetcher import Browser

fetcher = Browser('firefox')
crawler = Weibo('wanghong', 'searchkeywords3', output='keyweibos', fetcher=fetcher, Database=MongoDB)\
    .import_input(input_list=['上新 店铺']) \
    .login('0012028475117', 'Cc19900201')

crawler.crawl('searchweibos')