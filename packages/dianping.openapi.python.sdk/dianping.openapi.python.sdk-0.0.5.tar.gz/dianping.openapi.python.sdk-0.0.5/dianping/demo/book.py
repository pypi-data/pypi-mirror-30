from dianping.client import Client
from dianping.request.book import BookResultCallBackRequest
from dianping.request.book import CancelBookCallBackRequest
from dianping.request.book import IsvConsumeRequest
from dianping.request.book import RefundAuditResultRequest


def test_bookresultcallback():
    """
    @:param app_key
    @:param app_secret
    @:param session
    @:param book_status
    @:param app_shop_id
    @:param code
    @:param app_order_id
    """
    bookrresult = BookResultCallBackRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                            '24b4e5e0e94119930686399d02439415013ab013',
                                            '1455662777889999', 2, 'J000001', 200, '66666')
    client = Client(bookrresult)
    response = client.invoke()
    print(response)
    assert (response is not None)


def testcancelBook():
    cancelreq = CancelBookCallBackRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                          '24b4e5e0e94119930686399d02439415013ab013', 1455662777889999, 'J000001', 200,
                                          2)
    client = Client(cancelreq)
    response = client.invoke()
    print(response)
    assert (response is not None)


def testisvconsumeRequest():
    isvconsumereq = IsvConsumeRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                      '24b4e5e0e94119930686399d02439415013ab013', 1455662777889999, 'J000001')

    client = Client(isvconsumereq)
    response = client.invoke()
    print(response)
    assert (response is not None)


def testRefundAudit():
    refundauditreq = RefundAuditResultRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                              '24b4e5e0e94119930686399d02439415013ab013', 'J000001', 2,
                                              1455662777889999)
    client = Client(refundauditreq)
    response = client.invoke()
    print(response)
    assert (response is not None)


if __name__ == '__main__':
    test_bookresultcallback()
    testcancelBook()
    testisvconsumeRequest()
    testRefundAudit()
