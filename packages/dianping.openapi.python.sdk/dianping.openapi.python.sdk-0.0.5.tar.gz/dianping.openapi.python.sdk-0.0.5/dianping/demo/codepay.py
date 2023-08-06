from dianping.client import Client
from dianping.request.codepay import BookResultCallBackRequest
from dianping.request.codepay import IsvConsumeRequest


def bookresultcalltest():
    bookresultReq = BookResultCallBackRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                              '24b4e5e0e94119930686399d02439415013ab013',
                                              '1455662777889999', 2, 'J000001', 200, '66666')

    client = Client(bookresultReq)
    response = client.invoke()
    print(response)
    assert (response is not None)


def isvconsumetest():
    isvconsumereq = IsvConsumeRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                      '24b4e5e0e94119930686399d02439415013ab013',
                                      '1455662777889999', 'J000001')

    client = Client(isvconsumereq)
    response = client.invoke()
    print(response)
    assert (response is not None)


if __name__ == '__main__':
    bookresultcalltest()
    isvconsumetest()
