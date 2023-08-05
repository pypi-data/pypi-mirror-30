from client import DZClient
from request.book import BookResultCallBackRequest
from request.book import CancelBookCallBackRequest
from request.book import IsvConsumeRequest
from request.book import RefundAuditResultRequest


def test_bookresultcallback():
    bookrresult = BookResultCallBackRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                            '24b4e5e0e94119930686399d02439415013ab013',
                                            '1455662777889999', 2, 'J000001', 200, '66666')
    client = DZClient(bookrresult)
    response = client.invoke()
    print(response)
    assert (response is not None)


def testcancelBook():
    cancelreq = CancelBookCallBackRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                          '24b4e5e0e94119930686399d02439415013ab013', 1455662777889999, 'J000001', 200,
                                          2)
    client = DZClient(cancelreq)
    response = client.invoke()
    print(response)
    assert (response is not None)


def testisvconsumeRequest():
    isvconsumereq = IsvConsumeRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                      '24b4e5e0e94119930686399d02439415013ab013', 1455662777889999, 'J000001')

    client = DZClient(isvconsumereq)
    response = client.invoke()
    print(response)
    assert (response is not None)


def testRefundAudit():
    refundauditreq = RefundAuditResultRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                              '24b4e5e0e94119930686399d02439415013ab013', 'J000001', 2,
                                              1455662777889999)
    client = DZClient(refundauditreq)
    response = client.invoke()
    print(response)
    assert (response is not None)


if __name__ == '__main__':
    test_bookresultcallback()
    testcancelBook()
    testisvconsumeRequest()
    testRefundAudit()
