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
from pushbullet import PushBullet


args = sys.argv[1:]
i_file = int(args[0])

while True:
    fetcher = Browser('firefox')
    crawler = Taobao('wanghong', 'taobao_items', fetcher=fetcher, Database=MongoDB)\
        .import_input('items{}.json'.format(i_file), is_json=True)

    crawler.crawl('itempage')
    fetcher.session.close()
    if len(crawler.samples) == 0:
        pb = PushBullet('o.EXRbEibhhzjtfJdYuhseaWZDfeq3FLvo')
        pb.push_note('items{}'.format(i_file), 'done')
        break