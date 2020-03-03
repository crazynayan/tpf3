from base64 import b64encode

from test import TestAPI


class FileTestData(TestAPI):

    def setUp(self) -> None:
        self.test_data = self.get_test_data(' File', 'TS21')
        self.fixed_file = {'variation': 0, 'rec_id': 58321, 'macro_name': 'TJ0TJ', 'fixed_type': 94,
                           'fixed_ordinal': 383, 'forward_chain_count': 0, 'forward_chain_label': str(),
                           'field_data': list(), 'file_items': list(), 'variation_name': str()}
        self.pool_file = {'rec_id': 51688, 'macro_name': 'IY1IY', 'index_field': 'TJ0ATH',
                          'index_macro_name': 'TJ0TJ', 'forward_chain_count': 0, 'forward_chain_label': str(),
                          'field_data': list(), 'pool_files': list()}
        self.file_item = {'macro_name': 'IY1IY', 'field': 'IY1ATH', 'count_field': 'IY1CTR'}
        self.field_data = [{'field': 'IY9AON', 'data': b64encode(bytes([0x00, 0x00, 0x6F, 0x2F])).decode()},
                           {'field': 'IY9AGY', 'data': b64encode(bytes([0x00])).decode()}]
        self.file_item['field_data'] = self.field_data
        self.pool_file['file_items'] = [self.file_item]
        self.fixed_file['pool_files'] = [self.pool_file]
        self.test_data['fixed_files'].append(self.fixed_file)
        self.maxDiff = None

    def tearDown(self) -> None:
        self.delete(f"/test_data/{self.test_data['id']}")

    def test_file(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/fixed_files", json=self.fixed_file)
        self.assertEqual(200, response.status_code)
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        actual_test_data = response.json()
        self.fixed_file['id'] = actual_test_data['fixed_files'][0]['id']
        self.pool_file['id'] = actual_test_data['fixed_files'][0]['pool_files'][0]['id']
        self.file_item['id'] = actual_test_data['fixed_files'][0]['pool_files'][0]['file_items'][0]['id']
        self.assertEqual(self.test_data, actual_test_data)
        # Test delete
        response = self.delete(f"/test_data/{self.test_data['id']}/input/fixed_files/{self.fixed_file['id']}")
        self.assertEqual(200, response.status_code)
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        self.test_data['fixed_files'] = list()
        self.assertEqual(self.test_data, response.json())

    def test_run(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/fixed_files", json=self.fixed_file)
        self.assertEqual(200, response.status_code)
        self.fixed_file['variation'] = 1
        self.field_data[1]['data'] = b64encode(bytes([0x10])).decode()
        response = self.patch(f"/test_data/{self.test_data['id']}/input/fixed_files", json=self.fixed_file)
        self.assertEqual(200, response.status_code)
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr",
                              json={'variation': 0, 'key': 'group_plan', 'locator': str(),
                                    'data': 'BTS-B4T0/108/11-FINANCIAL SERVICES'})
        self.assertEqual(200, response.status_code)
        response = self.patch(f"/test_data/{self.test_data['id']}/input/cores/WA0AA/fields",
                              json={'variation': 0, 'field': 'WA0POR',
                                    'data': b64encode(bytes([0x00, 0x6F, 0x2F])).decode()})
        self.assertEqual(200, response.status_code)
        response = self.patch(f"/test_data/{self.test_data['id']}/input/cores/WA0AA/fields",
                              json={'variation': 0, 'field': 'WA0FNS', 'data': b64encode(bytes([0x10])).decode()})
        self.assertEqual(200, response.status_code)
        response = self.patch(f"/test_data/{self.test_data['id']}/output/regs", json={'regs': ['R6']})
        self.assertEqual(200, response.status_code)
        response = self.get(f"/test_data/{self.test_data['id']}/run")
        self.assertEqual(200, response.status_code)
        outputs = response.json()['outputs']
        self.assertEqual(8, outputs[0]['regs']['R6'])
        self.assertEqual(0, outputs[1]['regs']['R6'])
        self.assertEqual('$$ETK4$$.1', outputs[0]['last_line'])
        self.assertEqual('TS21EXIT.1', outputs[1]['last_line'])

    def test_rec_id_not_int(self):
        self.fixed_file['rec_id'] = 'TJ'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/fixed_files", json=self.fixed_file)
        self.assertEqual(400, response.status_code)

    def test_variation_too_high(self):
        self.fixed_file['variation'] = 2
        response = self.patch(f"/test_data/{self.test_data['id']}/input/fixed_files", json=self.fixed_file)
        self.assertEqual(400, response.status_code)
