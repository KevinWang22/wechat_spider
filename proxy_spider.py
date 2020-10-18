# -*- coding:utf-8 -*-
import random
import requests
import lxml.html
import time
import re


class ProxySpider:
    """获取代理ip"""
    def __init__(self):
        """初始化http_proxies和https_proxies"""
        self.http_proxies = []
        self.https_proxies = []

    def get_proxy_list(self):
        """获取前两页的代理ip"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/80.0.3987.106 Safari/537.36',
        }
        for page in range(1, 3):
            url = 'http://www.xiladaili.com/gaoni/%d' % page
            try:
                response = requests.get(url=url, headers=headers)
            except Exception as e:
                print(e)
            if response.status_code == 200:
                # print(response.text)
                page = response.text
                selector = lxml.html.fromstring(page)
                proxy_info_blocks = selector.xpath('//table[@class="fl-table"]/tbody/tr')
                for proxy_info in proxy_info_blocks:
                    proxy = proxy_info.xpath('td[1]/text()')[0]
                    # print(proxy)
                    protocol = proxy_info.xpath('td[2]/text()')[0]
                    anonymity = proxy_info.xpath('td[3]/text()')[0]
                    if '高匿' not in anonymity:
                        continue
                    life_time = proxy_info.xpath('td[6]/text()')[0]
                    if '天' not in life_time:
                        continue
                    check_time = proxy_info.xpath('td[7]/text()')[0]
                    strp_time = time.strptime(check_time, '%Y年%m月%d日 %H:%M')
                    # print(strp_time)
                    local_time = time.localtime()
                    if strp_time.tm_min < local_time.tm_min - 10:
                        break
                    point = proxy_info.xpath('td[8]/text()')[0]
                    if int(point) < 100:
                        continue
                    if proxy not in self.http_proxies and ('HTTP,' or 'HTTP代理' in protocol):
                        self.http_proxies.append(proxy)
                    if proxy not in self.https_proxies and 'HTTPS' in protocol:
                        self.https_proxies.append(proxy)
            time.sleep(random.random()*2)
        print('代理初始化成功')

    def random_proxies(self):
        """从代理列表中随机抽取两个代理ip（http, https）返回"""
        http_proxy = random.choice(self.http_proxies)
        https_proxy = random.choice(self.https_proxies)
        proxies = {
            'http': 'http://'+http_proxy,
            'https': 'https://'+https_proxy,
        }

        return proxies

    def random_http_proxy(self):
        """只返回一个http代理"""
        http_proxy = random.choice(self.http_proxies)
        proxy = {
            'http': 'http://' + http_proxy,
        }

        return proxy

    def random_https_proxy(self):
        """只返回一个https代理"""
        if not self.https_proxies:
            return None
        https_proxy = random.choice(self.https_proxies)
        proxy = {
            'https': 'https://' + https_proxy
        }

        return proxy

    def update_proxies(self, url):
        """更新代理列表，当某一代理列表为空时，重新获取一次"""
        if re.match(r'^http://', url):
            self.http_proxies.remove(url.split('//')[1])
            if len(self.http_proxies) <= 0:
                self.get_proxy_list()
        else:
            self.https_proxies.remove(url.split('//')[1])
            if len(self.https_proxies) == 0:
                self.get_proxy_list()
