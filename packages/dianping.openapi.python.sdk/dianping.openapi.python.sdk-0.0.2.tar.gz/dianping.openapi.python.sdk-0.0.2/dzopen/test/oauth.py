from client import DZClient
from request.oauth import AuthorizePlatformRequest
from request.oauth import RefreshTokenRequest


def platformauthtest():
    authorize_request = AuthorizePlatformRequest('1000069', '6862bd6012020b0fd385652905db18d4c9eaa835')
    client = DZClient(authorize_request)
    response = client.invoke()
    print(response)
    assert (response is not None)


def refreshtokentest():
    refreshreq = RefreshTokenRequest('17', '6A23F2D41F73902EFCC9B6B3F076D74B',
                                     '172e69a5b9e5d8245d012e66665ccb08cfbe116d')
    client = DZClient(refreshreq)
    response = client.invoke()
    print(response)
    assert (response is not None)


if __name__ == '__main__':
    platformauthtest()
    refreshtokentest()
