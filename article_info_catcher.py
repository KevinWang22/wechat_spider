import json
import re
from mitmproxy import ctx
from commons import save_num


class ArticleCatcher:

    def __init__(self):
        pass

    def response(self, flow):
        """
        获取appmsgext的返回包
        :param flow: mitmproxy.http.HTTPFlow
        :return: article_info
        """
        # 13年的推送没有点赞阅读这些信息，所以设为0
        if 'mp/appmsg/show?' in flow.request.url:
            ctx.log.info(flow.request.url)
            appmsgid_pattern = r'&appmsgid=(\d+)&'
            idx_pattern = r'&itemidx=(\d+)&'
            app_msg_id = re.findall(appmsgid_pattern, str(flow.request.url))[0]
            idx = re.findall(idx_pattern, str(flow.request.url))[0]
            aid = app_msg_id + '_' + idx
            read_num = like_num = looking_num = 0
            save_result = save_num(aid, looking_num, read_num, like_num)
            if save_result:
                ctx.log.info(aid + '保存成功')
            else:
                ctx.log.info(aid + '保存失败')
        # 13年的推送也会发送getappmsgext请求，但返回的和其他不一样，要在前面先单独处理
        elif 'mp.weixin.qq.com/mp/getappmsgext' in flow.request.url:
            form = flow.request.urlencoded_form
            # ctx.log.info(str(form))
            aid = form['mid'] + '_' + form['idx']
            ctx.log.info('appmsgext catch successfully')
            # ctx.log.info('aid' + aid)
            app_msg_list = json.loads(flow.response.content)
            # ctx.log.warn(str(app_msg_list))
            if 'ret' not in app_msg_list['base_resp']:
                like_num = app_msg_list['appmsgstat']['old_like_num']
                looking_num = app_msg_list['appmsgstat']['like_num']
                read_num = app_msg_list['appmsgstat']['read_num']
                # ctx.log.info(str(like_num) + ' ' + str(looking_num) + ' ' + str(read_num))
                save_result = save_num(aid, looking_num, read_num, like_num)
                if save_result:
                    ctx.log.info(aid + '保存成功')
                else:
                    ctx.log.info(aid + '保存失败')

        """if 'aweme/v1/search/sug' in flow.request.pretty_url:
            ctx.log.info('x-gorgon: ' + flow.request.headers['x-gorgon'])
            ctx.log.info('x-khronos: ' + flow.request.headers['x-khronos'])
            sug_list = json.loads(flow.response.content)['sug_list']
            for sug in sug_list:
                ctx.log.info('推荐: ' + sug['content'])"""


addons = [ArticleCatcher()]

