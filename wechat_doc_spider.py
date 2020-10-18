# -*- coding:utf-8 -*-
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import re
import os
from commons import index_url, search_url, paper_list_url, save_redis, save_biz_paper, get_clawed_page
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

    def __init__(self, user, pwd, biz):
        self.user = user
        self.pwd = pwd
        self.biz = biz
        self.proxy = ProxySpider()
        self.proxy.get_proxy_list()
        self.using_proxy = self.proxy.random_https_proxy()
        # print('inited proxy:', self.proxy.https_proxies)
        self.cookie = self.get_cookie()
        self.token = self.get_token()
        self.clawed_page = get_clawed_page(self.biz)
        if self.token == 0:
            print('token获取失败，请稍后再试')
        self.paper_params = {
            'action': 'list_ex',
            'begin': '0',
            'count': '5',
            'type': '9',
            'query': '',
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'token': str(self.token),
        }
        self.wechat_cookie = {
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
            }

    def login_official_account(self):
        driver = webdriver.Chrome(executable_path='chromedriver84.4147.exe')
        driver.get(index_url)
        time.sleep(5)
        # print(driver.page_source)
        driver.find_element_by_xpath('.//div[@class="login__type__container login__type__container__scan"]/a['
                                     '@class="login__type__container__select-type"]').click()
        # time.sleep(5)
        user_name = driver.find_element_by_name('account')
        user_name.clear()
        user_name.send_keys(self.user)
        password = driver.find_element_by_name('password')
        password.clear()
        password.send_keys(self.pwd)
        # time.sleep(5)
        driver.find_element_by_class_name('btn_login').click()
        print('请扫码')
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'weui-desktop-account__info'))
            )
        except Exception as e:
            print(e)
        else:
            driver.get(index_url)
            cookies = driver.get_cookies()
            # print(cookies)
            user_cookies = {}
            for cookie in cookies:
                user_cookies[cookie['name']] = cookie['value']

            # cookie每天都需要更新一次
            cookie_str = json.dumps(user_cookies)
            with open('cookies.txt', 'w+', encoding='utf-8') as f:
                f.write(cookie_str)
            print('cookie已保存')

    def build_refer(self):
        """构造header里的refer"""
        refer = 'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10' \
                '&createType=0&token={}&lang=zh_CN '
        return refer.format(self.token)

    def get_token(self, retry_times=0):
        cookies = self.get_cookie()
        print('token proxy:', self.using_proxy)
        try:
            token_response = requests.get(index_url, headers=headers, cookies=cookies, proxies=self.using_proxy)
        except Exception as e:
            print('token request error:', e)
            retry_times += 1
            if retry_times < 6:
                self.proxy.update_proxies(self.using_proxy['https'])
                self.using_proxy = self.proxy.random_https_proxy()
                time.sleep(2)
                return self.get_token(retry_times)
            else:
                return 0
        # print(token_response.url)
        else:
            print(token_response.url)
            token = re.findall(r'&token=(\d+)', str(token_response.url), re.S)[0]
            return token

    def get_cookie(self):
        # 如果没有登录过的话，就需要进行一次登录操作，否则直接读取已保存的cookie信息
        if not os.path.exists('cookies.txt'):
            self.login_official_account()
        with open('cookies.txt', 'r', encoding='utf-8') as f:
            cookies_str = f.read()
        cookies = json.loads(cookies_str)
        return cookies

    def get_biz(self, retry_times=0):
        """调用公众号超链接的查询接口查询公众号文章"""

        cookies = self.get_cookie()
        search_header = headers
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
            search_response = requests.get(search_url, headers=headers, cookies=cookies,
                                           proxies=self.using_proxy,
                                           params=search_params, timeout=10).json()
            print(search_response)
        except Exception as e:
            print('biz request error:', e)
            retry_times += 1
            if retry_times < 6:
                self.proxy.update_proxies(self.using_proxy['https'])
                self.using_proxy = self.proxy.random_https_proxy()
                time.sleep(1)
                return self.get_biz(retry_times)
            else:
                return 0
        # print(search_response)
        else:
            search_result = search_response['base_resp']['err_msg'] if search_response['base_resp']['err_msg'] != 'ok' \
                else [search for search in search_response['list'] if search['nickname'] == self.biz][0]
            print(search_result)
            return search_result

    def get_paper_count(self, search_response=None, retry_times=0):
        """获取公众号的所有文章列表"""

        cookie = self.get_cookie()
        paper_headers = headers
        paper_headers['refer'] = self.build_refer()
        if not search_response:
            search_res = self.get_biz()
            if search_res == 0:
                print('公众号获取失败，请稍后再试')
                return None, None
            if isinstance(search_res, str):
                print('公众号获取结果：', search_res)
                return None, None
        else:
            search_res = search_response
        print(search_res)
        fakeid = search_res['fakeid']
        self.paper_params['token'] = str(self.token)
        self.paper_params['fakeid'] = fakeid
        # 获取总文章数
        print('paper proxy:', self.using_proxy)
        try:
            paper_res = requests.get(paper_list_url, headers=paper_headers, cookies=cookie, params=self.paper_params,
                                     proxies=self.using_proxy, timeout=10)
        except Exception as e:
            print('paper request error:', e)
            retry_times += 1
            if retry_times < 6:
                self.proxy.update_proxies(self.using_proxy['https'])
                self.using_proxy = self.proxy.random_https_proxy()
                time.sleep(1)
                return self.get_paper_count(search_response=search_res, retry_times=retry_times)
            else:
                print('文章数获取失败，请稍后再试')
                return None, None
        else:
            paper_res = paper_res.json()
            print('paper_res:', paper_res)
            paper_count = paper_res.get('app_msg_cnt')
            infos = {
                'type': 'count',
                'biz': self.biz,
                'count': paper_count,
            }
            exited_count = save_redis(infos)

            return paper_count, exited_count

    def get_all_paper(self, page_num=None, retry_times=0):

        if not page_num:
            paper_count, exited_count = self.get_paper_count()
            if not paper_count:
                print('需爬取文章数获取失败，请稍后再试')
                return None
            print(paper_count, exited_count)
            clawing_paper_num = int(paper_count) - int(exited_count)
            clawing_pages = clawing_paper_num // 5 + 1
            self.paper_params['begin'] = '0'
        else:
            clawing_pages = page_num
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
                                        timeout=10).json()
            except Exception as e:
                print(e)
                retry_times += 1
                if retry_times < 6:
                    self.proxy.update_proxies(self.using_proxy['https'])
                    self.using_proxy = self.proxy.random_https_proxy()
                    time.sleep(random.randint(1, 3))
                    return self.get_all_paper(clawing_pages, retry_times)
                else:
                    print(f'第{int(self.paper_params["begin"]) // 5}页获取失败，请稍后再试')
                    continue
            else:
                try:
                    app_msg_list = response['app_msg_list']
                except KeyError:
                    print('keyError', response.text)
                else:
                    for app_msg in app_msg_list:
                        saving_info = {
                            'aid': str(app_msg['aid']),
                            'biz_name': self.biz,
                            'app_msg_id': str(app_msg['appmsgid']),   # 文章信息中的mid
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
                        if not save_redis(double_check_info):
                            print(double_check_info['paper'], '已经爬过了')
                            continue
                        save_result = save_biz_paper(saving_info)
                        print('文章：', saving_info['app_msg_title'] + '，保存', '成功' if save_result == 1 else '失败')
                        # print(saving_info)
                        # self.get_paper_detail(app_msg['link'])
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
                clawing_pages -= 1
                self.paper_params['begin'] = str(int(self.paper_params['begin']) + 5)

                time.sleep(random.randint(2, 5))
        print(self.biz + '文章爬取完毕')

    def get_paper_detail(self, paper_url):
        __biz, mid, idx, sn = self.get_detail_url_params(paper_url)
        data = {
            'is_read_only': '1',
            'is_temp_url': '0',
            'appmsgtype': '9',
            '__biz': __biz,
            'mid': mid,
            'sn': sn,
            'idx': idx,
        }

        aid = data['mid'] + '_' + data['idx']

        wechat_header = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 7.1.2; VOG-AL00 Build/N2G48H; wv) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Version/4.0 Chrome/66.0.3359.158 Mobile Safari/537.36 MMWEBID/3845 '
                          'MicroMessenger/7.0.7.1521(0x27000735) Process/toolsmp NetType/WIFI Language/zh_CN '
                          'MicroMessenger/7.0.7.1521(0x27000735) Process/toolsmp NetType/WIFI Language/zh_CN',
            'referer': str(paper_url)
        }

        appmsgext_url = 'https://mp.weixin.qq.com/mp/getappmsgext'

        wechat_params = {
            'appmsg_token': '',
            'x5': '0',
            'f': 'json',
            'mock': '',
            'uin': '777',
            'key': '777',
            'wxtoken': '777',
            'device_type': 'android-25',
        }

        try:
            app_msg_json = requests.post(appmsgext_url, headers=wechat_header, cookies=self.wechat_cookie, data=data,
                                         timeout=10).json()
            print(app_msg_json)
        except Exception as e:
            print(e)

    def get_detail_url_params(self, paper_url):
        # 从文章链接中获取文章详细信息的请求参数
        url_params = str(paper_url).split('?')[1].split('&')
        for param in url_params:
            param[:] = param[param.index('=')+1:]
        __biz, mid, idx, sn, *_ = url_params
        sn = sn[:-3] if sn[-3] == '#' else sn

        return __biz, mid, idx, sn


if __name__ == '__main__':
    wechat = WechatSpider('495768433@qq.com', 'as9754826', '广之旅头条')
    # print(type(wechat.get_biz('嬉游')))
    wechat.get_all_paper()

