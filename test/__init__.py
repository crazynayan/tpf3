from functools import wraps
from unittest import TestCase

from requests import Response, post, get, delete

from config import config


def authenticated_request(func):
    @wraps(func)
    def request_wrapper(cls, url: str, **kwargs):
        url = f"{config.SERVER_URL}{url}"
        if 'auth' not in kwargs:
            if not cls.TOKEN:
                cls.TOKEN = cls.authenticate()
            kwargs['headers'] = {'Authorization': f"Bearer {cls.TOKEN}"}
        response = func(cls, url, **kwargs)
        if response.status_code == 401:
            cls.TOKEN = str()
        return response

    return request_wrapper


class TestAPI(TestCase):
    TOKEN = str()
    TEST_DATA = dict()

    @classmethod
    def setUpClass(cls) -> None:
        if not cls.TOKEN:
            cls.TOKEN = cls.authenticate()
        cls.TEST_DATA = {'name': 'ETA5 Testing 123', 'seg_name': 'ETA5'}
        response = cls.post(f"/test_data", json=cls.TEST_DATA)
        cls.TEST_DATA = response.json()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.delete(f"/test_data/{cls.TEST_DATA['id']}")

    @classmethod
    def authenticate(cls) -> str:
        response: Response = cls.post('/tokens', auth=(config.USERNAME, config.PASSWORD))
        if response.status_code != 200:
            return str()
        token: dict = response.json()
        return token['token'] if 'token' in token else str()

    @classmethod
    @authenticated_request
    def get(cls, url: str, **kwargs) -> Response:
        return get(url, **kwargs)

    @classmethod
    @authenticated_request
    def post(cls, url: str, **kwargs) -> Response:
        return post(url, **kwargs)

    @classmethod
    @authenticated_request
    def delete(cls, url: str, **kwargs) -> Response:
        return delete(url, **kwargs)
