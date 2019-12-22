from test import TestAPI


class CreateTestData(TestAPI):

    def test_default_created(self) -> None:
        response = self.get(f"/test_data/{self.TEST_DATA['id']}")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(self.TEST_DATA, response.json())

    def test_empty(self) -> None:
        response = self.post(f"/test_data", json=dict())
        self.assertEqual(400, response.status_code)

    def test_duplicate_name(self) -> None:
        response = self.post(f"/test_data", json={'name': 'ETA5 Testing 123', 'seg_name': 'ETA5'})
        self.assertEqual(400, response.status_code)

    def test_3_items_in_body(self) -> None:
        response = self.post(f"/test_data", json={'name': 'ETA5 Testing 1234', 'seg_name': 'ETA5', 'id': 1})
        self.assertEqual(400, response.status_code)

    def test_with_only_name(self) -> None:
        response = self.post(f"/test_data", json={'name': 'ETA5 Testing 1234'})
        self.assertEqual(400, response.status_code)

    def test_with_invalid_seg(self) -> None:
        response = self.post(f"/test_data", json={'name': 'ETA5 Testing 1234', 'seg_name': 'no seg'})
        self.assertEqual(400, response.status_code)

    def test_with_no_name(self) -> None:
        response = self.post(f"/test_data", json={'name': '', 'seg_name': 'ETA5'})
        self.assertEqual(400, response.status_code)

    def test_with_no_seg_name(self) -> None:
        response = self.post(f"/test_data", json={'name': 'ETA5 Testing 1234', 'seg_name': ''})
        self.assertEqual(400, response.status_code)
