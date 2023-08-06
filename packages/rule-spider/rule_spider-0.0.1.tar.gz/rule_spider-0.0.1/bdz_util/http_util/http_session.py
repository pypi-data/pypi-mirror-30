# -*- coding: utf-8 -*-
'''
基本请求回话类
'''
import requests



from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class HttpSession(object):

    def __init__(self):
        self.html = ''
        self.cookie = {}
        self.cookie_list = []
        self.referer = ''
        self.resp = None

    def set_query_params(self,params):
        '''
        设置GET方式的参数,就是url后面?后面的一串
        :param params:
        :return:
        '''
        self.query_params = params


    def set_post_params(self,params):
        '''
        设置POST请求的参数
        :param params:
        :return:
        '''
        self.post_params = params


    @property
    def cookie_str(self):
        if self.cookie != None:
            li = []
            for (k, v) in self.cookie.items():
                s = k + "=" + v + ";"
                li.append(s)
            return ''.join(li)
        else:
            return ''


    def get(self,**kwargs):
        kwargs['method'] = "GET"
        return self.request(**kwargs)

    def post(self,**kwargs):
        kwargs['method'] = "POST"
        return self.request(**kwargs)


    def request(self, **kwargs):
        kwargs['cookies'] = self.cookie
        kwargs['timeout'] = 1800
        params = str(kwargs)
        i = 0
        req_ok = False
        resp = None
        while req_ok == False:
            i = i + 1
            try:
                resp = requests.request(**kwargs)
                req_ok = True
            except:
                req_ok = False
                print('第' + str(i) + '请求参数:' + params + '网络异常')
            if req_ok == True or i > 2:
                break
        # resp.encoding = 'utf-8'
        if req_ok:
            if 'GBK' in resp.headers.get('Content-Type').upper():
                resp.encoding = "GBK"
            else:
                resp.encoding = resp.apparent_encoding
            self.html = resp.text
            self.resp = resp
            self.update_cookie(resp.cookies)
            #headers = str(self.resp.headers)
            #print('请求参数:' + params + '响应头:' + headers)
            return resp
        else:
            return None

    def is_cookie_in(self, c):
        for index, cc in enumerate(self.cookie_list):
            if cc.name == c.name and cc.domain == c.domain and cc.path == c.path:
                return index
        return -1

    def update_cookie(self, resp_cookies):
        for co in resp_cookies:
            index_of_cookie_list = self.is_cookie_in(co)
            # 如果不在,append
            if index_of_cookie_list == -1:
                self.cookie_list.append(co)
            else:
                # 覆盖
                self.cookie_list[index_of_cookie_list] = co
        self.update_cookie_dict()

    def update_cookie_dict(self):
        for index, x in enumerate(self.cookie_list):
            self.cookie[x.name] = x.value
            for y in self.cookie_list:
                if x.name == y.name and len(y.domain) > len(x.domain):
                    # 同名更新.取domain长度大一些的
                    self.cookie[y.name] = y.value
                if x.name == y.name and len(y.path) > len(y.path):
                    self.cookie[y.name] = y.value
        return self.cookie

    def set_cookie(self, k, v):
        self.cookie[k] = v
    def set_cookie_dict(self,cookie_dict):
        self.cookie = cookie_dict
    def try_if_except(self, method, **kwargs):
        i = 0
        while True:
            try:
                if i > 2:
                    break
                i = i + 1
                method(**kwargs)
                break
            except:
                print('异常')
    pass
if __name__ == "__main__":
    # print('\u8bf7\u8f93\u5165\u8d26\u6237\u540d')
    pass