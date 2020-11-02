from wechat_doc_spider import WechatSpider
from app_operate import AppRobot


if __name__ == '__main__':
    control_type = 'wechat'
    user_id = '公众号账号'
    pwd = '公众号密码'
    biz = '公众号名称'
    chat_name = '聊天框名称'
    is_continue_wechat = True
    is_continue_app = False
    finish_null = True

    if control_type == 'wechat':
        wechat = WechatSpider(user=user_id, pwd=pwd, biz=biz, is_continue=is_continue_wechat)
        wechat.get_all_paper()
    else:
        robot = AppRobot()
        robot.run(biz_name=biz, chat_name=chat_name, is_continue=is_continue_app, finish_null=finish_null)
