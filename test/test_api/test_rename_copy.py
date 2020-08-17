from requests import Response

from test import TestAPI
from test.test_api.constants import ACTION, Actions, NAME, NEW_NAME, SEG_NAME, Types, TYPE, ErrorMsg


class Rename(TestAPI):

    def setUp(self):
        self.rename_body = {
            ACTION: Actions.RENAME,
            NAME: TestAPI.NAME,
            NEW_NAME: str()
        }
        self.rename_response = {
            "id": str(),
            NAME: str(),
            SEG_NAME: TestAPI.SEG_NAME,
            TYPE: Types.INPUT_HEADER
        }
        response = self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: TestAPI.NAME,
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
        # Test no name and and no new_name
        error_response = {
            NAME: ErrorMsg.NOT_EMPTY,
            NEW_NAME: ErrorMsg.NOT_EMPTY
        }
        response = self.post("/api/test_data", json={ACTION: Actions.RENAME})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.json())
        # Test empty name and new_name
        error_response = {
            NAME: ErrorMsg.NOT_EMPTY,
            NEW_NAME: ErrorMsg.NOT_EMPTY
        }
        self.rename_body[NAME] = "  "
        self.rename_body[NEW_NAME] = "       "
        response = self.post("/api/test_data", json=self.rename_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.json())
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
        self.rename_body[NEW_NAME] = self.NAME_101
        response = self.post(f"/api/test_data", json=self.rename_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.json())
        # Test valid longest name
        response = self._rename_test_data(self.NAME_100)
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(self.rename_response, response.json())


class Copy(TestAPI):

    def setUp(self):
        self.copy_body = {
            ACTION: Actions.COPY,
            NAME: TestAPI.NAME,
            NEW_NAME: str()
        }
        self.copy_response = [{
            "id": str(),
            NAME: str(),
            SEG_NAME: TestAPI.SEG_NAME,
            TYPE: Types.INPUT_HEADER
        }]
        self.cleanup = [TestAPI.NAME]
        self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})

    def _copy_test_data(self, new_name: str) -> Response:
        self.cleanup.append(new_name)
        self.copy_body[NEW_NAME] = new_name
        response = self.post(f"/api/test_data", json=self.copy_body)
        self.copy_response[0][NAME] = new_name
        self.copy_response[0]["id"] = response.json()[0]["id"]
        return response

    def tearDown(self):
        for name in self.cleanup:
            self.delete(f"/api/test_data", params={NAME: name})

    def test_copy(self):
        response = self._copy_test_data(f"{TestAPI.NAME} - 2")
        self.assertEqual(200, response.status_code)
        self.assertListEqual(self.copy_response, response.json())

    def test_basic_errors(self):
        # Test no name and and no new_name
        error_response = {
            NAME: ErrorMsg.NOT_EMPTY,
            NEW_NAME: ErrorMsg.NOT_EMPTY
        }
        response = self.post("/api/test_data", json={ACTION: Actions.COPY})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.json())
        # Test empty name and new_name
        error_response = {
            NAME: ErrorMsg.NOT_EMPTY,
            NEW_NAME: ErrorMsg.NOT_EMPTY
        }
        self.copy_body[NAME] = "  "
        self.copy_body[NEW_NAME] = "       "
        response = self.post("/api/test_data", json=self.copy_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.json())
        # Test name not found and new_name not unique
        error_response = {
            NAME: ErrorMsg.NOT_FOUND,
            NEW_NAME: ErrorMsg.UNIQUE
        }
        self.copy_body[NAME] = "some invalid name"
        self.copy_body[NEW_NAME] = TestAPI.NAME
        response = self.post("/api/test_data", json=self.copy_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.json())

    def test_long_names(self):
        # Test invalid name
        error_response = {
            NEW_NAME: ErrorMsg.LESS_100
        }
        self.copy_body[NEW_NAME] = self.NAME_101
        response = self.post(f"/api/test_data", json=self.copy_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.json())
        # Test valid longest name
        response = self._copy_test_data(self.NAME_100)
        self.assertEqual(200, response.status_code)
        self.assertListEqual(self.copy_response, response.json())
