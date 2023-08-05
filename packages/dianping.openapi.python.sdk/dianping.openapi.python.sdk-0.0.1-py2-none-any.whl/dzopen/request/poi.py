from dzauth import Sign


class Open_points:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude


class QueryPoiRequest(Sign):
    open_points = Open_points

    def __init__(self, app_key, app_secret, session, deviceId, user_id=None, city=None, region=None,
                 latitude=None, longitude=None, open_points=None, offset_type=0, radius=20000,
                 category=None, keyword=None, has_coupon=None,
                 has_deal=None, has_online_reservation=None, sort=1, limit=25, page=1):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_httpmethod("GET")
        self.set_url('https://openapi.dianping.com/router/poi/querypoi')

        self.set_deviceId(deviceId)
        self.set_user_id(user_id)
        self.set_city(city)
        self.set_region(region)
        self.set_latitude(latitude)
        self.set_longitude(longitude)
        self.set_open_points(open_points)
        self.set_offset_type(offset_type)
        self.set_radius(radius)
        self.set_category(category)
        self.set_keyword(keyword)
        self.set_has_coupon(has_coupon)
        self.set_has_deal(has_deal)
        self.set_has_online_reservation(has_online_reservation)
        self.set_sort(sort)
        self.set_limit(limit)
        self.set_page(page)

    def set_deviceId(self, deviceId):
        self.add_query_param('deviceId', deviceId)

    def set_user_id(self, user_id):
        self.add_query_param('user_id', user_id)

    def set_city(self, city):
        self.add_query_param('city', city)

    def set_region(self, region):
        self.add_query_param('region', region)

    def set_latitude(self, latitude):
        self.add_query_param('latitude', latitude)

    def set_longitude(self, longitude):
        self.add_query_param('longitude', longitude)

    def set_open_points(self, open_points):
        self.add_query_param('open_points', open_points)

    def set_offset_type(self, offset_type):
        self.add_query_param('offset_type', offset_type)

    def set_radius(self, radius):
        self.add_query_param('radius', radius)

    def set_category(self, category):
        self.add_query_param('category', category)

    def set_keyword(self, keyword):
        self.add_query_param('keyword', keyword)

    def set_has_coupon(self, has_coupon):
        self.add_query_param('has_coupon', has_coupon)

    def set_has_deal(self, has_deal):
        self.add_query_param('has_deal', has_deal)

    def set_has_online_reservation(self, has_online_reservation):
        self.add_query_param('has_deal', has_online_reservation)

    def set_sort(self, sort):
        self.add_query_param('sort', sort)

    def set_limit(self, limit):
        self.add_query_param('limit', limit)

    def set_page(self, page):
        self.add_query_param('page', page)


class QueryShopPoiDetailRequest(Sign):
    def __init__(self, app_key, app_secret, session, deviceId, user_id, latitude, longitude, utmSource, utmMedium,
                 business_id=0):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_httpmethod("GET")
        self.set_url('https://openapi.dianping.com/router/poi/querypoidetail')

        self.set_deviceId(deviceId)
        self.set_user_id(user_id)
        self.set_latitude(latitude)
        self.set_longitude(longitude)

        self.set_utmSource(utmSource)
        self.set_utmMedium(utmMedium)
        self.set_business_id(business_id)

    def set_deviceId(self, deviceId):
        self.add_query_param('deviceId', deviceId)

    def set_user_id(self, user_id):
        self.add_query_param('user_id', user_id)

    def set_latitude(self, latitude):
        self.add_query_param('latitude', latitude)

    def set_longitude(self, longitude):
        self.add_query_param('longitude', longitude)

    def set_utmSource(self, utmSource):
        self.add_query_param('utmSource', utmSource)

    def set_utmMedium(self, utmMedium):
        self.add_query_param('utmMedium', utmMedium)

    def set_business_id(self, business_id):
        self.add_query_param('business_id', business_id)


class QueryCitysRequest(Sign):
    def __init__(self, app_key, app_secret, session):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_httpmethod("GET")
        self.set_url('https://openapi.dianping.com/router/poi/querycitys')


class QueryRegionsRequest(Sign):
    def __init__(self, app_key, app_secret, session, city_name=None):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_httpmethod("GET")
        self.set_url('https://openapi.dianping.com/router/poi/queryregions')

        self.set_city_name(city_name)

    def set_city_name(self, city_name):
        self.add_query_param('city_name', city_name)


class QueryCategoriesRequest(Sign):
    def __init__(self, app_key, app_secret, session, city_name):
        Sign.__init__(self)

        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_httpmethod("GET")
        self.set_url('https://openapi.dianping.com/router/poi/querycategories')

        self.set_city_name(city_name)

    def set_city_name(self, city_name):
        self.add_query_param('city_name', city_name)


class QueryOverSeasCitiesRequest(Sign):
    def __init__(self, app_key, app_secret, session):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_httpmethod("GET")
        self.set_url('https://openapi.dianping.com/router/poi/queryOverSeasCities')


class QueryHomeProvincesRequest(Sign):
    def __init__(self, app_key, app_secret, session):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_httpmethod("GET")
        self.set_url('https://openapi.dianping.com/router/poi/queryHomeProvinces')


class QueryOverseasProvinces(Sign):
    def __init__(self, app_key, app_secret, session):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_httpmethod("GET")
        self.set_url('https://openapi.dianping.com/router/poi/queryOverseasProvinces')


class QueryCitiesByProvinceNameRequest(Sign):
    def __init__(self, app_key, app_secret, session, province_name):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_httpmethod("GET")
        self.set_url('https://openapi.dianping.com/router/poi/queryCitiesByProvinceName')
        self.set_province_name(province_name)

    def set_province_name(self, province_name):
        self.add_query_param('province_name', province_name)


class QueryPoiBusinessDistrictRequest(Sign):
    def __init__(self, app_key, app_secret, session, city_name):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_httpmethod("GET")
        self.set_url('https://openapi.dianping.com/router/poi/queryPoiBusinessDistrict')
        self.set_city_name(city_name)

    def set_city_name(self, city_name):
        self.add_query_param('city_name', city_name)


class QueryOpenCategoryNameRequest(Sign):
    def __init__(self, app_key, app_secret, session, city_name):
        Sign.__init__(self)
        self.set_app_key(app_key)
        self.set_secret(app_secret)
        self.set_session(session)
        self.set_httpmethod("GET")
        self.set_url('https://openapi.dianping.com/router/poi/queryOpenCategoryName')
        self.set_city_name(city_name)

    def set_city_name(self, city_name):
        self.add_query_param('city_name', city_name)
