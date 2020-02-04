from test import TestAPI


class CreateTestData(TestAPI):

    def test_default_created(self) -> None:
        test_data = self.get_sample_test_data()
        response = self.get(f"/test_data/{test_data['id']}")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(test_data, response.json())

    def test_empty(self) -> None:
        response = self.post(f"/test_data", json=dict())
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({'message': 'Invalid format of test data. Need unique name and seg_name only.',
                              'error': 'Bad Request'}, response.json())

    def test_duplicate_name(self) -> None:
        response = self.post(f"/test_data", json={'name': self.NAME, 'seg_name': self.SEG_NAME})
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
        response = self.post(f"/test_data", json={'name': '', 'seg_name': self.SEG_NAME})
        self.assertEqual(400, response.status_code)

    def test_with_no_seg_name(self) -> None:
        response = self.post(f"/test_data", json={'name': 'ETA5 Testing 1234', 'seg_name': ''})
        self.assertEqual(400, response.status_code)


class DeleteTestData(TestAPI):

    def test_delete(self):
        test_data = self.get_test_data('- Delete')
        response = self.delete(f"/test_data/{test_data['id']}")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual({'test_data_id': test_data['id']}, response.json())
        response = self.get(f"/test_data/{test_data['id']}")
        self.assertEqual(404, response.status_code)
        self.assertDictEqual({'error': 'Not Found', 'message': 'Test data id not found'}, response.json())

    def test_invalid_id(self):
        response = self.delete(f"/test_data/invalid_id")
        self.assertEqual(404, response.status_code)

    def test_empty_id(self):
        response = self.delete(f"/test_data/")
        self.assertEqual(404, response.status_code)


class GetAllTestData(TestAPI):

    def setUp(self):
        test_data = self.get_sample_test_data()
        self.test_data_header = {'id': test_data['id'], 'name': test_data['name'], 'seg_name': test_data['seg_name']}

    def test_get_all(self):
        response = self.get(f"/test_data")
        self.assertEqual(200, response.status_code)
        self.assertIn(self.test_data_header, response.json())

    def test_get_by_name(self):
        response = self.get(f"/test_data", params={'name': 'NZ99 - ETA5 - Testing 123'})
        self.assertEqual(200, response.status_code)
        self.assertIn(self.test_data_header, response.json())
        self.assertEqual(1, len(response.json()))

    def test_name_not_found(self):
        response = self.get(f"/test_data", params={'name': 'Invalid-Name'})
        self.assertEqual(404, response.status_code)
        self.assertDictEqual({'error': 'Not Found', 'message': 'No test data found by this name'}, response.json())

    def test_empty_name(self):
        response = self.get(f"/test_data", params={'name': ''})
        self.assertEqual(404, response.status_code)

    def test_other_parameters(self):
        response = self.get(f"/test_data", params={'invalid_params': 'invalid_data'})
        self.assertEqual(200, response.status_code)
        self.assertIn(self.test_data_header, response.json())


class RenameTestData(TestAPI):

    def setUp(self) -> None:
        self.test_data = self.get_test_data(' - Rename')

    def tearDown(self) -> None:
        self.delete_test_data(self.test_data['id'])

    def test_rename_both(self):
        renamed_test_data = {'name': 'ETA2 - New Name', 'seg_name': 'ETA2'}
        response = self.patch(f"/test_data/{self.test_data['id']}/rename", json=renamed_test_data)
        renamed_test_data['id'] = self.test_data['id']
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(renamed_test_data, response.json())
        response = self.get(f"/test_data", params={'name': self.test_data['name']})
        self.assertEqual(404, response.status_code)
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        self.assertEqual(renamed_test_data['name'], response.json()['name'])
        self.assertEqual(renamed_test_data['seg_name'], response.json()['seg_name'])

    def test_rename_seg(self):
        renamed_test_data = {'name': self.test_data['name'], 'seg_name': 'ETA2'}
        response = self.patch(f"/test_data/{self.test_data['id']}/rename", json=renamed_test_data)
        self.test_data['seg_name'] = 'ETA2'
        renamed_test_data['id'] = self.test_data['id']
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(renamed_test_data, response.json())
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(self.test_data, response.json())


class RenameErrorTestData(TestAPI):

    def setUp(self) -> None:
        self.test_data_id = self.get_sample_test_data()['id']

    def test_invalid_id(self):
        response = self.patch(f"/test_data/invalid_id/rename")
        self.assertEqual(404, response.status_code)

    def test_empty(self) -> None:
        response = self.patch(f"/test_data/{self.test_data_id}/rename", json=dict())
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({'message': 'Error in renaming test data', 'error': 'Bad Request'}, response.json())

    def test_3_items_in_body(self) -> None:
        response = self.patch(f"/test_data/{self.test_data_id}/rename",
                              json={'name': 'ETA5 Testing 1234', 'seg_name': 'ETA5', 'id': 1})
        self.assertEqual(400, response.status_code)

    def test_with_only_name(self) -> None:
        response = self.patch(f"/test_data/{self.test_data_id}/rename", json={'name': 'ETA5 Testing 1234'})
        self.assertEqual(400, response.status_code)

    def test_with_only_seg_name(self) -> None:
        response = self.patch(f"/test_data/{self.test_data_id}/rename", json={'seg_name': 'ETA5'})
        self.assertEqual(400, response.status_code)

    def test_with_invalid_seg(self) -> None:
        response = self.patch(f"/test_data/{self.test_data_id}/rename", json={'name': 'ETA5 Testing 1234',
                                                                              'seg_name': 'no seg'})
        self.assertEqual(400, response.status_code)

    def test_with_no_name(self) -> None:
        response = self.patch(f"/test_data/{self.test_data_id}/rename", json={'name': '', 'seg_name': 'ETA5'})
        self.assertEqual(400, response.status_code)

    def test_with_no_seg_name(self) -> None:
        response = self.patch(f"/test_data/{self.test_data_id}/rename", json={'name': 'ETA5 Testing 1234',
                                                                              'seg_name': ''})
        self.assertEqual(400, response.status_code)


class CopyTestData(TestAPI):

    def setUp(self) -> None:
        self.test_data = self.get_sample_test_data()
        self.copy_test_data_id = str()

    def tearDown(self) -> None:
        if self.copy_test_data_id:
            self.delete_test_data(self.copy_test_data_id)

    def test_copy(self):
        response = self.post(f"/test_data/{self.test_data['id']}/copy")
        self.assertEqual(200, response.status_code)
        self.copy_test_data_id = response.json()['id']
        response = self.get(f"/test_data/{self.copy_test_data_id}")
        self.assertEqual(200, response.status_code)
        copy_test_data = response.json()
        self.assertNotEqual(copy_test_data['name'], self.test_data['name'])
        self.assertNotEqual(copy_test_data['id'], self.test_data['id'])
        self.assertEqual(copy_test_data['seg_name'], self.test_data['seg_name'])
        self.assertDictEqual(copy_test_data['outputs'][0]['regs'], self.test_data['outputs'][0]['regs'])
        self.assertNotEqual(copy_test_data['outputs'][0]['id'], self.test_data['outputs'][0]['id'])
        # Cannot copy a copied test data. You need to rename it first
        response = self.post(f"/test_data/{self.copy_test_data_id}/copy")
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({'message': 'Error in copying test data', 'error': 'Bad Request'}, response.json())
        # Cannot copy a test data multiple times. You need to rename the copied test data first
        response = self.post(f"/test_data/{self.test_data['id']}/copy")
        self.assertEqual(400, response.status_code)

    def test_invalid_id(self):
        response = self.post(f"/test_data/invalid_id/copy")
        self.assertEqual(404, response.status_code)
