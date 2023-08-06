#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/28/18
# @File  : [pachong] weibostore_taobaourls.py


from __future__ import absolute_import
from __future__ import unicode_literals

import sys

from pachong.crawler import Weibo
from pachong.database.mongodb import MongoDB
from pachong.fetcher import Requests

args = sys.argv[1:]
i_file = args[0]


project = 'wanghong'
# project = 'test'
input_ = 'taobaouser_from_weibo'
fetcher = Requests()
crawler = Weibo(project, input_, fetcher=fetcher, Database=MongoDB).import_input('itemids{}.txt'.format(i_file))


crawler.crawl('weibostore')