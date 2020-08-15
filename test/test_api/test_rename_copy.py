from random import choice

from requests import Response

from test import TestAPI
from test.test_api.constants import ACTION, Action, NAME, NEW_NAME, SEG_NAME, Types, TYPE, ErrorMsg


class RenameCopy(TestAPI):

    def setUp(self):
        self.rename_body = {
            ACTION: Action.RENAME,
            NAME: TestAPI.NAME,
            NEW_NAME: str()
        }
        self.rename_response = {
            "id": str(),
            NAME: str(),
            SEG_NAME: TestAPI.SEG_NAME,
            TYPE: Types.INPUT_HEADER
        }
        response = self.post(f"/api/test_data", json={ACTION: Action.CREATE, NAME: TestAPI.NAME,
                                                      SEG_NAME: TestAPI.SEG_NAME})
        self.rename_response["id"] = response.json()["id"]
        self.cleanup = [TestAPI.NAME]

    def _rename_test_data(self, new_name: str) -> Response:
        self.cleanup.append(new_name)
        self.rename_body[NEW_NAME] = new_name
        self.rename_response[NAME] = new_name
        response = self.post(f"/api/test_data", json=self.rename_body)
        return response

    def tearDown(self):
        for name in self.cleanup:
            self.delete(f"/api/test_data", params={NAME: name})

    def test_rename(self):
        response = self._rename_test_data(f"{TestAPI.NAME} - 2")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(self.rename_response, response.json())

    def test_basic_errors(self):
        empty_response = {
            NAME: ErrorMsg.NOT_EMPTY,
            NEW_NAME: ErrorMsg.NOT_EMPTY
        }
        # Test no name and and no new_name
        response = self.post("/api/test_data", json={ACTION: Action.RENAME})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(empty_response, response.json())
        # Test empty name and new_name
        self.rename_body[NAME] = "  "
        self.rename_body[NEW_NAME] = "       "
        response = self.post("/api/test_data", json=self.rename_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(empty_response, response.json())
        # Test name not found and new_name not unique
        error_response = {
            NAME: ErrorMsg.NOT_FOUND,
            NEW_NAME: ErrorMsg.UNIQUE
        }
        self.rename_body[NAME] = "some invalid name"
        self.rename_body[NEW_NAME] = TestAPI.NAME
        response = self.post("/api/test_data", json=self.rename_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.json())

    def test_long_names(self):
        # Test invalid name
        error_response = {
            NEW_NAME: ErrorMsg.LESS_100
        }
        long_101 = "NZ99 - an invalid name with 101 characters - "
        long_101 = f"{long_101}{''.join([str(choice(range(10))) for _ in range(101 - len(long_101))])}"
        self.rename_body[NEW_NAME] = long_101
        response = self.post(f"/api/test_data", json=self.rename_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.json())
        # Test valid longest name
        long_100 = "NZ99 - a valid name with 100 characters"
        long_100 = f"{long_100}{''.join([str(choice(range(10))) for _ in range(100 - len(long_100))])}"
        response = self._rename_test_data(long_100)
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(self.rename_response, response.json())
