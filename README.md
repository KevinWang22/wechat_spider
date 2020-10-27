# wechat_spider
微信公众号文章爬虫

仅作为学习参考

一、 使用前的准备
python 3.7.4   #  需要提前安装seleium、appium、mitmproxy、pymsql、redis
数据库：redis、mysql
chrome浏览器及对应版本的driver，没有driver的可以从这里下载：http://npm.taobao.org/mirrors/chromedriver/
一个可以登录的微信账号和微信公众号
二、 使用方法
  (一) 文章基础信息
    1. 打开redis、mysql，配置好mysql的用户和密码
    2. 配置好你的公众号账号密码
    3. 修改wechat_doc_spider.py中的公众号名称
    4. 运行wechat_doc_spider.py
  (二) 文章详细信息
    1. 启动redis
    2. 启动mysql
    3. 打开mitmproxy
    4. 打开模拟器，配置代理
    5. 打开appium
    6. 修改需要爬取的公众号名称和使用的聊天窗，运行app_operate.py
