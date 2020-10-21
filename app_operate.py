# -*- coding: utf-8 -*-
import time
import random
from appium import webdriver
from appium.webdriver.common.mobileby import By
from appium.webdriver.common.touch_action import TouchAction
from commons import get_article_url


class AppRobot:
    """微信的机器人，实现点开聊天窗口、发送消息、点击链接、关闭打开的链接，
    从而实现抓包获取文章信息（点赞、阅读、在看）"""

    def __init__(self):

        self.desired_caps = {
            'platformName': 'Android',
            'platformVersion': '5.1.1',
            'deviceName': 'TAS_AN00',
            'appPackage': 'com.tencent.mm',
            'appActivity': 'com.tencent.mm.ui.LauncherUI',
            'unicodeKeyboard': True,
            'noReset': True,
        }
        self.driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', self.desired_caps)
        time.sleep(15)

    def find_chat_view(self, text):
        """在微信聊天列表中查找指定的聊天窗口"""
        chat_list = self.driver.find_elements(By.ID, 'com.tencent.mm:id/b4r')
        target_chat = None
        for chat in chat_list:
            # print((chat.find_element(By.ID, 'com.tencent.mm:id/e3x')).text)
            if (chat.find_element(By.ID, 'com.tencent.mm:id/e3x')).text == text:
                target_chat = chat
                break

        return target_chat

    def sent_text(self, content):
        edit_text = self.driver.find_element(By.ID, 'com.tencent.mm:id/al_')
        edit_text.clear()
        edit_text.send_keys(content)
        if self.driver.find_element(By.ID, 'anv'):
            self.driver.find_element(By.ID, 'anv').click()
            time.sleep(3)
            print('消息发送成功')
        else:
            print('发送按钮未找到')

    def click_last_info(self):
        try:
            TouchAction(self.driver).press(x=353, y=1012).release().perform()
            time.sleep(10)
        except Exception as e:
            print(e)

    def close_window(self):
        xpath = "//*[@content-desc='返回']/parent::*"
        try:
            self.driver.find_element(By.XPATH, xpath).click()
            time.sleep(random.randint(3, 8))
        except Exception as e:
            print(e)


if __name__ == '__main__':
    """path = os.path.split(os.path.realpath(__file__))[0]
    command = f'mitmdump -s {path}\\article_info_catcher.py'
    os.system(command)"""
    biz = '南湖国旅非同凡享'
    print(biz)
    url_list = get_article_url(biz, True)
    if url_list == 0:
        print('url获取失败，请重试')
    else:
        print('get url success')
        robot = AppRobot()
        chat_view = robot.find_chat_view('粘膜上皮细胞')
        chat_view.click()
        time.sleep(4)
        print(f'开始处理公众号{biz}的url')
        for url in url_list:
            robot.sent_text(url)
            robot.click_last_info()
            robot.close_window()
        print(biz + '所有已有url已处理')





