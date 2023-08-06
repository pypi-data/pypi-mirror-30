#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/22/18
# @File  : [pachong] weibostore_shopid.py


from __future__ import absolute_import
from __future__ import unicode_literals

from pachong.crawler.taobao import Taobao
from pachong.database.mongodb import MongoDB
from pachong.fetcher import Requests

project = 'wanghong'
# project = 'test'
input_ = 'taobaouser_from_weibo'
fetcher = Requests()
crawler = Taobao(project, input_, fetcher=fetcher, Database=MongoDB)#.import_input('itemids{}.txt'.format(i_file))


crawler.crawl('shopid2')