from mitmproxy import ctx
import json
import re
# from commons import get_appmsg


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
            ctx.log.info('appmsgext catch successfully')
            app_msg_list = json.loads(flow.response.content)
            ctx.log.warn(str(app_msg_list))
        """if 'aweme/v1/search/sug' in flow.request.pretty_url:
            ctx.log.info('x-gorgon: ' + flow.request.headers['x-gorgon'])
            ctx.log.info('x-khronos: ' + flow.request.headers['x-khronos'])
            sug_list = json.loads(flow.response.content)['sug_list']
            for sug in sug_list:
                ctx.log.info('推荐: ' + sug['content'])"""


addons = [ArticleCatcher()]

