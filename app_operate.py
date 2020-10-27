# -*- coding: utf-8 -*-
# 用法：1. 启动redis
#       2. 启动mysql
#       3. 打开mitmproxy
#       4. 打开模拟器，配置代理
#       5. 打开appium
#       6. 修改需要爬取的公众号名称和使用的聊天窗，运行这个文件
import time
import random
from appium import webdriver
from appium.webdriver.common.mobileby import By
from appium.webdriver.common.touch_action import TouchAction
from commons import get_article_url, save_last_claw_date


class AppRobot:
    """微信的机器人，实现点开聊天窗口、发送消息、点击链接、关闭打开的链接，
    从而实现抓包获取文章信息（点赞、阅读、在看）"""

    def __init__(self):

        # Android配置信息
        self.desired_caps = {
            'platformName': 'Android',
            'platformVersion': '5.1.1',
            'deviceName': 'TAS_AN00',
            'appPackage': 'com.tencent.mm',
            'appActivity': 'com.tencent.mm.ui.LauncherUI',
            'unicodeKeyboard': True,
            'noReset': True,
        }

        # 启动driver，等待15秒确保加载完
        self.driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', self.desired_caps)
        time.sleep(15)

    def find_chat_view(self, text):
        """在微信聊天列表中查找指定的聊天窗口"""
        """chat_list = self.driver.find_elements(By.ID, 'com.tencent.mm:id/b4r')
        target_chat = None
        for chat in chat_list:
            # print((chat.find_element(By.ID, 'com.tencent.mm:id/e3x')).text)
            if (chat.find_element(By.ID, 'com.tencent.mm:id/e3x')).text == text:
                target_chat = chat
                break"""
        # 用xpath来查找，id+text定位
        xpath = f"//*[@resource-id='com.tencent.mm:id/e3x' and @text='{text}']/../../../.."
        try:
            target_chat = self.driver.find_element(By.XPATH, xpath)
        except Exception as e:
            print(e)
            target_chat = None

        return target_chat

    def sent_text(self, content):
        """
        定位输入框，写入内容并点击发送按钮
        :param content: 要发送的内容
        :return: None
        """
        edit_text = self.driver.find_element(By.ID, 'com.tencent.mm:id/al_')

        # 把输入框清空
        edit_text.clear()
        edit_text.send_keys(content)
        if self.driver.find_element(By.ID, 'anv'):
            self.driver.find_element(By.ID, 'anv').click()
            time.sleep(3)
            print('消息发送成功')
        else:
            print('发送按钮未找到')

    def click_last_info(self):
        """点击最后发送的链接的方法"""
        try:
            # 模拟点击，利用坐标定位，点击后等待10，让链接打开
            TouchAction(self.driver).press(x=207, y=1346).release().perform()
            time.sleep(10)
        except Exception as e:
            print(e)

    def close_window(self):
        """关闭打开的窗口的方法"""
        # 用xpath定位返回按钮，返回的view的父元素才能点击
        xpath = "//*[@content-desc='返回']/parent::*"
        try:
            # 关闭前随机等待5-15秒，确保所有信息都加载完了
            time.sleep(random.randint(3, 8))

            # 点击定位到的按钮
            self.driver.find_element(By.XPATH, xpath).click()
            # 点击后随机等待3-8秒，确保模拟器响应完毕
            time.sleep(random.randint(3, 8))
        except Exception as e:
            print(e)

    def run(self, biz_name, chat_name, is_continue=False):
        """爬取的入口"""
        url_list = get_article_url(biz_name, is_continue)
        if url_list == 0:
            print('url获取失败，请重试')
        else:
            print('get url success')
            chat_view = self.find_chat_view(chat_name)
            if chat_view:
                chat_view.click()
                time.sleep(4)
                print(f'开始处理公众号{biz_name}的url')
                claw_date = time.strftime('%Y-%m-%d', time.localtime())
                save_last_claw_date(biz_name, claw_date)
                for url in url_list:
                    self.sent_text(url)
                    self.click_last_info()
                    self.close_window()
                print(biz + '所有已有url已处理')
            else:
                print('没找到指定的聊天窗，请确认聊天窗名称是否正确')


if __name__ == '__main__':
    """path = os.path.split(os.path.realpath(__file__))[0]
    command = f'mitmdump -s {path}\\article_info_catcher.py'
    os.system(command)"""
    biz = '嬉游'
    chat_name = '粘膜上皮细胞'
    # print(biz)
    robot = AppRobot()
    robot.run(biz, chat_name, True)





