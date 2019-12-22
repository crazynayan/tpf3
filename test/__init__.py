from unittest import TestCase

from requests import Response, post, get, delete

from config import config


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

    @staticmethod
    def get_url(url: str) -> str:
        return f"{config.SERVER_URL}{url}"

    @classmethod
    def authenticate(cls) -> str:
        response: Response = post(cls.get_url('/tokens'), auth=(config.USERNAME, config.PASSWORD))
        if response.status_code != 200:
            return str()
        token: dict = response.json()
        return token['token'] if 'token' in token else str()

    @classmethod
    def setup_authorization_header(cls, parameters: dict) -> dict:
        if not cls.TOKEN:
            cls.TOKEN = cls.authenticate()
        parameters['headers'] = {'Authorization': f"Bearer {cls.TOKEN}"}
        return parameters

    @classmethod
    def get(cls, url, **kwargs) -> Response:
        kwargs = cls.setup_authorization_header(kwargs)
        response: Response = get(cls.get_url(url), **kwargs)
        if response.status_code == 401:
            cls.TOKEN = str()
        return response

    @classmethod
    def post(cls, url, **kwargs) -> Response:
        kwargs = cls.setup_authorization_header(kwargs)
        response: Response = post(cls.get_url(url), **kwargs)
        if response.status_code == 401:
            cls.TOKEN = str()
        return response

    @classmethod
    def delete(cls, url, **kwargs) -> Response:
        kwargs = cls.setup_authorization_header(kwargs)
        response: Response = delete(cls.get_url(url), **kwargs)
        if response.status_code == 401:
            cls.TOKEN = str()
        return response
