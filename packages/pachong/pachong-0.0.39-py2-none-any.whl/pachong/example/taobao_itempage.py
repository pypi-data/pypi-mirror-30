#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/6/18
# @File  : [pachong] taobao_itempage.py


from __future__ import absolute_import
from __future__ import unicode_literals

import sys

from pachong.crawler.taobao import Taobao
from pachong.database.mongodb import MongoDB
from pachong.fetcher import Browser

args = sys.argv[1:]
nfile = int(args[0])

# fetcher = Browser(proxy='localhost:3128')
fetcher = Browser('firefox')
# fetcher = Browser(proxy='13.56.211.230:3128')
crawler = Taobao('wanghong', 'taobao_items', fetcher=fetcher, Database=MongoDB).import_input('itemids{}.txt'.format(nfile))
    # .login()

crawler.crawl('itempage')
fetcher.session.close()