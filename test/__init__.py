from unittest import TestCase

from requests import Response, post, get, delete

from config import config


class TestAPI(TestCase):
    TOKEN = str()

    def setUp(self) -> None:
        if not self.TOKEN:
            self.TOKEN = self.authenticate()
        self.test_data_dict = {'name': 'ETA5 Testing 123', 'seg_name': 'ETA5'}
        response = self.post(f"/test_data", json=self.test_data_dict)
        self.test_data_dict['id'] = response.json()['id']
        response = self.get(f"/test_data/{self.test_data_dict['id']}")
        self.test_data_dict['outputs'] = [{'cores': list(), 'dumps': list(), 'id': response.json()['outputs'][0]['id'],
                                           'last_line': str(), 'messages': list(), 'reg_pointers': dict(),
                                           'regs': dict()}]
        self.test_data_dict['cores'] = list()
        self.test_data_dict['errors'] = list()
        self.test_data_dict['fixed_files'] = list()
        self.test_data_dict['partition'] = str()
        self.test_data_dict['pnr'] = list()
        self.test_data_dict['regs'] = dict()
        self.test_data_dict['tpfdf'] = list()

    def tearDown(self) -> None:
        self.delete(f"/test_data/{self.test_data_dict['id']}")

    @staticmethod
    def get_url(url: str) -> str:
        return f"{config.SERVER_URL}{url}"

    def authenticate(self) -> str:
        response: Response = post(self.get_url('/tokens'), auth=(config.USERNAME, config.PASSWORD))
        if response.status_code != 200:
            return str()
        token: dict = response.json()
        return token['token'] if 'token' in token else str()

    def setup_authorization_header(self, parameters: dict) -> dict:
        if not self.TOKEN:
            self.TOKEN = self.authenticate()
        parameters['headers'] = {'Authorization': f"Bearer {self.TOKEN}"}
        return parameters

    def get(self, url, **kwargs) -> Response:
        kwargs = self.setup_authorization_header(kwargs)
        response: Response = get(self.get_url(url), **kwargs)
        if response.status_code == 401:
            self.TOKEN = str()
        return response

    def post(self, url, **kwargs) -> Response:
        kwargs = self.setup_authorization_header(kwargs)
        response: Response = post(self.get_url(url), **kwargs)
        if response.status_code == 401:
            self.TOKEN = str()
        return response

    def delete(self, url, **kwargs) -> Response:
        kwargs = self.setup_authorization_header(kwargs)
        response: Response = delete(self.get_url(url), **kwargs)
        if response.status_code == 401:
            self.TOKEN = str()
        return response
