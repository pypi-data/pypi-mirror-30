#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/6/18
# @File  : [pachong] taobao_comments.py


from __future__ import absolute_import
from __future__ import unicode_literals

from pachong.crawler.taobao import Taobao
from pachong.database.mongodb import MongoDB
from pachong.fetcher import Browser

# fetcher = Requests(proxy='localhost:3129')
fetcher = Browser('firefox', use_network=True, load_images=False)
# fetcher = Browser(proxy='13.56.211.230:3128')
crawler = Taobao('wanghong', 'taobao_items_test', output='taobao_comments', fetcher=fetcher, Database=MongoDB)#.import_input(input_list=['559667455412'])
# crawler.profile = 'taobao_shops'
crawler.crawl('comments')
