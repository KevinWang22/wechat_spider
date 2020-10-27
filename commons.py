# -*- coding: utf-8 -*-
import redis
import pymysql
import time


# 微信公众号首页的地址，没有cookie的时候是登录界面，有cookie的时候从重定向的url中可以拿到token
index_url = 'https://mp.weixin.qq.com'

# 在超链接中搜索公众号时调用的接口，需要提供token和query, action=search_biz，返回的列表包含公众号的fakeid
search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz'

# 查询公众号所有文章调用的接口，返回文章列表，包含标题，aid，内容url，需提供token和fakeid, action=list_ex
paper_list_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg'

# 公众号文章详细信息的接口，返回json字符串，包含点赞，阅读数等，url需要拼接get_detail_url_params返回的参数
# 同时还需要提供表单数据，包括：__biz, mid, sn, idx, appmsg_type=9, is_read_only=1, is_temp_url=0
paper_detail_url = 'https://mp.weixin.qq.com/mp/getappmsgext'

client = redis.StrictRedis()


def save_redis(infos):

    if infos['type'] == 'double':
        # info存的是文章的标题，同时做一次查重
        return client.sadd((infos['biz']+'paper').encode(), infos['paper'])
    else:
        # type = clawed
        if client.exists((infos['biz']+'clawed_page').encode()):
            client.spop((infos['biz']+'clawed_page').encode())
        return client.sadd((infos['biz']+'clawed_page').encode(), infos['clawed_page'])


def save_biz_paper(infos):
    if not infos:
        print('info为空')
        return 0
    status = 1
    try:
        db = pymysql.connect('localhost', 'root', 'as9754826', 'wechat_biz')
    except Exception as e:
        status = 0
        print(e)
    else:
        cursor = db.cursor()
        # print(type(infos['aid']))
        search_sql = f"select count(*) from biz where aid = '{str(infos['aid'])}'"
        # print(search_sql)
        try:
            cursor.execute(search_sql)
        except Exception as e:
            print(f'select {infos["biz_name"]} error:', e)
            status = 0
        else:
            row_count = cursor.fetchone()[0]
            if not row_count:
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
                    print('insert infos error', e)
                    print('sql:', sql)
                    db.rollback()
                    status = 0
            else:
                update_sql = f"update biz set "
                for key, value in infos.items():
                    if key != 'aid':
                        update_sql += f"{key} = '{value}',"
                update_sql = update_sql[:-2] + f" where aid = '{infos['aid']}'"
                try:
                    cursor.execute(update_sql)
                    db.commit()
                except Exception as e:
                    print('update infos error:', e)
                    print('sql:', update_sql)
                    db.rollback()
                    status = 0

        db.close()
        return status


def get_clawed_page(biz):
    clawed_page = 0 if not client.exists((str(biz) + 'clawed_page').encode()) else \
        int(client.spop((str(biz) + 'clawed_page').encode()))
    client.sadd((str(biz) + 'clawed_page').encode(), str(clawed_page))
    return clawed_page


def del_redis_key(key):
    if not isinstance(key, bytes):
        key = key.encode()
    try:
        delete_result = client.delete(key)
    except Exception as e:
        print(e)
        delete_result = 0

    return delete_result


def del_redis_ele(infos):
    clawed_page = client.spop((infos['biz_name']+'clawed_page').encode())
    new_clawed_page = int(clawed_page) - 1
    client.sadd((infos['biz_name']+'clawed_page').encode(), str(new_clawed_page))
    return client.srem((infos['biz_name'] + 'paper').encode(), infos['app_msg_title'])


def get_article_url(biz, is_continue=False):

    sql = f'select app_msg_url from biz where biz_name = "{biz}"'

    # 需要从上次爬完的地方开始时，就从redis中取出上次的时间，把update_time早于上次的全部爬出来
    if is_continue:
        if client.exists(f'{biz}_last_claw_date'.encode()):
            last_claw_date = get_last_claw_date(biz)
            print('last_claw_date', last_claw_date)
            if last_claw_date:
                sql += f' and (date_format(update_time, "%Y-%m-%d") < "{str(last_claw_date)}" '
                sql += 'or update_time is Null)'

    try:
        db = pymysql.connect('localhost', 'root', 'as9754826', 'wechat_biz')
    except Exception as e:
        print(e)
        return 0
    else:
        cursor = db.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        db.close()
        print('url_list_len', len(results))
        return results


def save_num(aid, like_num=0, read_num=0, old_like_num=0):
    """
    把抓包抓到的数据保存到数据库中
    :param aid: 文章的唯一标识
    :param like_num:  在看数
    :param read_num:  阅读数
    :param old_like_num:  点赞数
    :return: save_status: 保存状态，0=失败，1=成功
    """

    save_status = 1
    search_sql = f"select count(*) from biz where aid = '{aid}'"
    try:
        conn = pymysql.connect('localhost', 'root', 'as9754826', 'wechat_biz')
    except Exception as e:
        print(e)
        save_status = 0
    else:
        cursor = conn.cursor()
        cursor.execute(search_sql)
        affect_row = cursor.fetchone()[0]
        if affect_row:
            update_sql = f"update biz set read_num = {read_num}, like_num = {old_like_num}, looking_num = {like_num} " \
                         f"where aid = '{aid}'"
            try:
                cursor.execute(update_sql)
                conn.commit()
            except Exception as e:
                print('update error:', e)
                conn.rollback()
                save_status = 0

        else:
            insert_sql = f"insert into biz (aid, read_num, looking_num, like_num) values ('{aid}', '{read_num}'," \
                         f" '{like_num}', '{old_like_num}')"
            try:
                cursor.execute(insert_sql)
                conn.commit()
            except Exception as e:
                print('insert read_num error:', e)
                conn.rollback()
                save_status = 0

        conn.close()
        return save_status


def save_last_claw_date(biz, claw_date):
    """保存上次爬取点赞数的时间，这样就能实现继续爬了"""
    try:
        if client.exists(f'{biz}_last_claw_date'.encode()):
            client.spop(f'{biz}_last_claw_date'.encode())
        client.sadd(f'{biz}_last_claw_date'.encode(), claw_date)
    except Exception as e:
        print('claw date save error:', e)


def get_last_claw_date(biz):
    try:
        claw_date = client.spop(f'{biz}_last_claw_date'.encode())
        client.sadd(f'{biz}_last_claw_date'.encode(), str(claw_date))
    except Exception as e:
        print('get last claw date error:', e)
        claw_date = None

    return str(claw_date, encoding='utf-8')










