#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/6/18
# @File  : [pachong] taobao_comments.py


from __future__ import absolute_import
from __future__ import unicode_literals

import sys

from pachong.crawler.taobao import Taobao
from pachong.database.mongodb import MongoDB
from pachong.fetcher import Browser

# args = sys.argv[1:]
# nfile = int(args[0])

with open('/Users/cchen/GoogleDrive/porkspace/packages/pachong/pachong/inputs/itemids16.txt', 'r') as i:
    input_list = [line.strip() for line in i if line.strip()]

fetcher = Browser('firefox', use_network=True, load_images=False)
crawler = Taobao('wanghong', 'taobao_items', output='taobao_comments', fetcher=fetcher, Database=MongoDB)\
    .import_input(input_list=input_list, update=True)
    # .import_input('itemids{}.txt'.format(nfile))#.import_input(input_list=['559667455412'])
crawler.crawl('comments')
fetcher.session.close()

fetcher = Browser('firefox')
crawler = Taobao('wanghong', 'taobao_items', fetcher=fetcher, Database=MongoDB)\
    .import_input(input_list=input_list, update=True)
crawler.crawl('itempage')
fetcher.session.close()