import random
import scrapy


import scrapy
import json
from weibo.items import PeopleItem, StatusesItem, CommentItem, CommentPeopleItem
import re
import redis

import time
from scrapy.utils.project import get_project_settings
from tqdm import tqdm
import logging

class ActorBowenSpider(scrapy.Spider):
    name = 'user_bowen'
    allowed_domains = ['w.weibo.cn']
    start_urls = ['http://m.weibo.cn/u/3664122147']
    usr_id = start_urls[0].split('/')[-1]

    
    def __init__(self, slice=None, *args, **kwargs):
        self.settings = get_project_settings()
        self.slice = int(slice)
        self.db = 0
        self.red = redis.Redis(host = self.settings.get('REDIS_HOST'), 
                               port = self.settings.get('REDIS_PORT'), 
                               password = self.settings.get('REDIS_PASSWORD'),
                               db = self.db) 
        self.max_id = 0
        self.mon_dict =  {
            'Jan': 1,
            'Feb': 2,
            'Mar': 3,
            'Apr': 4,
            'May': 5,
            'Jun': 6,
            'Jul': 7,
            'Aug': 8,
            'Sep': 9,
            'Oct': 10,
            'Nov': 11,
            'Dec': 12,
        }



    def start_requests(self):   
        # weibo scrapy crawl user_bowen -a slice=1 -a sub_slice=40 -s CLOSESPIDER_ERRORCOUNT=2

        '''首先请求第一个js文件，包含有关注量，姓名等信息'''
        """js_url = 'https://m.weibo.cn/comments/hotflow?id=4811146617424110&mid=4811146617424110&max_id=138862379869996'
        #js_url = 'https://m.douban.com/rexxar/api/v2/movie/34874432/interests?count=20&order_by=hot&anony=0&start=0&ck=&for_mobile=1'
        self.comments_url = js_url
        yield scrapy.Request(url=js_url + '&max_id_type=0',
                             callback=self.parse_comments,
                             dont_filter=True)"""
        #insert_status = self.red.sadd('weibo_comment_user', 5730194883)
        #print(insert_status)
        #total_len = 244078
        #sub_len = int(244078/25)
        with open('user_id.txt', 'r') as f:
            user_ids = f.readlines()
        user_ids = [item.strip('\n') for item in user_ids]
        print(len(user_ids))
        ll = len(user_ids)

        # 后16个从15%开始

        start_dict = {
            0: 1231088353,
            1: 1648878027,
            2: 1759769913,
            3: 1825971940,
            4: 1918825957,
            5: 2061650625,
            6: 2245267913,
            7: 2449248492,
            8: 2661406801,
            9: 2831630102,
            10: 3064629347,
            11: 3264623965,
            12: 3655586734,
            13: 3934012809,
            14: 5113048350,
            15: 5236463586
        }

        print(f'From {int(ll * (self.slice / 32))}-{int(ll * ((self.slice + 1) / 32))}')
        
        #print(f'From {self.slice * total_len + sub_len * self.sub_slice}-{self.slice * total_len + sub_len * self.sub_slice + self.sub_slice}')
        
        #self.red.spop('weibo_comment_user')
        #return
        #user_dicts = {}
        sub_list = user_ids[int(ll * (self.slice / 32)): int(ll * ((self.slice + 1) / 32))]
        if self.slice >= 16:
            sub_list = sub_list[int(len(sub_list) * 0.15):]
        pbar = tqdm(sub_list)
        for idx, user_id in enumerate(pbar):
            user_id = str(user_id, 'utf-8') if type(user_id) != str else user_id
            js_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + user_id
            pbar.set_description(f'Crawling: {js_url}')
            yield scrapy.Request(url=js_url,
                                callback=self.parse_info_only_bowen,
                                dont_filter=True,
                                priority=10)

        
        print(f'Finish {int(ll * (self.slice / 32))}-{int(ll * ((self.slice + 1) / 32))}')


    def parse_info_only_bowen(self, response):
        #print('Here')
        try:
            js = json.loads(response.text)
            infos = js['data']['userInfo']
            name = infos['screen_name']
            user_id = infos['id']
            follow_count = infos['follow_count']
            followers_count = infos['followers_count']
            description = infos['description']
            # 微博数
            statuses_count = infos['statuses_count']
            verified = infos['verified']
            verified_reason = ''
            weibo_containerid = str(
                js['data']['tabsInfo']['tabs'][1]['containerid'])
            con_url = '&containerid=' + weibo_containerid
            next_url = response.url + con_url
            print(next_url)
            #buffer_list = []
            yield scrapy.Request(url=next_url,
                                callback=self.parse_wb,
                                dont_filter=True,
                                priority=10,
                                meta={
                                    'user_id':  user_id,
                                    #'user_dicts': user_dicts
                                })
                                #meta={
                                #   'buffer_list':  buffer_list
                                #})
        
        except Exception as ret:
            print('Parse user_info failed!: ', ret)        

    def parse_info(self, response):
        #print('Here')
        try:
            js = json.loads(response.text)
            infos = js['data']['userInfo']
            name = infos['screen_name']
            user_id = infos['id']
            follow_count = infos['follow_count']
            followers_count = infos['followers_count']
            description = infos['description']
            # 微博数
            statuses_count = infos['statuses_count']
            verified = infos['verified']
            verified_reason = ''
            if verified == True:
                verified_reason = infos['verified_reason']
            item = PeopleItem(name=name,
                                follow_count=follow_count,
                                followers_count=followers_count,
                                description=description,
                                statuses_count=statuses_count,
                                verified=verified,
                                verified_reason=verified_reason,
                                type='weibouseritem'
                            )
            yield item
            #user_dicts = response.meta['user_dicts']
            #user_dicts[user_id] = 0
            weibo_containerid = str(
                js['data']['tabsInfo']['tabs'][1]['containerid'])
            con_url = '&containerid=' + weibo_containerid
            next_url = response.url + con_url
            print(next_url)
            #buffer_list = []
            yield scrapy.Request(url=next_url,
                                callback=self.parse_wb,
                                dont_filter=True,
                                priority=10,
                                meta={
                                    'user_id':  user_id,
                                    #'user_dicts': user_dicts
                                })
                                #meta={
                                #   'buffer_list':  buffer_list
                                #})
        
        except Exception as ret:
            print('Parse user_info failed!: ', ret)
            
        

    def parse_wb(self, response):
    
        user_id = response.meta['user_id']
        #user_dicts = response.meta['user_dicts']

        try:
            time_flag = True
            js = json.loads(response.text)
            datas = js['data']['cards']
            for data in datas:
                # 去掉推荐位和标签位
                if len(data) == 4 or 'mblog' not in data:
                    continue
                edit_at = data['mblog']['created_at']
                # Fri Nov 18 16:39:14 +0800 2022
                parse_date = edit_at.split(' ')
                if int(edit_at[-4:]) < 2023 or self.mon_dict[parse_date[1]] < 4:
                    time_flag = False
                    break
                else:
                    if self.mon_dict[parse_date[1]] == 4:

                        text = data['mblog']['text']
                        reposts_count = data['mblog']['reposts_count']
                        comments_count = data['mblog']['comments_count']
                        attitudes_count = data['mblog']['attitudes_count']
                        statues_id = str(data['mblog']['id'])
                        origin_url = data['scheme'].split('?')[0]
                        item = StatusesItem(user_id=user_id,
                                            edit_at=edit_at,
                                            text=text,
                                            reposts_count=reposts_count,
                                            comments_count=comments_count,
                                            attitudes_count=attitudes_count,
                                            statues_id=statues_id,
                                            origin_url=origin_url,
                                            type='weibostatusitem4')

                        if int(user_id) > self.max_id:
                            self.max_id = int(user_id)
                            logging.info(f'parse max id: {self.max_id}')
                        yield item
                #user_dicts[user_id] += 1

        except Exception as ret:
            print("=" * 40)
            print("这里出错了: %s" % ret)
            print("="*40)
        
        try:
            if time_flag:
                if 'cardlistInfo' not in js['data']:
                    print(js)
                    print(response.url)
                
                else:
                    since_id = str(js['data']['cardlistInfo']['since_id'])
                    next_url = ''
                    if 'since_id' not in response.url:
                        next_url = response.url + '&since_id=' + since_id
                    else:
                        next_url = re.sub(r'since_id=\d+', 'since_id=%s' %
                                        since_id, response.url)
                    print(user_id, next_url)
                    yield scrapy.Request(url=next_url,
                                        callback=self.parse_wb,
                                        dont_filter=True,
                                        priority=10,
                                        meta={
                                            'user_id':  user_id,
                                            #'user_dicts': user_dicts
                                        })
        
        except Exception as ret:
            print("=" * 40)
            print("这里出错了: %s" % ret)
            print("="*40)
        return
        self.comments_url = 'https://m.weibo.cn/comments/hotflow?id={0}&mid={1}&max_id_type=0'.format(statues_id, statues_id)
        time.sleep(random.uniform(0, 1))
        yield scrapy.Request(url=self.comments_url,
                             callback=self.parse_comments,
                             dont_filter=True)

# =========================================================================
# 下面这部分爬取每条微博的评论，
    def parse_comments(self, response):
        """js = json.loads(response.text)
        max_id = '&max_id=' + str(js['data']['max_id'])
        next_url = response.url + max_id
        print("=" * 40)
        print(next_url)
        yield scrapy.Request(url=response.url + max_id,
                             callback=self.parse_comments_next,
                             dont_filter=True)"""
        
        status_id = response.meta['bowen_status_id']
        status_user_id = response.meta['bowen_user_id']
        #user_dicts = response.meta['user_dicts']

        try:
            js = json.loads(response.text)['data']
        except Exception as ret:
            print(response)
            print('Load json failed!: ', ret)
            return
        """try:
            max_id_val =  str(js['max_id'])
            max_id = "&max_id=" + str(js['max_id'])
            max_id_type = '&max_id_type=' + str(js['max_id_type'])
        except Exception as ret:
            print('Next Parse max_id failed!: ', ret)
            max_id = None
            max_id_type = None
            return"""
    

        try:
            datas = js['data']
        except Exception as ret:
            print('Parse json data failed!: ', ret)
            datas = None
        
        if datas is not None:
            print(f'Parse comments for status {status_id} from user {status_user_id}')
            for comment in datas:
                try:
                    comment_people_id = comment['user']['id']
                    comment_time = comment['created_at']
                    text = comment['text']
                    comment_people_id = comment['user']['id']
                    comment_people_name = comment['user']['screen_name']
                    comment_likes = comment['like_count']
                    total_number = comment['total_number']
                    item = CommentItem(
                                    father_status_id = status_id,
                                    father_user_id = status_user_id,
                                    comment_time=comment_time,
                                    text=text,
                                    comment_people_id=comment_people_id,
                                    comment_people_name=comment_people_name,
                                    comment_likes=comment_likes,
                                    total_number=total_number,
                                    type = 'weibocommentitem')
                    yield item
                    insert_status = self.red.sadd('weibo_comment_user', comment_people_id)
                    #print(insert_status)
                    """js_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={0}'.format(comment_people_id)
                    print('Crawl user info and wb: ', js_url)
                    yield scrapy.Request(url=js_url,
                                        callback=self.parse_info,
                                        dont_filter=True,
                                        priority=10,
                                        )"""


                except Exception as ret:

                    print('Parse comment data failed!: ', ret)
                    continue


            #max_id = "&max_id=" + str(js['data']['max_id'])
            #max_id_type = '&max_id_type=' + str(js['data']['max_id_type'])

        """if max_id is not None:
            print("=" * 40)
            print(max_id)
            print(max_id_type)
            print("=" * 40)
            if max_id_val == '0':
                return
            
            return
            time.sleep(random.uniform(0, 1))
            print(self.comments_url + max_id + max_id_type)
            yield scrapy.Request(url=self.comments_url + max_id + max_id_type,
                                callback=self.parse_comments_next,
                                dont_filter=True
                                #priority = 10
            )"""
        #except Exception as ret:
        #    print("=" * 40)
        #    print("此处出错 comments！%s" % ret)
        #    print(response.text)
        #    print("=" * 40)

    def parse_comments_next(self, response):
        try:
            js = json.loads(response.text)['data']
        except Exception as ret:
            print(response)
            print('Next Load json failed!: ', ret)
            return
        try:
            max_id_val =  str(js['max_id'])
            if max_id_val == '0':
                return
            else:
                max_id = "&max_id=" + str(js['max_id'])
                max_id_type = '&max_id_type=' + str(js['max_id_type'])
        except Exception as ret:
            print('Next Parse max_id failed!: ', ret)
            max_id = None
            max_id_type = None
            return

        try:
            datas = js['data']
        except Exception as ret:
            print('Next Parse json data failed!: ', ret)
            datas = None
        
        if datas is not None:
            for comment in datas:
                try:
                    comment_time = comment['created_at']
                    text = comment['text']
                    comment_people_id = comment['user']['id']
                    comment_people_name = comment['user']['screen_name']
                    comment_likes = comment['like_count']
                    total_number = comment['total_number']
                    item = CommentItem(comment_time=comment_time,
                                    text=text,
                                    comment_people_id=comment_people_id,
                                    comment_people_name=comment_people_name,
                                    comment_likes=comment_likes,
                                    total_number=total_number,
                                    )
                    yield item
                except Exception as ret:

                    print('Next Parse comment data failed!: ', ret)
                    continue

            #max_id = "&max_id=" + str(js['data']['max_id'])
            #max_id_type = '&max_id_type=' + str(js['data']['max_id_type'])

        if max_id is not None:
            print("=" * 40)
            print(max_id)
            print(max_id_type)
            print("=" * 40)
            if str(js['max_id']) == '0':
                return
            time.sleep(random.uniform(0, 1))
            yield scrapy.Request(url=self.comments_url + max_id + max_id_type,
                                callback=self.parse_comments_next,
                                dont_filter=True
                                #priority = 10
            )