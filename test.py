import requests
import re
import time

url = 'https://www.bilibili.com/bangumi/play/ss33626'

headers = {
    'user-agent': 'Mozilla/5.0(Windows NT 10.0; Win64; x64)AppleWebKit/537.36(KHTML, like Gecko) Chrome/83.0.4103.61 '
                 'Safari/537.36',
}

print(re.findall(r'__INITIAL_STATE__=(.*?);', requests.get(url, headers=headers).text))