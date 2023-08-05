from request.ugc import QueryShopReviewRequest
from request.ugc import QueryStarRequest
from client import DZClient


# app_key, app_secret, session, app_shop_id, begintime, endtime, star, platform, offset, limit
def queryshopreviewtest():
    request = QueryShopReviewRequest('1000069', '6862bd6012020b0fd385652905db18d4c9eaa835',
                                     '24b4e5e0e94119930686399d02439415013ab013',
                                     'J000001', '2017-10-25 10:30:00', '2018-01-18 10:30:00', 1, 1, 1, 10)
    client = DZClient(request)
    response = client.invoke()
    print(response)
    assert (response is not None)


def test_query_star():
    query_start_request = QueryStarRequest('1000069', '6862bd6012020b0fd385652905db18d4c9eaa835',
                                           '24b4e5e0e94119930686399d02439415013ab013',
                                           'J000001', 1)
    client = DZClient(query_start_request)
    response = client.invoke()
    print(response)
    assert (response is not None)


if __name__ == '__main__':
    queryshopreviewtest()
    test_query_star()
