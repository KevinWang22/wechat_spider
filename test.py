import requests
import re


url = 'http://mp.weixin.qq.com/s?__biz=MjM5MTM2Mjk4MQ==&mid=2650242990&idx=1&sn=0f869748dd122c5ceb8b3f5e161bf9af' \
      '&chksm=beb5656489c2ec72a2e07fae6c5aad93dfba886eccf124feb9d63559870e4ef14fe52d6b8a5b#rd'

url1 = 'https://mp.weixin.qq.com/mp/getappmsgext?f=json&mock=&uin=MjgxMDQ2NTMxOQ%3D%3D&key=7e8de568c78f67e' \
      '54b499dce50d2d51dee5fff4f5cbdcd1702513f266fbbf09b8915db7e4a7152558db35b9bf3e0680513bd198c8700d6f7c75' \
      'c4135c329fb6cf084ceb78bd76f8cd0b67c87b303a1e94a53bdd681e13cad337057dd67320832fb48e8c479a81f89ec59b81' \
      'bd461b4b0ca0516cedbae5770c980966c7010eb80' \
      '&pass_ticket=nc1a98Oc3rf8iYELSdjj5eHB7ykYBJD26PusldLEx0e%2Bs%2FuVRb0w8Q6WrB9SsewI' \
      '&wxtoken=777&devicetype=Windows%26nbsp%3B10%26nbsp%3Bx64' \
      '&clientversion=6300002f&__biz=MjM5MzYxMTU2MA%3D%3D' \
      '&appmsg_token=1082_XlWSdmrf4eHFhZ9Q9E_MAD0cjBPvyV0qAbdiW6y2woEbcqAW3i4I5tWlB3dPvkDYWxhBOwSnK3eqfmmV&x5=0&f=json'

appmsgext_url = 'https://mp.weixin.qq.com/mp/getappmsgext'

wechat_header = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 7.1.2; VOG-AL00 Build/N2G48H; wv) AppleWebKit/537.36 (KHTML, '
                  'like Gecko) Version/4.0 Chrome/66.0.3359.158 Mobile Safari/537.36 MMWEBID/3845 '
                  'MicroMessenger/7.0.7.1521(0x27000735) Process/toolsmp NetType/WIFI Language/zh_CN '
                  'MicroMessenger/7.0.7.1521(0x27000735) Process/toolsmp NetType/WIFI Language/zh_CN',
    'refer': 'https://mp.weixin.qq.com/s?__biz=MjM5NzI1NzI2NQ==&mid=2650540379&idx=1&sn=59002e735b3a5a297d26f3b317de2485&chksm=bed4600589a3e9137c6a816090b9a995a70d65d89071ae15e597a5ee1ac857e3bcad627124e7&xtrack=1&scene=0&subscene=93&clicktime=1602560318&enterid=1602560318&ascene=7&devicetype=android-22&version=27000735&nettype=WIFI&abtest_cookie=AAACAA%3D%3D&lang=zh_CN&exportkey=A2LdmzCy8rD4rxNuZDwkQmE%3D&pass_ticket=O7I2sclKT1FQVSPHWdEwx%2BF7Ig4%2B4fr37wK1ay3MOXVSDsdIAWPqEkX%2BPctXV3a6&wx_header=1',
    'Host': 'mp.weixin.qq.com',

}

header = {
    'user-agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML， like Gecko) Version/4.0Chrome/57.0.2987.132 MQQBrowser/6.2 Mobile',

}

wechat_cookie = {
    'rewardsn': '',
    'wxtokenkey': '777',
    'wxuin': '2810465319',
    'devicetype': 'android-22',
    'version': '27000735',
    'lang': 'zh_CN',
    'pass_ticket': 'O7I2sclKT1FQVSPHWdEwx+F7Ig4+4fr37wK1ay3MOXVSDsdIAWPqEkX+PctXV3a6',
    'wap_sid2': 'CKeYkbwKEooBeV9IQk90OFh1VkJNQVNpSnlIYmsxRGJzNFdTTFE5ZjFCNjQwZERXRE5LY1FKZ29KMFZkLVRlallsNDdSSlJrRW5mdVRVTFEzajdQcE9NT09ybVJXUnRLRDdLRnJHdGE5MFU2NVpnUnRxSjhtN0plOGlhZ0s1VHhaZXptdk1lZ1hiNm94Z1NBQUF+MJiIkPwFOA1AAQ==',
}


data = {
    'is_read_only': '1',
    'is_temp_url': '0',
    'appmsgtype': '9',
    '__biz': 'MzI4ODg5MTIzMA==',
    'mid': '2247521365',
    'sn': '84d5a7cffe03ed2047331bff2d7e1ccc',
    'idx': '1',

}

# wechat_header['Cookie'] = str(wechat_cookie)

appmsgext_url = appmsgext_url

wechat_params = {
    'f': 'json',
    'mock': '',
    'uin': '777',
    'key': '777',
    'wxtoken': '777',
    'device_type': 'android-25',
    '__biz': data['__biz'],
    'appmsg_token': '1082_M2iRmtTLYYkoqNuFFFz8WYI7YVG7UstTx2PJveUNBR_FBrLpcZMGNzbRQiYbP9sxWUT3EQi1sJEQXtPM',
    'x5': '0',
}

response = requests.post(appmsgext_url, headers=wechat_header, cookies=wechat_cookie,
                         params=wechat_params, data=data, verify=True).json()

# uin=MjgxMDQ2NTMxOQ==&&key=0a19845a51c58415782ceffa48112777d0740c760ff46d0621202f43a608b449be070276d34c8c619f6a1ed0f319c2a6911dc6b448ff28463d634640a7eb773b439c7b177d9eee3b4135657bd90db616869b2f1db653c8b2729ee1be84894e4fc0ecc8aff78ffa2bcd7d05429483bc433523e98fd1f8d75a5dac4da819fabd30

print(response)

