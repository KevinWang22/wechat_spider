# 微信公众号文章爬虫
仅作为学习参考

### 前期准备

---

1. 需要的第三方库

   selenium、appnium、mitmproxy、pymsql、redis

2. 数据库

   redis+mysql

3. 其他

   1. chrome浏览器和对应版本的driver，driver可以从这里[下载](http://npm.taobao.org/mirrors/chromedriver/)

   2. 一个可以登录的微信账号及其绑定的一个公众号账号



### 爬取的思路

---

#### 文章基础信息

调用微信公众号在增加超链接时候的查询接口，支持查询一个公众号下的所有文章，但是每次调用接口只能获取5次推送的内容，因此需要多次调用

### 文章详细信息

在获取完文章基础信息后，会保存文章的永久链接到数据库中，经测试，如果直接请求，只会返回文章的内容，但是不会返回点赞这些信息，这些信息必须要有微信账号的token，所以这里使用appnium+mitmproxy的方法，把数据库中的链接读出来，然后依次在微信中打开，直接抓包



### 使用方法

---

#### 爬取文章基础信息

1. 打开redis、mysql，配置好mysql的用户和密码

2. 配置好你的公众号账号密码

3. 修改wechat_doc_spider.py中的公众号名称

4. 运行wechat_doc_spider.py

#### 爬取文章详细信息

1. 启动redis
2. 启动mysql
3. 打开mitmproxy
4. 打开模拟器，配置代理
5. 打开appium
6. 修改需要爬取的公众号名称和使用的聊天窗，运行app_operate.py