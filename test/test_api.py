from test import TestAPI


class TestData(TestAPI):

    def test_create_test_data(self) -> None:
        response = self.get(f"/test_data/{self.test_data_dict['id']}")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(self.test_data_dict, response.json())
        response = self.post(f"/test_data", json=dict())
        self.assertEqual(400, response.status_code)
        response = self.post(f"/test_data", json={'name': 'ETA5 Testing 123', 'seg_name': 'ETA5'})
        self.assertEqual(400, response.status_code)
        response = self.post(f"/test_data", json={'name': 'ETA5 Testing 1234', 'seg_name': 'ETA5', 'id': 1})
        self.assertEqual(400, response.status_code)
        response = self.post(f"/test_data", json={'name': 'ETA5 Testing 1234'})
        self.assertEqual(400, response.status_code)
        response = self.post(f"/test_data", json={'name': 'ETA5 Testing 1234', 'seg_name': 'no seg'})
        self.assertEqual(400, response.status_code)
        response = self.post(f"/test_data", json={'name': '', 'seg_name': 'ETA5'})
        self.assertEqual(400, response.status_code)
        response = self.post(f"/test_data", json={'name': 'ETA5 Testing 1234', 'seg_name': ''})
        self.assertEqual(400, response.status_code)
