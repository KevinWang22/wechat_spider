# -*- coding: utf-8 -*-
import redis
import pymysql


# 微信公众号首页的地址，没有cookie的时候是登录界面，有cookie的时候从重定向的url中可以拿到token
index_url = 'https://mp.weixin.qq.com'

# 在超链接中搜索公众号时调用的接口，需要提供token和query, action=search_biz，返回的列表包含公众号的fakeid
search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz'

# 查询公众号所有文章调用的接口，返回文章列表，包含标题，aid，内容url，需提供token和fakeid, action=list_ex
paper_list_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg'

# 公众号文章详细信息的接口，返回json字符串，包含点赞，阅读数等，url需要拼接get_detail_url_params返回的参数
# 同时还需要提供表单数据，包括：__biz, mid, sn, idx, appmsg_type=9, is_read_only=1, is_temp_url=0
paper_detail_url = 'https://mp.weixin.qq.com/mp/getappmsgext'


def save_redis(infos):
    client = redis.StrictRedis()

    # type为count时，infos存的是文章数量
    if infos['type'] == 'count':
        existed_count = 0 if not client.exists((infos['biz']+'count').encode()) \
            else client.spop((infos['biz']+'count').encode())
        client.sadd((infos['biz']+'count').encode(), infos['count'])
        return existed_count
    elif infos['type'] == 'double':
        # info存的是文章的标题，同时做一次查重
        return client.sadd((infos['biz']+'paper').encode(), infos['paper'])
    else:
        if client.exists((infos['biz']+'clawed_page').encode()):
            client.spop((infos['biz']+'clawed_page').encode())
        client.sadd((infos['biz']+'clawed_page').encode(), infos['clawed_page'])


def save_biz_paper(infos):
    if not infos:
        print('info为空')
        return 0
    try:
        db = pymysql.connect('localhost', 'root', 'as9754826', 'wechat_biz')
    except Exception as e:
        print(e)
        return 0
    else:
        cursor = db.cursor()
        keys = []
        values = []
        # print(infos)
        for key, value in infos.items():
            # print('key', key)
            keys.append(key)
            # print('value', value)
            values.append('"' + value + '"')
        key_str = ','.join(keys)
        value_str = ','.join(values)
        # print(value_str)
        sql = f'insert into biz ({key_str}) values ({value_str})'
        # print(sql)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            return 0

        db.close()
        return 1


def get_clawed_page(biz):
    client = redis.StrictRedis()
    clawed_page = 0 if not client.exists((str(biz) + 'clawed_page').encode()) else \
        client.spop((str(biz) + 'clawed_page').encode())
    return clawed_page



