class Auth(object):
    def __init__(self):
        pass

    def get_param_map(self):
        pass


class Sign(Auth):
    def __init__(self):
        self._params = {}
        self._url = ''
        self._session = ''
        self._secret = ''
        self._http_method = ''

    def get_query_param(self):
        return self._params

    def set_query_param(self, param):
        self._params = param

    def add_query_param(self, k, v):
        if self._params is None:
            self._params = {}
        self._params[k] = v

    def get_url(self):
        return self._url

    def set_url(self, url):
        self._url = url

    def get_app_key(self):
        return self._params['app_key']

    def set_app_key(self, appkey):
        self.add_query_param('app_key', appkey)

    def get_secret(self):
        return self._secret

    def set_secret(self, secret):
        self._secret = secret

    def get_sign_method(self):
        return self.get_query_param().get('sign_method')

    def set_sign_method(self, sign_method):
        self.add_query_param('sign_method', sign_method)

    def get_v(self):
        return self.get_query_param().get('v')

    def set_v(self, v):
        self.add_query_param('v', v)

    def get_session(self):
        return self.get_query_param().get('session')

    def set_session(self, session):
        self.add_query_param('session', session)

    def get_httpmethod(self):
        return self._http_method

    def set_httpmethod(self, httpmethod):
        self._http_method = httpmethod


class OAuth(Auth):
    def __init__(self):
        self._params = {}
        self._url = ''
        self._http_method = ''

    def get_app_key(self):
        return self._params['app_key']

    def set_app_key(self, appkey):
        self.add_query_param('app_key', appkey)

    def get_query_param(self):
        return self._params

    def set_query_param(self, param):
        self._params = param

    def add_query_param(self, k, v):
        if self._params is None:
            self._params = {}
        self._params[k] = v

    def get_url(self):
        return self._url

    def set_url(self, url):
        self._url = url

    def get_app_key(self):
        return self._params['app_key']

    def set_app_key(self, appkey):
        self.add_query_param('app_key', appkey)

    def get_httpmethod(self):
        return self._http_method

    def set_httpmethod(self, httpmethod):
        self._http_method = httpmethod
