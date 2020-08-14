from test import TestAPI
from test.test_api.constants import ACTION, Action, NAME, NEW_NAME, SEG_NAME


class RenameCopy(TestAPI):

    def setUp(self):
        self.cleanup = False
        self.cleanup_new = False
        self.new_name = f"{TestAPI.NAME} - New"
        self.create_body = {
            ACTION: Action.CREATE,
            NAME: TestAPI.NAME,
            SEG_NAME: TestAPI.SEG_NAME
        }
        self.rename_body = {
            ACTION: Action.RENAME,
            NAME: TestAPI.NAME,
            NEW_NAME: self.new_name
        }

    def tearDown(self):
        if self.cleanup:
            self.delete(f"/api/test_data", params={NAME: TestAPI.NAME})
        if self.cleanup_new:
            self.delete(f"/api/test_data", params={NAME: self.new_name})

    def test_rename(self):
        self.cleanup = True
        response = self.post("/api/test_data", json=self.create_body)
        create_id = response.json()["id"]
        self.cleanup_new = True
        response = self.post("/api/test_data", json=self.rename_body)
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertEqual(self.new_name, response_body[NAME])
        self.assertEqual(create_id, response_body["id"])
        self.assertEqual(4, len(response_body))
