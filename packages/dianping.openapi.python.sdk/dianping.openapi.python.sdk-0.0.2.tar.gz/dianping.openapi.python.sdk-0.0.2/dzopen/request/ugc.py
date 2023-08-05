from dzopen.dzauth import Sign


class QueryShopReviewRequest(Sign):
    def __init__(self, app_key, app_secret, session, app_shop_id, begintime, endtime, star, platform, offset, limit):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_url('https://openapi.dianping.com/router/ugc/queryshopreview')
        self.set_sign_method('MD5')
        self.set_app_shop_id(app_shop_id)
        self.set_begintime(begintime)
        self.set_endtime(endtime)
        self.set_star(star)
        self.set_platform(platform)
        self.set_offset(offset)
        self.set_limit(limit)
        self.set_httpmethod('POST')

    def set_app_shop_id(self, app_shop_id):
        self.add_query_param('app_shop_id', app_shop_id)

    def set_begintime(self, begintime):
        self.add_query_param('begintime', begintime)

    def set_endtime(self, endtime):
        self.add_query_param('endtime', endtime)

    def set_star(self, star):
        self.add_query_param('star', star)

    def set_platform(self, platform):
        self.add_query_param('platform', platform)

    def set_offset(self, offset):
        self.add_query_param('offset', offset)

    def set_limit(self, limit):
        self.add_query_param('limit', limit)


class QueryStarRequest(Sign):
    def __init__(self, app_key, app_secret, session, app_shop_id, platform):
        Sign.__init__(self)
        self.set_session(session)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_app_shop_id(app_shop_id)
        self.set_platform(platform)
        self.set_sign_method('MD5')
        self.set_url('https://openapi.dianping.com/router/ugc/querystar')
        self.set_httpmethod('POST')

    def set_app_shop_id(self, app_shop_id):
        self.add_query_param('app_shop_id', app_shop_id)

    def set_platform(self, platform):
        self.add_query_param('platform', platform)
