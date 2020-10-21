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
    return client.srem((infos['biz_name'] + 'paper').encode(), infos['paper'])


def get_article_url(biz, is_continue=False):

    sql = f'select app_msg_url from biz where biz_name = "{biz}"'

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


if __name__ == '__main__':

    """deleting_key = '嬉游clawed_page'
    if del_redis_key(deleting_key):
        print('删除成功')"""

    """urls = get_article_url('发现旅行')

    if urls == 0 or not urls:
        print('查询失败')
    else:
        for url in urls:
            print(url[0])"""
    search_sql = f"select count(*) from biz where aid = '发现旅行'"
    conn = pymysql.connect('localhost', 'root', 'as9754826', 'wechat_biz')
    cur = conn.cursor()
    cur.execute(search_sql)
    print(cur.fetchone()[0])








