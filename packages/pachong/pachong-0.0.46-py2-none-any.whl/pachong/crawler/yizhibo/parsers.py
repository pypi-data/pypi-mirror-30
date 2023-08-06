#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 4/5/18
# @File  : [pachong] parsers.py

from __future__ import absolute_import
from __future__ import unicode_literals

import re
from datetime import datetime
from datetime import timedelta

from pachong.crawler.common.utils import keep_int


def parse_profile(fetcher, attributes='nick,avatar,pinfo,level,n_followers,n_fans'):
    if fetcher.find('img', class_='icon_404'):
        return None
    chong = {}
    profile = fetcher.find('div', class_='person_info')
    if 'nick' in attributes:
        nick = profile.find('div', class_='person_name')
        if nick:
            chong['nick'] = nick.get_text(strip=True)
    if 'avatar' in attributes:
        avatar = profile.find('div', class_='person_header').find('img')
        if avatar:
            chong['avatar'] = re.sub('@[^@]+\.jpg$', '',avatar.get('src', ''))
    if 'pinfo' in attributes:
        pinfo = profile.find('div', class_='person_intro')
        if pinfo:
            chong['pinfo'] = pinfo.get_text(strip=True, separator=u' ')
    if 'level' in attributes:
        level = profile.find('div', class_=re.compile('level_[0-9]+'))
        if level:
            chong['level'] = int(re.compile('level_([0-9]+)').search(' '.join(level.get('class', []))).group(1))

    social = fetcher.find('div', class_='person_concern')
    if 'n_followers' in attributes:
        n_followers = social.find('div', class_='concern_num')
        if n_followers:
            chong['n_followers'] = int(n_followers.find('span').get_text(strip=True))
    if 'n_fans' in attributes:
        n_fans = social.find('div', class_='fan_num')
        if n_fans:
            chong['n_followers'] = int(n_fans.find('span').get_text(strip=True))
    return chong


def parse_replaylist(fetcher, attributes='n_views,date,title,n_likes,n_messages,cover'):
    rooms = fetcher.find_all('li', class_='index_all_common')
    return [_parse_replay(room, attributes) for room in rooms]


def _parse_replay(room, attributes):
    chong = {}
    chong['_id'] = room.find('div', class_='scid').text
    if '照片' in room.find('div', class_='index_time').text:
        chong['type'] = 'photo'
    else:
        status = room.find('div', class_='index_state').get_text(strip=True)
        chong['type'] = 'replay' if '回放' in status else 'live'

    if 'n_views' in attributes:
        n_views = room.find('div', class_='index_num')
        if n_views:
            chong['n_views'] = keep_int(n_views.text)
    if 'date' in attributes:
        date = room.find('div', class_='index_time')
        if date:
            date_text = date.text
            chong['date'] = (datetime.utcnow() + timedelta(hours=8) -
                             (timedelta(hours=keep_int(date_text)) if '小时' in date.text else
                              timedelta(minutes=keep_int(date_text)))).strftime('%Y-%m-%d') \
                if '前' in date_text else re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}').search(date_text).group(0)
    if 'title' in attributes:
        title = room.find('div', class_='index_intro')
        if title:
            chong['title'] = title.get_text(strip=True)
    if 'n_likes' in attributes:
        n_likes = room.find('div', class_='index_zan')
        if n_likes:
            chong['n_likes'] = keep_int(n_likes.text)
    if 'n_messages' in attributes:
        n_messages = room.find('div', class_='index_msg')
        if n_messages:
            chong['n_messages'] = keep_int(n_messages.text)
    if 'cover' in attributes:
        cover = room.find('img', class_='index_img_main')
        if cover:
            chong['cover'] = re.sub('@.+$' , '', cover.get('src', ''))
    return chong

# def parse_usercard(usercard):
#     link = usercard.find('a', target='_blank')
#     memberid = parse_url_args(link.attrs['href'])['memberid']
#     weiboid = link.attrs.get('weibo_openid', '')
#     nickname = link.text.encode('utf-8')
#     level = re.sub('[^0-9]', '', ' '.join(usercard.find('div', class_='level').attrs['class']))
#
#     gold = usercard.find('span', class_='J_goldcoin')
#     gold = gold.text.encode('utf-8') if gold else ''
#     maxonline = usercard.find('span', class_='J_maxonline')
#     maxonline = re.sub(u'\u4eba', '', maxonline.text).encode('utf-8') if maxonline else ''
#
#     return [memberid, weiboid, nickname, level, gold, maxonline]
