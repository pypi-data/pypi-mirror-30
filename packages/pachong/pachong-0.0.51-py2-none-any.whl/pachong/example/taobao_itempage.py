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
from pachong.fetcher import Browser, Requests
from pushbullet import PushBullet
#
# args = sys.argv[1:]
# i_file = int(args[0])

# crawler = Taobao('wanghong', 'taobao_items', output='taobao_comments', fetcher=Requests(), Database=MongoDB)
# .import_input('items{}.json'.format(i_file), is_json=True)

while True:

    fetcher = Browser('firefox', use_network=True, load_images=False)
    crawler = Taobao('wanghong', 'taobao_items', output='taobao_comments', fetcher=fetcher, Database=MongoDB) \
        .import_input(input_list=['561204998278'], update=True) \
        .crawl('comments')
    # fetcher.session.close()
    if len(crawler.samples) == 0:
        break
#
# while True:
    fetcher = Browser('firefox')
    crawler = Taobao('wanghong', 'taobao_items', fetcher=fetcher, Database=MongoDB) \
        .crawl('itempage')
    fetcher.session.close()
    if len(crawler.samples) == 0:
        break
#
# pb = PushBullet('o.EXRbEibhhzjtfJdYuhseaWZDfeq3FLvo')
# pb.push_note('taobao{}'.format(i_file), 'done')


#
# import re
# import json
# b = a
#
# while True:
#     try:
#         json.loads(a)
#     except ValueError as e:
#         position = int(re.compile('\(char ([0-9]+)\)').search(e.args[0]).group(1))
#         a = re.sub('^' + re.escape(a[:position - 1]) + '\"([^"]+)\"', a[:position - 1] + '\\"\g<1>', a)
#
#
re.compile('\"content\":\"[^"]+\"[^"]+\"[}]]*,\"').search(a).group(0)
json.loads(re.sub('(\"content\":\"[^"]+)\"([^"]+\"[}]]*,\")', '\g<1>\g<2>', a))

print re.compile('\"content\":\"(.*?)[}]]*,\"').search(b).group(0)