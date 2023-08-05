from dzauth import OAuth


class AuthorizePlatformRequest(OAuth):
    def __init__(self, app_key, app_secret):
        OAuth.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_grant_type('authorize_platform')
        self.set_httpmethod("POST")
        self.set_url('https://openapi.dianping.com/router/oauth/token')

    def set_grant_type(self, grant_type):
        self.add_query_param('grant_type', grant_type)

    def set_secret(self, secret):
        self.add_query_param('app_secret', secret)


class RefreshTokenRequest(OAuth):
    def __init__(self, app_key, app_secret, refresh_token):
        OAuth.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_grant_type('refresh_token')
        self.set_refresh_token(refresh_token)

        self.set_httpmethod("POST")
        self.set_url('https://openapi.dianping.com/router/oauth/token')

    def set_secret(self, secret):
        self.add_query_param('app_secret', secret)

    def set_grant_type(self, grant_type):
        self.add_query_param('grant_type', grant_type)

    def set_refresh_token(self, set_refresh_token):
        self.add_query_param('set_refresh_token', set_refresh_token)
