from test import TestAPI
from test.test_api.constants import TYPE, Types, FIELD_DATA, FIELD, DATA, MACRO_NAME, Actions, ACTION, NAME, SEG_NAME, \
    SuccessMsg, ErrorMsg


class InputCoreBlock(TestAPI):

    def setUp(self):
        self.update_body = {
            NAME: TestAPI.NAME,
            ACTION: Actions.UPDATE,
            TYPE: Types.INPUT_CORE_BLOCK,
            FIELD_DATA: [
                {FIELD: "WA0BBR", DATA: "F1F2"}
            ]
        }
        self.response = {
            "id": str(),
            NAME: TestAPI.NAME,
            TYPE: Types.INPUT_CORE_BLOCK,
            MACRO_NAME: "WA0AA",
            FIELD_DATA: [
                {FIELD: "WA0BBR", DATA: "F1F2"}
            ]
        }
        self.delete_body = {
            NAME: TestAPI.NAME,
            ACTION: Actions.DELETE,
            TYPE: Types.INPUT_CORE_BLOCK,
            MACRO_NAME: "WA0AA",
            FIELD_DATA: [  # IF field data is not specified then the entire core block is deleted
                {FIELD: "WA0BBR"}
            ]
        }
        self.cleanup = list()

    def tearDown(self):
        for name in self.cleanup:
            self.delete(f"/api/test_data", params={NAME: name})

    def test_create_update_delete(self):
        self.cleanup.append(TestAPI.NAME)
        self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
        # Test Create with one field
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(200, response.status_code, response.json())
        self.response["id"] = response.json()["id"]
        self.assertDictEqual(self.response, response.json())
        # Update the same core block
        self.update_body[FIELD_DATA] = [
            {FIELD: "  wa0bbr  ", DATA: " f3f4"},
            {FIELD: "#wa0tty", DATA: "01"}
        ]
        self.response[FIELD_DATA] = [
            {FIELD: "WA0BBR", DATA: " f3f4"},
            {FIELD: "#WA0TTY", DATA: "01"}
        ]
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(200, response.status_code, response.json())
        self.assertDictEqual(self.response, response.json())
        # Remove one field
        self.delete_body[FIELD_DATA][0][FIELD] = "Wa0bbr "
        self.response[FIELD_DATA] = [{FIELD: "#WA0TTY", DATA: "01"}]
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(200, response.status_code, response.json())
        self.assertDictEqual(self.response, response.json())
        # Remove the last remaining field
        self.delete_body[FIELD_DATA][0][FIELD] = " #Wa0tty"
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(200, response.status_code, response.json())
        self.assertDictEqual({Types.INPUT_CORE_BLOCK: SuccessMsg.DELETE}, response.json())

    def test_create_multiple_and_delete_all(self):
        self.cleanup.append(TestAPI.NAME)
        self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
        # Test create with multiple field
        self.update_body[FIELD_DATA] = self.response[FIELD_DATA] = [
            {FIELD: "WA0BBR", DATA: "F1F2"},
            {FIELD: "#WA0TTY", DATA: "01"}
        ]
        self.update_body[NAME] = f"  {TestAPI.NAME}  "
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(200, response.status_code, response.json())
        self.response["id"] = response.json()["id"]
        self.assertDictEqual(self.response, response.json())
        # Test delete all
        del self.delete_body[FIELD_DATA]
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(200, response.status_code, response.json())
        self.assertDictEqual({Types.INPUT_CORE_BLOCK: SuccessMsg.DELETE}, response.json())

    # noinspection DuplicatedCode
    def test_basic_errors_for_update(self):
        # Invalid type
        response = self.post(f"/api/test_data", json={ACTION: Actions.UPDATE, TYPE: "Invalid Type"})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({TYPE: ErrorMsg.INVALID_TYPE}, response.json())
        # No Test data name
        update_body = {ACTION: Actions.UPDATE, TYPE: Types.INPUT_CORE_BLOCK}
        response = self.post(f"/api/test_data", json=update_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({NAME: ErrorMsg.NOT_EMPTY, FIELD_DATA: ErrorMsg.NOT_EMPTY}, response.json())
        # Empty Test data name
        update_body[NAME] = "  "
        response = self.post(f"/api/test_data", json=update_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({NAME: ErrorMsg.NOT_EMPTY, FIELD_DATA: ErrorMsg.NOT_EMPTY}, response.json())
        # Invalid Test data name
        update_body[NAME] = "Invalid name"
        response = self.post(f"/api/test_data", json=update_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({NAME: ErrorMsg.NOT_FOUND, FIELD_DATA: ErrorMsg.NOT_EMPTY}, response.json())

    # noinspection DuplicatedCode
    def test_basic_errors_for_delete(self):
        # Invalid type
        response = self.post(f"/api/test_data", json={ACTION: Actions.DELETE, TYPE: "Invalid Type"})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({TYPE: ErrorMsg.INVALID_TYPE}, response.json())
        delete_body = {ACTION: Actions.DELETE, TYPE: Types.INPUT_CORE_BLOCK}
        response = self.post(f"/api/test_data", json=delete_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({NAME: ErrorMsg.NOT_EMPTY, MACRO_NAME: ErrorMsg.NOT_EMPTY}, response.json())
        # Empty Test data name
        delete_body[NAME] = "  "
        delete_body[MACRO_NAME] = "      "
        response = self.post(f"/api/test_data", json=delete_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({NAME: ErrorMsg.NOT_EMPTY, MACRO_NAME: ErrorMsg.NOT_EMPTY}, response.json())
        # Invalid Test data name
        delete_body[NAME] = "Invalid name"
        response = self.post(f"/api/test_data", json=delete_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({NAME: ErrorMsg.NOT_FOUND, MACRO_NAME: ErrorMsg.NOT_EMPTY}, response.json())

    def test_field_data_errors_for_update(self):
        self.cleanup.append(TestAPI.NAME)
        self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
        self.post(f"/api/test_data", json=self.update_body)
        # Test various field_data errors
        self.update_body[FIELD_DATA] = [
            {DATA: "12"},
            {FIELD: " #wa0tty ", DATA: "12"},
            {FIELD: "#WA0TTY"},
            {FIELD: "EBW000", DATA: "12"},
            {},
            {FIELD: "invalid field", DATA: "any data"},
            {FIELD: " wa0bbr ", DATA: "F1F2"},
        ]
        error_response = {
            FIELD_DATA: [
                {FIELD: ErrorMsg.NOT_EMPTY},
                {},
                {FIELD: ErrorMsg.UNIQUE, DATA: ErrorMsg.NOT_EMPTY},
                {FIELD: f"{ErrorMsg.MACRO_SAME} WA0AA"},
                {FIELD: ErrorMsg.NOT_EMPTY, DATA: ErrorMsg.NOT_EMPTY},
                {FIELD: ErrorMsg.MACRO_LIBRARY},
                {DATA: ErrorMsg.DATA_SAME}
            ]
        }
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(400, response.status_code, response.json())
        self.assertDictEqual(error_response, response.json())
        # Test name errors along with field data and with no valid field
        self.update_body[NAME] = "invalid name"
        self.update_body[FIELD_DATA] = [
            {DATA: "12"},
            {FIELD: "invalid field"},
            {FIELD: " - ", DATA: "12"},
            {FIELD: "  "},
        ]
        error_response = {
            NAME: ErrorMsg.NOT_FOUND,
            FIELD_DATA: [
                {FIELD: ErrorMsg.NOT_EMPTY},
                {FIELD: ErrorMsg.MACRO_NOT_FOUND, DATA: ErrorMsg.NOT_EMPTY},
                {FIELD: ErrorMsg.MACRO_NOT_FOUND},
                {FIELD: ErrorMsg.NOT_EMPTY, DATA: ErrorMsg.NOT_EMPTY}
            ]
        }
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(400, response.status_code, response.json())
        self.assertDictEqual(error_response, response.json())

    def test_errors_for_delete(self):
        self.cleanup.append(TestAPI.NAME)
        self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
        self.post(f"/api/test_data", json=self.update_body)
        # Test various field_data errors
        self.delete_body[FIELD_DATA] = [
            {DATA: "12"},
            {FIELD: " Wa0bbr  ", DATA: "12"},
            {FIELD: " #wa0tty "},
            {FIELD: "EBW000"},
            {},
            {FIELD: "invalid field", DATA: "any data"},
            {FIELD: "WA0BBR"},
        ]
        error_response = {
            FIELD_DATA: [
                {FIELD: ErrorMsg.NOT_EMPTY},
                {},
                {FIELD: ErrorMsg.NOT_FOUND},
                {FIELD: f"{ErrorMsg.MACRO_SAME} WA0AA"},
                {FIELD: ErrorMsg.NOT_EMPTY},
                {FIELD: ErrorMsg.MACRO_LIBRARY},
                {FIELD: ErrorMsg.UNIQUE}
            ]
        }
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(400, response.status_code, response.json())
        self.assertDictEqual(error_response, response.json())
        # Test no macro name and no name
        del self.delete_body[NAME]
        del self.delete_body[MACRO_NAME]
        self.delete_body[FIELD_DATA] = [
            {FIELD: "WA0BBR"},
            {FIELD: " wa0bbr "},
            {FIELD: "EBW000"},
            {FIELD: "     "}
        ]
        error_response = {
            NAME: ErrorMsg.NOT_EMPTY,
            MACRO_NAME: ErrorMsg.NOT_EMPTY,
            FIELD_DATA: [
                {FIELD: ErrorMsg.MACRO_NOT_FOUND},
                {FIELD: ErrorMsg.UNIQUE},
                {FIELD: ErrorMsg.MACRO_NOT_FOUND},
                {FIELD: ErrorMsg.NOT_EMPTY},
            ]
        }
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(400, response.status_code, response.json())
        self.assertDictEqual(error_response, response.json())
        # Test invalid macro name and  invalid name
        self.delete_body[NAME] = "Invalid name"
        self.delete_body[MACRO_NAME] = "Invalid name"
        error_response = {
            NAME: ErrorMsg.NOT_FOUND,
            MACRO_NAME: ErrorMsg.MACRO_LIBRARY,
            FIELD_DATA: [
                {FIELD: f"{ErrorMsg.MACRO_SAME} INVALID NAME"},
                {FIELD: ErrorMsg.UNIQUE},
                {FIELD: f"{ErrorMsg.MACRO_SAME} INVALID NAME"},
                {FIELD: ErrorMsg.NOT_EMPTY},
            ]
        }
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(400, response.status_code, response.json())
        self.assertDictEqual(error_response, response.json())
        # Test different macro name
        self.delete_body[NAME] = f"  {TestAPI.NAME}  "
        self.delete_body[MACRO_NAME] = "EB0EB"
        error_response = {
            MACRO_NAME: ErrorMsg.NOT_FOUND,
            FIELD_DATA: [
                {FIELD: f"{ErrorMsg.MACRO_SAME} EB0EB"},
                {FIELD: ErrorMsg.UNIQUE},
                {FIELD: ErrorMsg.NOT_FOUND},
                {FIELD: ErrorMsg.NOT_EMPTY}
            ]
        }
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(400, response.status_code, response.json())
        self.assertDictEqual(error_response, response.json())
