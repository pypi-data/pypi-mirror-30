from client import DZClient
from request.tuangou import PrepareRequest
from request.tuangou import ConsumeRequest
from request.tuangou import ConsumedRequest
from request.tuangou import ListByDateRequest
from request.tuangou import ReverseConsumeRequest
from request.tuangou import ScanPrepareRequest
from request.tuangou import QueryShopDealRequest


def preparetest():
    preparequery = PrepareRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                  '24b4e5e0e94119930686399d02439415013ab013',
                                  '0332808512', 'J000001')
    client = DZClient(preparequery)
    response = client.invoke()
    print(response)
    assert (response is not None)


def consumetest():
    consumequery = ConsumeRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                  '24b4e5e0e94119930686399d02439415013ab013', 'ad',
                                  '0332808512', '1', 'J000001', 'aa')
    client = DZClient(consumequery)
    response = client.invoke()
    print(response)
    assert (response is not None)


def consumedtest():
    consumedquery = ConsumedRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                    '24b4e5e0e94119930686399d02439415013ab013',
                                    '0332808512', 'J000001')
    client = DZClient(consumedquery)
    response = client.invoke()
    print(response)
    assert (response is not None)


def listbydaterequesttest():
    listbydaterequst = ListByDateRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                         '24b4e5e0e94119930686399d02439415013ab013',
                                         'J000001', '', '', '')
    client = DZClient(listbydaterequst)
    response = client.invoke()
    print(response)
    assert (response is not None)


def reverconsumetest():
    listbydaterequst = ReverseConsumeRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                             '24b4e5e0e94119930686399d02439415013ab013', '', '0332808512',
                                             'J000001', '', '')
    client = DZClient(listbydaterequst)
    response = client.invoke()
    print(response)
    assert (response is not None)


def queryshopdealtest():
    queryshopdealrequst = QueryShopDealRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                               '24b4e5e0e94119930686399d02439415013ab013',
                                               'J000001')
    client = DZClient(queryshopdealrequst)
    response = client.invoke()
    print(response)
    assert (response is not None)


if __name__ == '__main__':
    preparetest()
    consumetest()
    consumedtest()
    listbydaterequesttest()
    reverconsumetest()
    queryshopdealtest()
