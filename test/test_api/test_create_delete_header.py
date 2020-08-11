from test import TestAPI
from test.test_api.constants import ErrorMsg, Types, NAME, SEG_NAME, TYPE, SuccessMsg, TEST_DATA


# noinspection DuplicatedCode
class CreateDeleteHeader(TestAPI):

    def setUp(self):
        self.cleanup: bool = False

    def tearDown(self):
        if self.cleanup:
            self.delete(f"/api/test_data", params={NAME: TestAPI.NAME})

    def test_create(self):
        self.cleanup = True
        response = self.post("/api/test_data", json={NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertEqual(TestAPI.NAME, response_body[NAME])
        self.assertEqual(TestAPI.SEG_NAME, response_body[SEG_NAME])
        self.assertEqual(Types.INPUT_HEADER, response_body[TYPE])
        self.assertIn("id", response_body)
        self.assertEqual(4, len(response_body))

    def test_duplicate(self):
        self.cleanup = True
        self.post("/api/test_data", json={NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
        response = self.post("/api/test_data", json={NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
        self.assertEqual(400, response.status_code)
        response_body = response.json()
        self.assertEqual(ErrorMsg.UNIQUE, response_body[NAME])
        self.assertEqual(1, len(response_body))

    def test_long_name_and_seg_not_in_library(self):
        body = {
            SEG_NAME: "some invalid segment",
            NAME: "an invalid name with 101 characters "
                  "01234012345678901234567890123456789012345678901234567890123456789"
        }
        response = self.post("/api/test_data", json=body)
        self.assertEqual(400, response.status_code)
        response_body = response.json()
        self.assertEqual(ErrorMsg.LESS_100, response_body[NAME])
        self.assertEqual(ErrorMsg.SEG_LIBRARY, response_body[SEG_NAME])
        self.assertEqual(2, len(response_body))

    def test_invalid_type_and_lower_case_seg_name_and_space_padding_in_name(self):
        self.cleanup = True
        body = {NAME: f"  {TestAPI.NAME}  ", SEG_NAME: TestAPI.SEG_NAME.lower(), TYPE: Types.PNR}
        response = self.post("/api/test_data", json=body)
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertEqual(TestAPI.NAME, response_body[NAME])
        self.assertEqual(TestAPI.SEG_NAME, response_body[SEG_NAME])
        self.assertEqual(Types.INPUT_HEADER, response_body[TYPE])
        self.assertIn("id", response_body)
        self.assertEqual(4, len(response_body))

    def test_empty_body(self):
        response = self.post("/api/test_data", json=dict())
        self.assertEqual(400, response.status_code)
        response_body = response.json()
        self.assertEqual(ErrorMsg.NOT_EMPTY, response_body[NAME])
        self.assertEqual(ErrorMsg.NOT_EMPTY, response_body[SEG_NAME])
        self.assertEqual(2, len(response_body))

    def test_with_space_padding(self):
        response = self.post("/api/test_data", json={NAME: "    ", SEG_NAME: "   "})
        self.assertEqual(400, response.status_code)
        response_body = response.json()
        self.assertEqual(ErrorMsg.NOT_EMPTY, response_body[NAME])
        self.assertEqual(ErrorMsg.NOT_EMPTY, response_body[SEG_NAME])
        self.assertEqual(2, len(response_body))

    def test_longest_name_and_invalid_extra_fields(self):
        long_name = "a valid name with 100 characters " \
                    "0123456012345678901234567890123456789012345678901234567890123456789"
        response = self.post("/api/test_data", json={NAME: long_name, SEG_NAME: TestAPI.SEG_NAME, "error": "invalid"})
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertEqual(long_name, response_body[NAME])
        self.assertEqual(TestAPI.SEG_NAME, response_body[SEG_NAME])
        self.assertEqual(Types.INPUT_HEADER, response_body[TYPE])
        self.assertIn("id", response_body)
        self.assertEqual(4, len(response_body))
        self.delete(f"/api/test_data", params={NAME: long_name})

    def test_delete_success(self):
        self.post("/api/test_data", json={NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
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
        second_name = f"{TestAPI.NAME} 2"
        self.post("/api/test_data", json={NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
        self.post("/api/test_data", json={NAME: second_name, SEG_NAME: TestAPI.SEG_NAME})
        response = self.get(f"/api/test_data")
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertEqual(2, len(response_body))
        self.assertEqual(4, len(response_body[0]))
        self.assertIn("id", response_body[1])
        self.assertEqual(second_name, next(test_data[NAME] for test_data in response_body
                                           if test_data[NAME] == second_name))
        self.delete("/api/test_data", params={NAME: second_name})

    def test_get_by_name(self):
        self.cleanup = True
        self.post("/api/test_data", json={NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
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
