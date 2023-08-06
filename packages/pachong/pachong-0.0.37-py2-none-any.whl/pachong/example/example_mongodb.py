#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/16/18
# @File  : [pachong] example_mongodb.py


from pachong.database import MongoDB

db = MongoDB('wanghong', 'users')
print(db.find('2045908335')['weibos'])
db2 = MongoDB('wanghong', 'users_full')

current_ids = {doc['_id'] for doc in db2.find_all({})}
for doc in db.find_all({}):
    if doc['_id'] in current_ids:
        db2.update(doc['_id'], doc)
    else:
        db2.insert(doc)


n_followers = [doc.get('n_followers', 0) for doc in db2.find_all({})]
import pandas
tar = pandas.DataFrame(n_followers)
tar.describe()


# uids = {user['_id'] for user in a}
# with open('taobaouser_from_weibo.txt', 'w') as o:
#     [o.write(uid + '\n') for uid in uids]

MongoDB('wanghong', 'taobao_items').update('559774227824', )

for item in db2.find_all({'$nor': [{'winfo': {'$regex': '(品牌主理人|工作室创始人)'}},
                                   {'pinfo': {'$regex': '(品牌主理人|工作室创始人)'}}]}):
    db2.drop(item['_id'])

for item in db2.find_all({'$and': [{'n_followers': {'$gte': 338}},
                                   {'n_weibos': {'$gte': 40}}]}):
    db.insert(item)

for item in db.find_all({'task.shopid.status': 'error'},['task.shopid.traceback']):
    print item


a = db.get({'task.timeline.status': 'error'})
print(a['task']['timeline']['traceback'])
test = MongoDB('test', 'user')
for item in test.get_all(): print(item)
test.insert({'_id': 1, 'test': [('h额呵呵', 1), ('啊哈哈哈', 'http')]})
a = test.get(1)
for item in a['test']:
    print(item[0])
    print(item[1])



import pymongo
from sshtunnel import SSHTunnelForwarder

MONGO_HOST = "10.0.1.29"
MONGO_PORT = 27017
MONGO_DB = "test"
MONGO_USER = "cchen"
MONGO_PASS = "Cc19900201"

db = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
db['test']['test'].insert({'b': 'haha'})
a = db['test']['test'].find()
from tqdm import tqdm
with tqdm(a, total=a.count()) as bar:
    for b in bar:
        print(b)
a.count()

a=a.skip(1)
a.next()

db['test']['test'].update_one({'b':'haha'}, {'$set': {'d': 'hehe'}})

server = SSHTunnelForwarder(
    MONGO_HOST,
    remote_bind_address=('127.0.0.1', 27017)
)

server.start()

client = pymongo.MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port
db = client[MONGO_DB]
db['test'].insert({'a': 'haha'})

server.stop()




from glob import glob
import random
import math
exclude_list = []
for fp in glob('/Users/cchen/GoogleDrive/porkspace/packages/pachong/pachong/itemids*.txt'):
    with open(fp, 'r') as i:
        exclude_list += [line.strip() for line in i]

db = MongoDB('wanghong', 'taobao_items')
with open('/Users/cchen/GoogleDrive/porkspace/packages/pachong/pachong/itemids15.txt', 'r') as i:
    samples = [_id.strip() for _id in i if _id.strip()]
ids = [doc['_id'] for doc in db.find_all({'task.comments.status': {'$in': ['done', 'error']},
                                          'task.itempage.status': {'$nin': ['done', 'error']},
                                          '_id': {'$in': samples}})]
# ids = ids[-20000:]
ids = random.sample(ids, len(ids))
len_per_file = 75
for i_file in range(min(int(math.ceil(len(ids) * 1./len_per_file)), 15)):
    with open('itemids{}.txt'.format(i_file), 'w') as f:
        this_ids = ids[i_file * len_per_file: (i_file + 1) * len_per_file]
        [f.write(_id + '\n') for _id in this_ids]

docs = [doc for doc in db.find_all()]
docs = random.sample(docs, len(docs))
len_per_file = 57
import json
for i_file in range(min(int(math.ceil(len(docs) * 1./len_per_file)), 20)):
    with open('/Users/cchen/Downloads/wh/users{}.json'.format(i_file), 'w') as f:
        this_docs = docs[i_file * len_per_file: (i_file + 1) * len_per_file]
        [f.write(json.dumps(doc) + '\n') for doc in this_docs]


db = MongoDB('wanghong', 'taobao_comments')
item_ids = {item['itemid'] for item in db.find_all(fields=['itemid'])}
db2 = MongoDB('wanghong', 'taobao_items')
items = [item for item in db2.find_all()]
db2.drop_field({'_id': {'$nin': list(item_ids)}}, 'task.comments')


import json
db = MongoDB('wanghong', 'taobaouser_from_weibo')
for fp in glob('/Users/cchen/GoogleDrive/porkspace/*t.json'):
    with open(fp, 'r') as i:
        for line in i:
            jline = json.loads(line.strip())
            _id = jline['_id']
            db.update(_id, jline)


import json
from glob import glob
db = MongoDB('wanghong', 'taobao_items')
# db2= MongoDB('wanghong', 'taobao_comments')
for fp in glob('/Users/cchen/GoogleDrive/porkspace/*item.json'):
    with open(fp, 'r') as i:
        for line in i:
            jline = json.loads(line.strip())
            _id = jline['_id']
            if 'task' not in jline:
                continue
            task = jline.pop('task')
            input_ = db.find(jline['_id'])
            input_task = input_.get('task', {})
            input_task.update(task)
            input_.update(jline)
            input_['task'] = input_task
            db.update(jline['_id'], input_)
            # if jline.get('task', {}).get('comments',{}).get('status') == 'done':
            #     db.update(jline['_id'], {'task.comments.status': 'done'})


db = MongoDB('wanghong', 'users')
db.drop_field_all(field='task.shopid_manual.status')


db.find_all({'task.comments.status': {'$ne':'done'},
             'task.itempage.status': {'$ne': 'done'}}).count()

#
# db1 = MongoDB('wanghong', 'users')
# uids = {target['_id'] for target in db1.find_all(fields=['_id'])}
db2 = MongoDB('wanghong', 'keyweibos')
# for target in db2.find_all(fields=['_id', 'uid']):
#     uids2 = {target['uid'] for target in db2.find_all(fields=['_id', 'uid'])}
#         db2.drop(target['_id'])

db3 = MongoDB('wanghong', 'taobaouser_from_weibo')
db3.drop_field_all('task.profile')
ids = [target['_id'] for target in db3.find_all({'task.weibostore.status': {'$ne': 'done'}}, fields=['_id', 'uid'])]