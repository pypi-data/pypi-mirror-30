import sign
import time
import requests
import dzauth


class DZClient:
    def __init__(self, auth):
        self.auth = auth

    def invoke(self):
        reqparams = self.auth.get_query_param()
        url = self.auth.get_url()
        httpmethod = self.auth.get_httpmethod()

        if isinstance(self.auth, dzauth.Sign):
            params = {
                'sign_method': 'MD5',
                'format': 'json',
                'v': '1',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            }
            params = dict(params.items() + reqparams.items())
            signstr = sign.sign(params, self.auth.get_secret(), params.get('sign_method'))
            params['sign'] = signstr

        elif isinstance(self.auth, dzauth.OAuth):
            params = reqparams

        response = self.__sendrequset__(httpmethod, url, params)
        return response

    def __sendrequset__(self, method, url, param):
        header = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}

        if method.upper() == 'GET':
            resp = requests.get(url, param)
        elif method.upper() == 'POST':
            resp = requests.post(url, param, None)
        return resp.content

    if __name__ == '__main__':
        invoke()
