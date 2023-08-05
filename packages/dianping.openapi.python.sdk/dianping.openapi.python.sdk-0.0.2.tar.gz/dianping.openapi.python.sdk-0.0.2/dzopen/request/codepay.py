from dzopen.dzauth import Sign


class BookResultCallBackRequest(Sign):
    def __init__(self, app_key, app_secret, session, order_id, book_status, app_shop_id, code, app_order_id=None):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_url('https://openapi.dianping.com/router/book/bookresultcallback')
        self.set_httpmethod('POST')
        self.set_order_id(order_id)
        self.set_book_status(book_status)
        self.set_app_shop_id(app_shop_id)
        self.set_code(code)
        self.set_app_order_id(app_order_id)

    def set_order_id(self, orderid):
        self.add_query_param('order_id', orderid)

    def set_book_status(self, book_status):
        self.add_query_param('book_status', book_status)

    def set_app_shop_id(self, app_shop_id):
        self.add_query_param('app_shop_id', app_shop_id)

    def set_app_order_id(self, app_order_id):
        self.add_query_param('app_order_id', app_order_id)

    def set_code(self, code):
        self.add_query_param('code', code)


class IsvConsumeRequest(Sign):
    def __init__(self, app_key, app_secret, session, order_id, app_shop_id):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_url('https://openapi.dianping.com/router/book/isvconsume')
        self.set_httpmethod('POST')
        self.set_order_id(order_id)
        self.set_app_shop_id(app_shop_id)

    def set_order_id(self, order_id):
        self.add_query_param('order_id', order_id)

    def set_app_shop_id(self, app_shop_id):
        self.add_query_param('app_shop_id', app_shop_id)
