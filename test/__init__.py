from functools import wraps
from random import choice
from unittest import TestCase

from requests import Response, post, get, delete, patch

from config import config


def authenticated_request(func):
    @wraps(func)
    def request_wrapper(self, url: str, **kwargs):
        url = f"{config.SERVER_URL}{url}"
        if not config.TOKEN:
            config.TOKEN = post(f"{config.SERVER_URL}/tokens", auth=(config.USERNAME, config.PASSWORD)).json()['token']
        kwargs['headers'] = {'Authorization': f"Bearer {config.TOKEN}"}
        response = func(self, url, **kwargs)
        if response.status_code == 401:
            config.TOKEN = str()
        return response

    return request_wrapper


class TestAPI(TestCase):
    NAME = "NZ99 - ETA5 - Testing 123"
    SEG_NAME = "ETA5"
    NAME_100 = "NZ99 - a valid name with 100 characters - "
    NAME_100 = f"{NAME_100}{''.join([str(choice(range(10))) for _ in range(100 - len(NAME_100))])}"
    NAME_101 = "NZ99 - an invalid name with 101 characters - "
    NAME_101 = f"{NAME_101}{''.join([str(choice(range(10))) for _ in range(101 - len(NAME_101))])}"

    def get_sample_test_data(self) -> dict:
        if config.TEST_DATA:
            return config.TEST_DATA
        response = self.get(f"/test_data", params={'name': self.NAME})
        if response.status_code == 200:
            test_data_id = response.json()[0]['id']
            # response = self.get(f"/test_data/{test_data_id}")
            # config.TEST_DATA = response.json()
            # return config.TEST_DATA
            self.delete(f"/test_data/{test_data_id}")
        response = self.post(f"/test_data", json={'name': self.NAME, 'seg_name': self.SEG_NAME})
        if response.status_code != 200:
            raise TypeError
        config.TEST_DATA = response.json()
        return config.TEST_DATA

    def get_test_data(self, reason: str, seg_name: str = None) -> dict:
        if not seg_name:
            seg_name = self.SEG_NAME
        response = self.post(f"/test_data", json={'name': f"{self.NAME}{reason}", 'seg_name': seg_name})
        if response.status_code != 200:
            raise TypeError
        return response.json()

    def delete_test_data(self, test_data_id: str) -> Response:
        return self.delete(f"/test_data/{test_data_id}")

    @authenticated_request
    def get(self, url: str, **kwargs) -> Response:
        return get(url, **kwargs)

    @authenticated_request
    def post(self, url: str, **kwargs) -> Response:
        return post(url, **kwargs)

    @authenticated_request
    def patch(self, url: str, **kwargs) -> Response:
        return patch(url, **kwargs)

    @authenticated_request
    def delete(self, url: str, **kwargs) -> Response:
        return delete(url, **kwargs)
