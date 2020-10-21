from mitmproxy import ctx
import json
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
        if 'mp.weixin.qq.com/mp/getappmsgext' in flow.request.url:
            form = flow.request.urlencoded_form
            # ctx.log.info(str(form))
            aid = form['mid'] + '_' + form['idx']
            ctx.log.info('appmsgext catch successfully')
            # ctx.log.info('aid' + aid)
            app_msg_list = json.loads(flow.response.content)
            # ctx.log.warn(str(app_msg_list))
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

