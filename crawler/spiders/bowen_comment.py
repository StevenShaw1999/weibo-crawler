import random
import scrapy


import scrapy
import json
from weibo.items import PeopleItem, StatusesItem, CommentItem
import re

import time

class ActorBowenSpider(scrapy.Spider):
    name = 'bowen_comment'
    allowed_domains = ['w.weibo.cn']
    start_urls = ['http://m.weibo.cn/u/3664122147']
    usr_id = start_urls[0].split('/')[-1]

    def start_requests(self):
        '''首先请求第一个js文件，包含有关注量，姓名等信息'''
        js_url = 'https://m.weibo.cn/comments/hotflow?id=4811146617424110&mid=4811146617424110&max_id=138862379869996'
        #js_url = 'https://m.douban.com/rexxar/api/v2/movie/34874432/interests?count=20&order_by=hot&anony=0&start=0&ck=&for_mobile=1'
        self.comments_url = js_url
        yield scrapy.Request(url=js_url + '&max_id_type=0',
                             callback=self.parse_comments_next,
                             dont_filter=True)

    def parse_info(self, response):
        #print('Here')
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
                          user_id=user_id,
                          follow_count=follow_count,
                          followers_count=followers_count,
                          description=description,
                          statuses_count=statuses_count,
                          verified=verified,
                          verified_reason=verified_reason)
        yield item

        weibo_containerid = str(
            js['data']['tabsInfo']['tabs'][1]['containerid'])
        con_url = '&containerid=' + weibo_containerid
        next_url = response.url + con_url
        print(next_url)
        #buffer_list = []
        yield scrapy.Request(url=next_url,
                             callback=self.parse_wb,
                             dont_filter=True,)
                             #meta={
                             #   'buffer_list':  buffer_list
                             #})

    def parse_wb(self, response):
        try:
            js = json.loads(response.text)
            datas = js['data']['cards']
            for data in datas:
                # 去掉推荐位和标签位
                if len(data) == 4 or 'mblog' not in data:
                    continue
                edit_at = data['mblog']['created_at']
                text = data['mblog']['text']
                reposts_count = data['mblog']['reposts_count']
                comments_count = data['mblog']['comments_count']
                attitudes_count = data['mblog']['attitudes_count']
                statues_id = str(data['mblog']['id'])
                origin_url = data['scheme'].split('?')[0]

                item = StatusesItem(edit_at=edit_at,
                                    text=text,
                                    reposts_count=reposts_count,
                                    comments_count=comments_count,
                                    attitudes_count=attitudes_count,
                                    statues_id=statues_id,
                                    origin_url=origin_url)
                yield item
            if 'since_id' not in js['data']['cardlistInfo']:
                return
            since_id = str(js['data']['cardlistInfo']['since_id'])
            next_url = ''
            if 'since_id' not in response.url:
                next_url = response.url + '&since_id=' + since_id
            else:
                next_url = re.sub(r'since_id=\d+', 'since_id=%s' %
                                  since_id, response.url)

        except Exception as ret:
            print("=" * 40)
            print("这里出错了: %s" % ret)
            print("="*40)
            print(js)
            print("=" * 40)

        print(next_url)
        yield scrapy.Request(url=next_url,
                             callback=self.parse_wb,
                             dont_filter=True,)
                             #meta={
                             #   'buffer_list': since_id_buffer
                             #})
        

        self.comments_url = 'https://m.weibo.cn/comments/hotflow?id={0}&mid={1}'.format(statues_id, statues_id)
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

        try:
            js = json.loads(response.text)['data']
        except Exception as ret:
            print(response)
            print('Load json failed!: ', ret)
            return
        try:
            max_id_val =  str(js['max_id'])
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
            print('Parse json data failed!: ', ret)
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
                                    total_number=total_number)
                    yield item
                except Exception as ret:

                    print('Parse comment data failed!: ', ret)
                    continue

            #max_id = "&max_id=" + str(js['data']['max_id'])
            #max_id_type = '&max_id_type=' + str(js['data']['max_id_type'])

        if max_id is not None:
            print("=" * 40)
            print(max_id)
            print(max_id_type)
            print("=" * 40)
            if max_id_val == '0':
                return
            time.sleep(random.uniform(0, 1))
            print(self.comments_url + max_id + max_id_type)
            yield scrapy.Request(url=self.comments_url + max_id + max_id_type,
                                callback=self.parse_comments_next,
                                dont_filter=True
                                #priority = 10
            )
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
                                    total_number=total_number)
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