from dzauth import Sign

""" 
tuangou prepare

"""


class PrepareRequest(Sign):
    def __init__(self, app_key, app_secret, session, receipt_code, app_shop_id):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_url('https://openapi.dianping.com/router/tuangou/receipt/prepare')
        self.set_httpmethod('POST')
        self.set_receipt_code(receipt_code)
        self.set_app_shop_id(app_shop_id)

    def set_receipt_code(self, receipt_code):
        self.add_query_param('receipt_code', receipt_code)

    def set_app_shop_id(self, app_shop_id):
        self.add_query_param('app_shop_id', app_shop_id)


""" 
tuangou consume
 
"""


class ConsumeRequest(Sign):
    def __init__(self, app_key, app_secret, session, requestid, receipt_code, count, app_shop_account,
                 app_shop_accountname):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_url('https://openapi.dianping.com/router/tuangou/receipt/consume')
        self.set_httpmethod('POST')

        self.set_request_id(requestid)
        self.set_receipt_code(receipt_code)
        self.set_count(count)
        self.set_app_shop_account(app_shop_account)
        self.set_app_shop_accountname(app_shop_accountname)

    def set_request_id(self, request_id):
        self.add_query_param('request_id', request_id)

    def set_receipt_code(self, receipt_code):
        self.add_query_param('receipt_code', receipt_code)

    def set_count(self, count):
        self.add_query_param('count', count)

    def set_app_shop_account(self, app_shop_account):
        self.add_query_param('app_shop_account', app_shop_account)

    def set_app_shop_accountname(self, app_shop_accountname):
        self.add_query_param('app_shop_accountname', app_shop_accountname)


class ConsumedRequest(Sign):
    def __init__(self, app_key, app_secret, session, receipt_code, app_shop_id):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_url('https://openapi.dianping.com/router/tuangou/receipt/getconsumed')
        self.set_httpmethod('POST')

        self.set_receipt_code(receipt_code)
        self.set_app_shop_id(app_shop_id)

    def set_receipt_code(self, receipt_code):
        self.add_query_param('receipt_code', receipt_code)

    def set_app_shop_id(self, app_shop_id):
        self.add_query_param('app_shop_id', app_shop_id)


class ListByDateRequest(Sign):
    def __init__(self, app_key, app_secret, session, app_shop_id, date, offset, limit):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_url('https://openapi.dianping.com/router/tuangou/receipt/querylistbydate')
        self.set_httpmethod('POST')

        self.set_app_shop_id(app_shop_id)
        self.app_shop_id = app_shop_id
        self.set_date(date)
        self.set_offset(offset)
        self.set_limit(limit)

    def set_app_shop_id(self, app_shop_id):
        self.add_query_param('app_shop_id', app_shop_id)

    def set_date(self, date):
        self.add_query_param('date', date)

    def set_offset(self, offset):
        self.add_query_param('offset', offset)

    def set_limit(self, limit):
        self.add_query_param('limit', limit)


class ReverseConsumeRequest(Sign):
    def __init__(self, app_key, app_secret, session, app_deal_id, receipt_code, app_shop_id, app_shop_account,
                 app_shop_accountname):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_url('https://openapi.dianping.com/router/tuangou/receipt/reverseconsume')
        self.set_httpmethod('POST')

        self.set_receipt_code(receipt_code)
        self.set_app_shop_account(app_shop_account)
        self.set_app_shop_accountname(app_shop_accountname)
        self.set_app_shop_id(app_shop_id)
        self.set_app_deal_id(app_deal_id)

    def set_receipt_code(self, receipt_code):
        self.add_query_param('receipt_code', receipt_code)

    def set_app_shop_account(self, app_shop_account):
        self.add_query_param('app_shop_account', app_shop_account)

    def set_app_shop_accountname(self, app_shop_accountname):
        self.add_query_param('app_shop_accountname', app_shop_accountname)

    def set_app_deal_id(self, app_deal_id):
        self.add_query_param('app_deal_id', app_deal_id)

    def set_app_shop_id(self, app_shop_id):
        self.add_query_param('app_shop_id', app_shop_id)


class ScanPrepareRequest(Sign):
    def __init__(self, app_key, app_secret, session, qr_code, app_shop_id):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_url('https://openapi.dianping.com/router/tuangou/receipt/scanprepare')
        self.set_httpmethod('POST')
        self.set_app_shop_id(app_shop_id)
        self.qr_code = qr_code

    def set_app_shop_id(self, app_shop_id):
        self.add_query_param('app_shop_id', app_shop_id)

    def set_qr_code(self, qr_code):
        self.add_query_param('qr_code', qr_code)


class QueryShopDealRequest(Sign):
    def __init__(self, app_key, app_secret, session, app_shop_id):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_url('https://openapi.dianping.com/router/tuangou/receipt/scanprepare')
        self.set_httpmethod('POST')
        self.set_app_shop_id(app_shop_id)

    def set_app_shop_id(self, app_shop_id):
        self.add_query_param('app_shop_id', app_shop_id)
