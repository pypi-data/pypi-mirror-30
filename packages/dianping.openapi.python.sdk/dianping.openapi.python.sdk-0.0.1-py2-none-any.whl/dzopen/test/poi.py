# coding: utf-8
# 'ascii'
from client import DZClient
from request.poi import QueryCategoriesRequest
from request.poi import QueryCitiesByProvinceNameRequest
from request.poi import QueryCitysRequest
from request.poi import QueryHomeProvincesRequest
from request.poi import QueryOpenCategoryNameRequest
from request.poi import QueryOverSeasCitiesRequest
from request.poi import QueryOverseasProvinces
from request.poi import QueryPoiBusinessDistrictRequest
from request.poi import QueryRegionsRequest
from request.poi import QueryShopPoiDetailRequest


def querycategorietest():
    categoriesrequest = QueryCategoriesRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                               '24b4e5e0e94119930686399d02439415013ab013',
                                               '上海')
    client = DZClient(categoriesrequest)
    response = client.invoke()
    print(response)
    assert (response is not None)


def querycitytest():
    querycity = QueryCitysRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                  '24b4e5e0e94119930686399d02439415013ab013')
    client = DZClient(querycity)
    response = client.invoke()
    print(response)
    assert (response is not None)


def querycitybyprovincenametest():
    querycitybyprovicerequest = QueryCitiesByProvinceNameRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                                                 '24b4e5e0e94119930686399d02439415013ab013',
                                                                 '上海')
    client = DZClient(querycitybyprovicerequest)
    response = client.invoke()
    print(response)
    assert (response is not None)


def queryhomeprovincenametest():
    queryhomeprovicerequest = QueryHomeProvincesRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                                        '24b4e5e0e94119930686399d02439415013ab013')
    client = DZClient(queryhomeprovicerequest)
    response = client.invoke()
    print(response)
    assert (response is not None)


def queryopencategorynametest():
    opencategoryname = QueryOpenCategoryNameRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                                    '24b4e5e0e94119930686399d02439415013ab013', '上海')
    client = DZClient(opencategoryname)
    response = client.invoke()
    print(response)
    assert (response is not None)


def queryoverseacitytest():
    queryoverseacity = QueryOverSeasCitiesRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                                  '24b4e5e0e94119930686399d02439415013ab013')
    client = DZClient(queryoverseacity)
    response = client.invoke()
    print(response)
    assert (response is not None)


def queryoverseaprovincetest():
    queryoverseaprivince = QueryOverseasProvinces(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                                  '24b4e5e0e94119930686399d02439415013ab013')
    client = DZClient(queryoverseaprivince)
    response = client.invoke()
    print(response)
    assert (response is not None)


def querypoibusinessdistricttest():
    querypoibusinessdistrict = QueryPoiBusinessDistrictRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                                               '24b4e5e0e94119930686399d02439415013ab013', '上海')
    client = DZClient(querypoibusinessdistrict)
    response = client.invoke()
    print(response)
    assert (response is not None)


def queryregionstest():
    queryregions = QueryRegionsRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                       '24b4e5e0e94119930686399d02439415013ab013', '上海')
    client = DZClient(queryregions)
    response = client.invoke()
    print(response)
    assert (response is not None)


def queryshoppoidetailstest():
    queryshoppoidetail = QueryShopPoiDetailRequest(1000069, '6862bd6012020b0fd385652905db18d4c9eaa835',
                                                   '24b4e5e0e94119930686399d02439415013ab013', '123', '12', '', '', '',
                                                   '')
    client = DZClient(queryshoppoidetail)
    response = client.invoke()
    print(response)
    assert (response is not None)


if __name__ == '__main__':
    querycategorietest()
    querycitybyprovincenametest()
    querycitytest()
    queryhomeprovincenametest()
    queryopencategorynametest()
    queryoverseacitytest()
    queryoverseaprovincetest()
    querypoibusinessdistricttest
    queryregionstest()
    queryshoppoidetailstest()
