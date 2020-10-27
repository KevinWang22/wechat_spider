# -*- coding:utf-8 -*-
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import re
import os
from commons import index_url, search_url, paper_list_url, save_redis, save_biz_paper, get_clawed_page, del_redis_ele
from proxy_spider import ProxySpider
import time
import datetime
import random


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 '
                  'Safari/537.36 QBCore/4.0.1301.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2875.116 Safari/537.36 NetType/WIFI '
                  'MicroMessenger/7.0.5 WindowsWechat '
}


class WechatSpider:
    """微信文章基本信息的爬取，从微信公众号搜索接口获取
    一次爬取页数有限制，目前最多一次爬取了70页
    超过限制会返回freq control的错误信息，需要停一会才能继续"""

    def __init__(self, user, pwd, biz, is_continue=False):
        """
        :param user:  公众号账号
        :param pwd:   登录密码
        :param biz:   需要爬取的公众号全称
        :param is_continue:  是否从上次结束的地方继续，默认False
        """
        self.user = user
        self.pwd = pwd
        self.biz = biz

        # 初始化代理ip
        self.proxy = ProxySpider()
        self.proxy.get_proxy_list()

        # 随机选择一个ip地址
        self.using_proxy = self.proxy.random_https_proxy()
        # print('inited proxy:', self.proxy.https_proxies)

        # 初始化cookie和token，有时效
        self.cookie = self.get_cookie()
        self.token = self.get_token()

        # 如果token没有获取到，就先停止，缓一缓再重新启动
        if self.token == 0:
            print('token获取失败，请稍后再试')
            exit()

        # request获取文章时使用的params
        self.paper_params = {
            'action': 'list_ex',
            'count': '5',
            'type': '9',
            'query': '',
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'token': str(self.token),
        }
        # 获取这个公众号以前爬了多少页了
        self.clawed_page = get_clawed_page(self.biz)
        print('clawed page:', self.clawed_page)

        # 如果不是从上次结束的地方继续的话，就设置开始位置为0
        if not is_continue:
            self.paper_params['begin'] = '0'
        else:
            # 每页有5次推送，则开始的位置为当前爬取的页面*5
            self.paper_params['begin'] = str(self.clawed_page * 5)

        # print(self.paper_params['begin'])
        # 没用上
        """self.wechat_cookie = {
                'rewardsn': '',
                'wxtokenkey': '777',
                'wxuin': '2810465319',
                'devicetype': 'android-22',
                'version': '27000735',
                'lang': 'zh_CN',
                'pass_ticket': 'O7I2sclKT1FQVSPHWdEwx+F7Ig4+4fr37wK1ay3MOXVSDsdIAWPqEkX+PctXV3a6',
                'wap_sid2': 'CKeYkbwKEooBeV9IQk90OFh1VkJNQVNpSnlIYmsxRGJzNFdTTFE5ZjFCNjQwZERXRE5LY1FKZ'
                            '29KMFZkLVRlallsNDdSSlJrRW5mdVRVTFEzajdQcE9NT09ybVJXUnRLRDdLRnJHdGE5MFU2NV'
                            'pnUnRxSjhtN0plOGlhZ0s1VHhaZXptdk1lZ1hiNm94Z1NBQUF+MJiIkPwFOA1AAQ==',
            }"""

    def login_official_account(self):
        """selenium模拟登录，同时把登录成功后的cookies保存下来"""
        driver = webdriver.Chrome(executable_path='chromedriver84.4147.exe')
        driver.get(index_url)
        time.sleep(5)
        # print(driver.page_source)

        # 打开网页之后切换到输入账号密码的界面
        driver.find_element_by_xpath('.//div[@class="login__type__container login__type__container__scan"]/a['
                                     '@class="login__type__container__select-type"]').click()
        # time.sleep(5)
        # 输入账号密码
        user_name = driver.find_element_by_name('account')
        user_name.clear()
        user_name.send_keys(self.user)
        password = driver.find_element_by_name('password')
        password.clear()
        password.send_keys(self.pwd)
        # time.sleep(5)
        driver.find_element_by_class_name('btn_login').click()

        # 点击登录之后需要扫码验证身份
        print('请扫码')
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'weui-desktop-account__info'))
            )
        except Exception as e:
            print(e)
        else:
            # 登录成功之后重新加载一次首页，同时把cookies保存下来，当天可用
            driver.get(index_url)
            cookies = driver.get_cookies()
            # print(cookies)
            user_cookies = {}

            # 把cookie转换成字典
            for cookie in cookies:
                user_cookies[cookie['name']] = cookie['value']

            # 转换为json字符串，并写到cookies.txt中，cookie每天都需要更新一次
            cookie_str = json.dumps(user_cookies)

            with open('cookies.txt', 'w', encoding='utf-8') as f:
                f.write(cookie_str)
            print('cookie已保存')
            driver.quit()

    def build_refer(self):
        """构造header里的refer"""
        refer = 'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10' \
                '&createType=0&token={}&lang=zh_CN '
        return refer.format(self.token)

    def get_token(self, retry_times=0):
        """requests请求一次首页，网站会重定向到登录状态的首页去，token在返回的url中
        :param retry_times: 重试次数，最多重试5次
        :return token: 获取到的token，如果重试超过5次返回0
        """

        print('token proxy:', self.using_proxy)
        try:
            token_response = requests.get(index_url, headers=headers, cookies=self.cookie,
                                          proxies=self.using_proxy, timeout=30)
        except Exception as e:
            print('token request error:', e)
            retry_times += 1
            if retry_times < 6:
                # 错了就换一个代理ip
                self.proxy.update_proxies(self.using_proxy['https'])
                self.using_proxy = self.proxy.random_https_proxy()
                # 避免太频繁请求被封
                time.sleep(random.randint(2, 5))
                return self.get_token(retry_times)
            else:
                return 0
        # print(token_response.url)
        else:
            # print(token_response.url)
            token = re.findall(r'&token=(\d+)', str(token_response.url), re.S)[0]
            return token

    def get_cookie(self):
        """获取cookie的方法"""

        # 如果没有登录过或者cookie过期的话，就需要进行一次登录操作，否则直接读取已保存的cookie信息
        if not os.path.exists('cookies.txt') or \
                time.strftime('%Y-%m-%d', time.localtime()) != \
                time.strftime('%Y-%m-%d', time.strptime(time.ctime(os.path.getmtime('cookies.txt')))):
            self.login_official_account()

        # 从保存的txt里读cookie数据
        with open('cookies.txt', 'r', encoding='utf-8') as f:
            cookies_str = f.read()

        # 转换成字典
        cookies = json.loads(cookies_str)
        return cookies

    def get_biz(self, retry_times=0):
        """调用公众号超链接的查询接口查询公众号"""

        search_header = headers
        # 查询的时候要提供refer，包含token
        search_header['refer'] = self.build_refer()
        search_params = {
            'query': self.biz,
            'token': str(self.token),
            'action': 'search_biz',
            'begin': '0',
            'count': '5',
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
        }
        print('biz proxy:', self.using_proxy)
        try:
            search_response = requests.get(search_url, headers=headers, cookies=self.cookie,
                                           proxies=self.using_proxy,
                                           params=search_params, timeout=30).json()
            print(search_response)
        except Exception as e:
            print('biz request error:', e)
            retry_times += 1
            if retry_times < 6:
                # 和token的逻辑一样
                self.proxy.update_proxies(self.using_proxy['https'])
                self.using_proxy = self.proxy.random_https_proxy()
                time.sleep(random.randint(2, 5))
                return self.get_biz(retry_times)
            else:
                return 0
        # print(search_response)
        else:
            if search_response['base_resp']['err_msg'] == 'ok':
                # 访问成功，会返回一个公众号列表，从中找出名称和提供的名称一致的公众号信息
                search_result = [search for search in search_response['list'] if search['nickname'] == self.biz][0]
            elif search_response['base_resp']['err_msg'] == 'invalid csrf token':
                # token过期了，需要更新
                self.token = self.get_token()
                search_result = self.get_biz()
            else:
                search_result = search_response['base_resp']['err_msg']
            print(search_result)
            return search_result

    def get_paper_count(self, search_response=None, retry_times=0):
        """获取公众号的推送数
        :param search_response: 公众号的信息，重试的时候就不用再获取一次
        :param retry_times: 重试次数
        :return paper_count: 推送数，为None的时候说明获取失败
        """

        paper_headers = headers
        paper_headers['refer'] = self.build_refer()

        # 获取公众号信息，需要里面的fakeid
        if not search_response:
            search_res = self.get_biz()
            if search_res == 0:
                print('公众号获取失败，请稍后再试')
                return None
            if isinstance(search_res, str):
                print('公众号获取结果：', search_res)
                return None
        else:
            search_res = search_response
        print(search_res)

        # 提取fakeid
        fakeid = search_res['fakeid']
        # self.paper_params['token'] = str(self.token)

        # fakeid更新到params中
        self.paper_params['fakeid'] = fakeid
        print('paper proxy:', self.using_proxy)
        # 获取总推送数，一次推送可能包含多篇文章
        try:
            paper_res = requests.get(paper_list_url, headers=paper_headers, cookies=self.cookie,
                                     params=self.paper_params, proxies=self.using_proxy, timeout=30)
        except Exception as e:
            print('paper request error:', e)
            retry_times += 1
            # 重试规则与上面一致
            if retry_times < 6:
                self.proxy.update_proxies(self.using_proxy['https'])
                self.using_proxy = self.proxy.random_https_proxy()
                time.sleep(random.randint(2, 5))
                return self.get_paper_count(search_response=search_res, retry_times=retry_times)
            else:
                print('文章数获取失败，请稍后再试')
                return None
        else:
            paper_res = paper_res.json()
            print('paper_res:', paper_res)

            # 推送数在这里
            paper_count = paper_res.get('app_msg_cnt')
            """infos = {
                'type': 'count',
                'biz': self.biz,
                'count': paper_count,
            }
            save_redis(infos)"""

            return paper_count

    def get_all_paper(self, page_num=None, retry_times=0):
        """调用文章查询接口获取所有文章
        :param page_num: 需要爬取的页数，重试的时候用,就不用再取一次
        :param retry_times: 重试次数
        """

        # 第一次调用的时候，调用get_paper_count获取推送数
        if not page_num:
            paper_count = self.get_paper_count()
            if not paper_count:
                print('需爬取文章数获取失败，请稍后再试')
                return None
            print(paper_count)
            # 每页5个推送，算出页数
            clawing_pages = paper_count // 5 + 1 - self.clawed_page + 1
            # self.paper_params['begin'] = '0'
        else:
            clawing_pages = page_num

        # 构造headers
        refer = self.build_refer()
        paper_header = headers
        paper_header['refer'] = refer
        print('clawing_pages', clawing_pages)
        while clawing_pages > 0:
            # retry_times = 0
            print('all_paper proxy:', self.using_proxy)
            try:
                response = requests.get(paper_list_url, headers=paper_header, cookies=self.get_cookie(),
                                        params=self.paper_params, proxies=self.using_proxy,
                                        timeout=30).json()
            except Exception as e:
                print(e)
                retry_times += 1
                if retry_times < 6:
                    self.proxy.update_proxies(self.using_proxy['https'])
                    self.using_proxy = self.proxy.random_https_proxy()
                    time.sleep(random.randint(3, 10))
                    return self.get_all_paper(clawing_pages, retry_times)
                else:
                    print(f'第{int(self.paper_params["begin"]) // 5}页获取失败，请稍后再试')
                    # 重试次数超过6次的时候也要更换代理，以便下一页爬取
                    """self.proxy.update_proxies(self.using_proxy['https'])
                    self.using_proxy = self.proxy.random_https_proxy()
                    continue"""
                    break
            else:
                try:
                    # 文章信息在这里
                    app_msg_list = response['app_msg_list']
                except KeyError:
                    # print('keyError', response)
                    # 请求次数过多的时候就会返回这个错误
                    if response['base_resp']['err_msg'] == 'freq control':
                        print('爬得太频繁了，先歇会')
                        break

                    # token过期了
                    elif response['base_resp']['err_msg'] == 'invalid csrf token':
                        new_token = self.get_token()
                        if new_token != 0:
                            self.paper_params['token'] = str(new_token)
                        else:
                            print('token重新获取失败')
                            break
                    else:
                        print('keyError', response)
                else:
                    for app_msg in app_msg_list:
                        # 从每个文章信息里提取需要的数据
                        saving_info = {
                            'aid': str(app_msg['aid']),  # mid_idx
                            'biz_name': self.biz,
                            'app_msg_id': str(app_msg['appmsgid']),   # 文章链接中的mid
                            'msg_create_time': datetime.datetime.fromtimestamp(int(app_msg['create_time'])
                                                                               ).strftime('%Y-%m-%d %H:%M:%S'),
                            'app_msg_digest': app_msg['digest'],
                            'app_msg_url': app_msg['link'],
                            'app_msg_title': app_msg['title'],
                        }

                        double_check_info = {
                            'type': 'double',
                            'biz': self.biz,
                            'paper': saving_info['app_msg_title']
                        }
                        # 做一次查重校验，用文章标题来判断这篇文章是不是已经爬过了
                        if not save_redis(double_check_info):
                            print(double_check_info['paper'], '已经爬过了')
                            continue

                        # 没有爬过的就入库
                        save_result = save_biz_paper(saving_info)
                        if save_result == 1:
                            print('文章：', saving_info['app_msg_title'] + '保存成功')
                        else:
                            del_redis_ele(saving_info)
                            print('文章：', saving_info['app_msg_title'] + '保存失败')

                        # print(saving_info)
                        # self.get_paper_detail(app_msg['link'])
                    # 每页爬完之后都把重试次数重置
                    retry_times = 0

                    # 已爬取的页数更新，在计算需要爬取的页数和开始位置的时候用
                    self.clawed_page += 1
                    clawed_info = {
                        'type': 'clawed',
                        'biz': self.biz,
                        'clawed_page': self.clawed_page,
                    }
                    try:
                        save_redis(clawed_info)
                    except Exception as e:
                        print(e)

            # 需要爬的次数和开始位置变更
            clawing_pages -= 1
            self.paper_params['begin'] = str(int(self.paper_params['begin']) + 5)

            time.sleep(random.randint(5, 15))
        print(self.biz + '文章爬取完毕')


if __name__ == '__main__':
    wechat = WechatSpider('495768433@qq.com', 'as9754826', '嬉游')
    # print(type(wechat.get_biz('嬉游')))
    wechat.get_all_paper()

