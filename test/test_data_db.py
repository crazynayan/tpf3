from copy import deepcopy

from test import TestAPI


class Pnr(TestAPI):
    def setUp(self) -> None:
        self.test_data: dict = self.get_sample_test_data()
        self.pnr_updated: list = list()
        self.maxDiff = None

    def tearDown(self) -> None:
        for pnr_id in self.pnr_updated:
            self.delete(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}")

    def test_name_no_locator(self) -> None:
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr",
                              json={'key': 'name', 'data': 'some data'})
        self.assertEqual(200, response.status_code)
        self.pnr_updated.append(response.json()['id'])
        self.assertDictEqual({'id': response.json()['id'], 'key': 'name', 'data': 'some data', 'field_bytes': list(),
                              'locator': str()}, response.json())

    def test_fqtv_no_data_no_locator(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json={'key': 'fqtv'})
        self.assertEqual(200, response.status_code)
        self.pnr_updated.append(response.json()['id'])
        self.assertDictEqual({'id': response.json()['id'], 'key': 'fqtv', 'data': str(), 'field_bytes': list(),
                              'locator': str()}, response.json())

    def test_hfax_multiple_data_locator(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr",
                              json={'key': 'hfax', 'data': 'data1, data2, data3, data4', 'locator': 'GIVING'})
        self.assertEqual(200, response.status_code)
        self.pnr_updated.append(response.json()['id'])
        self.assertEqual({'id': response.json()['id'], 'key': 'hfax', 'data': 'data4', 'field_bytes': list(),
                          'locator': 'GIVING'}, response.json())
        response = self.get(f"/test_data/{self.test_data['id']}")
        expected_test_data = deepcopy(self.test_data)
        actual_test_data = response.json()
        pnr_dict = {'key': 'hfax', 'field_bytes': list(), 'locator': 'GIVING'}
        for index in range(1, 5):
            pnr_dict = deepcopy(pnr_dict)
            pnr_dict['id'] = actual_test_data['pnr'][index - 1]['id']
            pnr_dict['data'] = f"data{index}"
            expected_test_data['pnr'].append(pnr_dict)
        for index in range(0, 2):
            self.pnr_updated.append(actual_test_data['pnr'][index]['id'])
        self.assertDictEqual(expected_test_data, actual_test_data)
        response = self.delete(f"/test_data/{self.test_data['id']}/input/pnr/{actual_test_data['pnr'][2]['id']}")
        self.assertEqual(200, response.status_code)
        self.assertEqual({'id': response.json()['id'], 'key': 'hfax', 'data': 'data3', 'field_bytes': list(),
                          'locator': 'GIVING'}, response.json())
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        actual_test_data = response.json()
        self.assertEqual(3, len(actual_test_data['pnr']))

    def test_itin_field_bytes(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json={'key': 'itin', 'data': 'some data'})
        self.assertEqual(200, response.status_code)
        pnr_id = response.json()['id']
        self.pnr_updated.append(pnr_id)
        self.assertEqual({'id': pnr_id, 'key': 'itin', 'data': 'some data', 'field_bytes': list(),
                          'locator': str()}, response.json())
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WI0BS', 'field_bytes': {'WI0ARC': 'BA', 'WI0BRD': 'DFW'}})
        self.assertEqual(200, response.status_code)
        actual_pnr = response.json()
        self.assertEqual(2, len(actual_pnr['field_bytes']))
        expected_pnr = {'id': actual_pnr['id'], 'data': str(), 'locator': str(), 'key': 'itin', 'field_bytes': [
            {'field': 'WI0ARC', 'id': actual_pnr['field_bytes'][0]['id'], 'data': 'BA', 'length': 0},
            {'field': 'WI0BRD', 'id': actual_pnr['field_bytes'][1]['id'], 'data': 'DFW', 'length': 0}]}
        self.assertDictEqual(expected_pnr, actual_pnr)
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WI0BS', 'field_bytes': {'WI0ARC': 'AA'}})
        self.assertEqual(200, response.status_code)
        expected_pnr['field_bytes'][0]['data'] = 'AA'
        self.assertDictEqual(expected_pnr, response.json())
        expected_test_data = deepcopy(self.test_data)
        expected_test_data['pnr'].append(expected_pnr)
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertDictEqual(expected_test_data, response.json())
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json={'key': 'itin', 'data': 'ORD'})
        self.assertEqual(200, response.status_code)
        self.pnr_updated.append(response.json()['id'])
        self.assertNotEqual(expected_pnr['id'], response.json()['id'])

    def test_group_plan_field_bytes_update(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr",
                              json={'key': 'group_plan', 'locator': 'DGXEWR'})
        self.assertEqual(200, response.status_code)
        pnr_id = response.json()['id']
        self.pnr_updated.append(pnr_id)
        self.assertEqual({'id': pnr_id, 'key': 'group_plan', 'data': str(), 'field_bytes': list(),
                          'locator': 'DGXEWR'}, response.json())
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'TR1GAA',
                                    'field_bytes': {'TR1G_40_OCC': 'AA', 'TR1G_40_PRD_TYP': 'AIR'}})
        self.assertEqual(200, response.status_code)
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'TR1GAA',
                                    'field_bytes': {'TR1G_40_OCC': 'SU', 'TR1G_40_PRD_TYP': 'SUR',
                                                    'TR1G_40_LPRG': 'FF'}})
        self.assertEqual(200, response.status_code)
        actual_pnr = response.json()
        expected_test_data = deepcopy(self.test_data)
        pnr = {'id': pnr_id, 'data': str(), 'locator': 'DGXEWR', 'key': 'group_plan', 'field_bytes': [
            {'field': 'TR1G_40_OCC', 'id': actual_pnr['field_bytes'][0]['id'], 'data': 'SU', 'length': 0},
            {'field': 'TR1G_40_PRD_TYP', 'id': actual_pnr['field_bytes'][1]['id'], 'data': 'SUR', 'length': 0},
            {'field': 'TR1G_40_LPRG', 'id': actual_pnr['field_bytes'][2]['id'], 'data': 'FF', 'length': 0}]}
        expected_test_data['pnr'].append(pnr)
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertDictEqual(expected_test_data, response.json())

    def test_subs_card_seg_error_field_bytes(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr",
                              json={'key': 'subs_card_seg', 'data': 'data1', 'locator': str()})
        self.assertEqual(200, response.status_code)
        pnr_id = response.json()['id']
        self.pnr_updated.append(pnr_id)
        # Check duplicate data
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr",
                              json={'key': 'subs_card_seg', 'data': 'data1'})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({'message': 'Error in adding PNR element', 'error': 'Bad Request'}, response.json())
        # Check invalid pnr_id
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/invalid_id/fields",
                              json={'macro_name': 'WA0AA', 'field_bytes': {'WA0BBR': '01'}})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({'message': 'Error in adding PNR field', 'error': 'Bad Request'}, response.json())
        # Check invalid test_data_id for fields
        response = self.patch(f"/test_data/invalid_id/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WA0AA', 'field_bytes': {'WA0BBR': '01'}})
        self.assertEqual(404, response.status_code)
        # Check invalid_test_data_id for delete
        response = self.delete(f"/test_data/invalid_id/input/pnr/{pnr_id}")
        self.assertEqual(404, response.status_code)
        # Check no macro_name
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'field_bytes': {'WA0BBR': '01'}})
        self.assertEqual(400, response.status_code)
        # Check no field_bytes
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WA0AA'})
        self.assertEqual(400, response.status_code)
        # Check invalid macro name
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'INVALID', 'field_bytes': {'WA0BBR': '01'}})
        self.assertEqual(400, response.status_code)
        # Check field_bytes not dict
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WA0AA', 'field_bytes': ('WA0BBR', '01')})
        self.assertEqual(400, response.status_code)
        # Check field name not in macro
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WA0AA', 'field_bytes': {'WA0BBR': '01', 'EBW001': '02'}})
        self.assertEqual(400, response.status_code)
        # Check field value not str
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WA0AA', 'field_bytes': {'WA0BBR': '01', 'WA0ET2': 2}})
        self.assertEqual(400, response.status_code)
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WA0AA', 'field_bytes': {'WA0BBR': '01', 'WA0ET2': '02'}})
        self.assertEqual(200, response.status_code)

    def test_invalid_test_data_id(self):
        response = self.patch(f"/test_data/invalid_id/input/pnr", json={'key': 'name'})
        self.assertEqual(404, response.status_code)

    def test_invalid_pnr_id(self):
        response = self.delete(f"/test_data/{self.test_data['id']}/input/pnr/invalid_id", json={'key': 'name'})
        self.assertEqual(400, response.status_code)

    def test_no_key(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json={'locator': 'GIVING', 'data': 'd'})
        self.assertEqual(400, response.status_code)

    def test_invalid_key(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json={'key': 'invalid'})
        self.assertEqual(400, response.status_code)

    def test_locator_5_chars(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json={'key': 'name', 'locator': 'ABCDE'})
        self.assertEqual(400, response.status_code)

    def test_locator_7_chars(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr",
                              json={'key': 'name', 'locator': 'ABCDEFG'})
        self.assertEqual(400, response.status_code)

    def test_field_bytes_in_body(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr",
                              json={'key': 'name', 'field_bytes': 'WA0BBR'})
        self.assertEqual(400, response.status_code)
