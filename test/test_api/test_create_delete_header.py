from random import choice

from test import TestAPI
from test.test_api.constants import ErrorMsg, Types, NAME, SEG_NAME, TYPE, SuccessMsg, TEST_DATA, ACTION, Action


# noinspection DuplicatedCode
class CreateDeleteHeader(TestAPI):

    def setUp(self):
        self.cleanup: bool = False
        self.create_body: dict = {
            NAME: TestAPI.NAME,
            SEG_NAME: TestAPI.SEG_NAME,
            ACTION: Action.CREATE
        }
        self.long_101 = "NZ99 - an invalid name with 101 characters - "
        self.long_101 = f"{self.long_101}{''.join([str(choice(range(10))) for _ in range(101 - len(self.long_101))])}"
        self.long_100 = "NZ99 - a valid name with 100 characters"
        self.long_100 = f"{self.long_100}{''.join([str(choice(range(10))) for _ in range(100 - len(self.long_100))])}"
        self.cleanup_100 = False
        self.second_name = f"{TestAPI.NAME} 2"
        self.cleanup_second = False

    def tearDown(self):
        if self.cleanup:
            self.delete(f"/api/test_data", params={NAME: TestAPI.NAME})
        if self.cleanup_100:
            self.delete(f"/api/test_data", params={NAME: self.long_100})
        if self.cleanup_second:
            self.delete(f"/api/test_data", params={NAME: self.second_name})

    def test_create(self):
        self.cleanup = True
        response = self.post("/api/test_data", json=self.create_body)
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertEqual(TestAPI.NAME, response_body[NAME])
        self.assertEqual(TestAPI.SEG_NAME, response_body[SEG_NAME])
        self.assertEqual(Types.INPUT_HEADER, response_body[TYPE])
        self.assertIn("id", response_body)
        self.assertEqual(4, len(response_body))

    def test_duplicate(self):
        self.cleanup = True
        self.post("/api/test_data", json=self.create_body)
        response = self.post("/api/test_data", json=self.create_body)
        self.assertEqual(400, response.status_code)
        response_body = response.json()
        self.assertEqual(ErrorMsg.UNIQUE, response_body[NAME])
        self.assertEqual(1, len(response_body))

    def test_long_name_and_seg_not_in_library(self):
        self.assertEqual(101, len(self.long_101))
        self.create_body[NAME] = self.long_101
        self.create_body[SEG_NAME] = "some invalid segment"
        response = self.post("/api/test_data", json=self.create_body)
        self.assertEqual(400, response.status_code)
        response_body = response.json()
        self.assertEqual(ErrorMsg.LESS_100, response_body[NAME])
        self.assertEqual(ErrorMsg.SEG_LIBRARY, response_body[SEG_NAME])
        self.assertEqual(2, len(response_body))

    def test_invalid_type_and_lower_case_seg_name_and_space_padding_in_name(self):
        self.cleanup = True
        body = {NAME: f"  {TestAPI.NAME}  ", SEG_NAME: TestAPI.SEG_NAME.lower(), TYPE: Types.PNR, ACTION: Action.CREATE}
        response = self.post("/api/test_data", json=body)
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertEqual(TestAPI.NAME, response_body[NAME])
        self.assertEqual(TestAPI.SEG_NAME, response_body[SEG_NAME])
        self.assertEqual(Types.INPUT_HEADER, response_body[TYPE])
        self.assertIn("id", response_body)
        self.assertEqual(4, len(response_body))

    def test_empty_body(self):
        # Complete empty body will give action not empty
        response = self.post("/api/test_data", json=dict())
        self.assertEqual(400, response.status_code)
        self.assertEqual({ACTION: ErrorMsg.NOT_EMPTY}, response.json())
        # Create action will say name and seg_name must not be empty
        response = self.post("/api/test_data", json={ACTION: Action.CREATE})
        self.assertEqual(400, response.status_code)
        response_body = response.json()
        self.assertEqual(ErrorMsg.NOT_EMPTY, response_body[NAME])
        self.assertEqual(ErrorMsg.NOT_EMPTY, response_body[SEG_NAME])
        self.assertEqual(2, len(response_body))

    def test_with_space_padding(self):
        response = self.post("/api/test_data", json={NAME: "    ", SEG_NAME: "   ", ACTION: Action.CREATE})
        self.assertEqual(400, response.status_code)
        response_body = response.json()
        self.assertEqual(ErrorMsg.NOT_EMPTY, response_body[NAME])
        self.assertEqual(ErrorMsg.NOT_EMPTY, response_body[SEG_NAME])
        self.assertEqual(2, len(response_body))

    def test_longest_name_and_invalid_extra_fields(self):
        self.create_body[NAME] = self.long_100
        self.create_body["error"] = "invalid"
        self.cleanup_100 = True
        response = self.post("/api/test_data", json=self.create_body)
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertEqual(self.long_100, response_body[NAME])
        self.assertEqual(TestAPI.SEG_NAME, response_body[SEG_NAME])
        self.assertEqual(Types.INPUT_HEADER, response_body[TYPE])
        self.assertIn("id", response_body)
        self.assertEqual(4, len(response_body))

    def test_delete_success(self):
        self.post("/api/test_data", json=self.create_body)
        response = self.delete(f"/api/test_data", params={NAME: TestAPI.NAME})
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertEqual(SuccessMsg.DELETE, response_body[TEST_DATA])
        self.assertEqual(1, len(response_body))

    def test_delete_fail(self):
        response = self.delete(f"/api/test_data", params={NAME: TestAPI.NAME})
        self.assertEqual(404, response.status_code)
        response_body = response.json()
        self.assertEqual(ErrorMsg.NOT_FOUND, response_body[TEST_DATA])
        self.assertEqual(1, len(response_body))

    def test_delete_fail_with_no_params(self):
        response = self.delete(f"/api/test_data")
        self.assertEqual(404, response.status_code)
        response_body = response.json()
        self.assertEqual(ErrorMsg.NOT_FOUND, response_body[TEST_DATA])
        self.assertEqual(1, len(response_body))

    def test_get_all(self):
        self.cleanup = True
        self.post("/api/test_data", json=self.create_body)
        self.cleanup_second = True
        self.create_body[NAME] = self.second_name
        self.post("/api/test_data", json=self.create_body)
        response = self.get(f"/api/test_data")
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertEqual(2, len(response_body))
        self.assertEqual(4, len(response_body[0]))
        self.assertIn("id", response_body[1])
        self.assertEqual(self.second_name, next(test_data[NAME] for test_data in response_body
                                                if test_data[NAME] == self.second_name))

    def test_get_by_name(self):
        self.cleanup = True
        self.post("/api/test_data", json=self.create_body)
        response = self.get(f"/api/test_data", params={NAME: TestAPI.NAME})
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertEqual(1, len(response_body))
        self.assertEqual(4, len(response_body[0]))
        self.assertIn("id", response_body[0])
        self.assertEqual(TestAPI.NAME, response_body[0][NAME])
        # Invalid Name - Will return an empty list
        response = self.get(f"/api/test_data", params={NAME: "invalid name"})
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertListEqual(list(), response_body)
        # Empty Name - Will return an empty list
        response = self.get(f"/api/test_data", params={NAME: ""})
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertListEqual(list(), response_body)
        # Invalid Parameter - Will work as get all
        response = self.get(f"/api/test_data", params={"invalid": "invalid"})
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertEqual(1, len(response_body))

    def test_invalid_action(self):
        # No action
        response = self.post(f"/api/test_data")
        self.assertEqual(400, response.status_code)
        self.assertEqual({ACTION: ErrorMsg.NOT_EMPTY}, response.json())
        # Action with just spaces
        self.create_body[ACTION] = " "
        response = self.post(f"/api/test_data", json=self.create_body)
        self.assertEqual(400, response.status_code)
        self.assertEqual({ACTION: ErrorMsg.NOT_EMPTY}, response.json())
        self.create_body[ACTION] = " invalid "
        response = self.post(f"/api/test_data", json=self.create_body)
        self.assertEqual(400, response.status_code)
        self.assertEqual({ACTION: ErrorMsg.INVALID_ACTION}, response.json())
