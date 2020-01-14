from base64 import b64encode
from copy import deepcopy
from typing import Union, Dict

from test import TestAPI


class Pnr(TestAPI):
    def setUp(self) -> None:
        self.test_data: dict = self.get_sample_test_data()
        self.pnr_updated: list = list()
        self.maxDiff = None
        self.default_pnr: Dict[str, Union[str, int, list]] = {
            'key': 'name', 'locator': str(), 'variation': 0, 'data': str()}

    def tearDown(self) -> None:
        for pnr_id in self.pnr_updated:
            self.delete(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}")

    def test_name_no_locator(self) -> None:
        self.default_pnr['key'] = 'name'
        self.default_pnr['data'] = 'some data'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.assertEqual(200, response.status_code)
        self.default_pnr['id'] = response.json()['id']
        self.default_pnr['field_data'] = list()
        self.pnr_updated.append(self.default_pnr['id'])
        self.assertDictEqual(self.default_pnr, response.json())

    def test_fqtv_no_data_no_locator(self):
        self.default_pnr['key'] = 'fqtv'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.assertEqual(200, response.status_code)
        self.default_pnr['id'] = response.json()['id']
        self.default_pnr['field_data'] = list()
        self.pnr_updated.append(self.default_pnr['id'])
        self.assertDictEqual(self.default_pnr, response.json())

    def test_hfax_multiple_data_locator(self):
        self.default_pnr['key'] = 'hfax'
        self.default_pnr['data'] = 'data1, data2, data3, data4'
        self.default_pnr['locator'] = 'GIVING'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.assertEqual(200, response.status_code)
        self.default_pnr['id'] = response.json()['id']
        self.pnr_updated.append(self.default_pnr['id'])
        self.default_pnr['data'] = 'data4'
        self.default_pnr['field_data'] = list()
        self.assertDictEqual(self.default_pnr, response.json())
        response = self.get(f"/test_data/{self.test_data['id']}")
        expected_test_data = deepcopy(self.test_data)
        actual_test_data = response.json()
        for index in range(1, 5):
            pnr_dict = self.default_pnr.copy()
            pnr_dict['id'] = actual_test_data['pnr'][index - 1]['id']
            pnr_dict['data'] = f"data{index}"
            expected_test_data['pnr'].append(pnr_dict)
        for index in range(0, 2):
            self.pnr_updated.append(actual_test_data['pnr'][index]['id'])
        self.assertDictEqual(expected_test_data, actual_test_data)
        response = self.delete(f"/test_data/{self.test_data['id']}/input/pnr/{actual_test_data['pnr'][2]['id']}")
        self.assertEqual(200, response.status_code)
        self.default_pnr['data'] = 'data3'
        self.default_pnr['id'] = response.json()['id']
        self.assertEqual(self.default_pnr, response.json())
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        actual_test_data = response.json()
        self.assertEqual(3, len(actual_test_data['pnr']))

    def test_itin_field_data(self):
        self.default_pnr['key'] = 'itin'
        self.default_pnr['data'] = 'some data'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.assertEqual(200, response.status_code)
        pnr_id = response.json()['id']
        self.pnr_updated.append(pnr_id)
        self.default_pnr['id'] = pnr_id
        self.default_pnr['field_data'] = list()
        self.assertEqual(self.default_pnr, response.json())
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WI0BS', 'field_data': {'WI0ARC': 'BA', 'WI0BRD': 'DFW'}})
        self.assertEqual(200, response.status_code)
        actual_pnr = response.json()
        self.assertEqual(2, len(actual_pnr['field_data']))
        expected_pnr = self.default_pnr.copy()
        expected_pnr['id'] = actual_pnr['id']
        expected_pnr['data'] = str()
        expected_pnr['field_data'] = [{'field': 'WI0ARC', 'data': 'BA'}, {'field': 'WI0BRD', 'data': 'DFW'}]
        self.assertDictEqual(expected_pnr, actual_pnr)
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WI0BS', 'field_data': {'WI0ARC': 'AA'}})
        self.assertEqual(200, response.status_code)
        expected_pnr['field_data'][0]['data'] = 'AA'
        self.assertDictEqual(expected_pnr, response.json())
        expected_test_data = deepcopy(self.test_data)
        expected_test_data['pnr'].append(expected_pnr)
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertDictEqual(expected_test_data, response.json())
        self.default_pnr['data'] = 'ORD'
        del self.default_pnr['id']
        del self.default_pnr['field_data']
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.assertEqual(200, response.status_code)
        self.pnr_updated.append(response.json()['id'])
        self.assertNotEqual(expected_pnr['id'], response.json()['id'])

    def test_group_plan_field_data_update(self):
        self.default_pnr['key'] = 'group_plan'
        self.default_pnr['locator'] = 'DGXEWR'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.assertEqual(200, response.status_code)
        pnr_id = response.json()['id']
        self.pnr_updated.append(pnr_id)
        self.default_pnr['id'] = pnr_id
        self.default_pnr['field_data'] = list()
        self.assertEqual(self.default_pnr, response.json())
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'TR1GAA',
                                    'field_data': {'TR1G_40_OCC': 'AA', 'TR1G_40_PRD_TYP': 'AIR'}})
        self.assertEqual(200, response.status_code)
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'TR1GAA',
                                    'field_data': {'TR1G_40_OCC': 'SU', 'TR1G_40_PRD_TYP': 'SUR',
                                                   'TR1G_40_LPRG': 'FF'}})
        self.assertEqual(200, response.status_code)
        expected_test_data = deepcopy(self.test_data)
        pnr = self.default_pnr.copy()
        pnr['field_data'] = [{'field': 'TR1G_40_OCC', 'data': 'SU'}, {'field': 'TR1G_40_PRD_TYP', 'data': 'SUR'},
                             {'field': 'TR1G_40_LPRG', 'data': 'FF'}]
        expected_test_data['pnr'].append(pnr)
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertDictEqual(expected_test_data, response.json())

    def test_subs_card_seg_error_field_data(self):
        self.default_pnr['key'] = 'subs_card_seg'
        self.default_pnr['data'] = 'data1'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.assertEqual(200, response.status_code)
        pnr_id = response.json()['id']
        self.pnr_updated.append(pnr_id)
        # Check duplicate data
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.assertEqual(200, response.status_code)
        self.pnr_updated.append(response.json()['id'])
        # Check invalid pnr_id
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/invalid_id/fields",
                              json={'macro_name': 'WA0AA', 'field_data': {'WA0BBR': '01'}})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({'message': 'Error in adding PNR field', 'error': 'Bad Request'}, response.json())
        # Check invalid test_data_id for fields
        response = self.patch(f"/test_data/invalid_id/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WA0AA', 'field_data': {'WA0BBR': '01'}})
        self.assertEqual(404, response.status_code)
        # Check invalid_test_data_id for delete
        response = self.delete(f"/test_data/invalid_id/input/pnr/{pnr_id}")
        self.assertEqual(404, response.status_code)
        # Check no macro_name
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'field_data': {'WA0BBR': '01'}})
        self.assertEqual(400, response.status_code)
        # Check no field_data
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WA0AA'})
        self.assertEqual(400, response.status_code)
        # Check invalid macro name
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'INVALID', 'field_data': {'WA0BBR': '01'}})
        self.assertEqual(400, response.status_code)
        # Check field_data not dict
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WA0AA', 'field_data': ('WA0BBR', '01')})
        self.assertEqual(400, response.status_code)
        # Check field name not in macro
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WA0AA', 'field_data': {'WA0BBR': '01', 'EBW001': '02'}})
        self.assertEqual(400, response.status_code)
        # Check field value not str
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WA0AA', 'field_data': {'WA0BBR': '01', 'WA0ET2': 2}})
        self.assertEqual(400, response.status_code)
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr/{pnr_id}/fields",
                              json={'macro_name': 'WA0AA', 'field_data': {'WA0BBR': '01', 'WA0ET2': '02'}})
        self.assertEqual(200, response.status_code)

    def test_invalid_test_data_id(self):
        response = self.patch(f"/test_data/invalid_id/input/pnr", json=self.default_pnr)
        self.assertEqual(404, response.status_code)

    def test_invalid_pnr_id(self):
        response = self.delete(f"/test_data/{self.test_data['id']}/input/pnr/invalid_id", json=self.default_pnr)
        self.assertEqual(400, response.status_code)

    def test_no_key(self):
        del self.default_pnr['key']
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.assertEqual(400, response.status_code)

    def test_invalid_key(self):
        self.default_pnr['key'] = 'invalid'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.assertEqual(400, response.status_code)

    def test_locator_5_chars(self):
        self.default_pnr['locator'] = 'ABCDE'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.assertEqual(400, response.status_code)

    def test_locator_7_chars(self):
        self.default_pnr['locator'] = 'ABCDEFG'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.assertEqual(400, response.status_code)

    def test_field_data_in_body(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/pnr",
                              json={'key': 'name', 'field_data': 'WA0BBR'})
        self.assertEqual(400, response.status_code)


class Tpfdf(TestAPI):
    def setUp(self) -> None:
        self.test_data: dict = self.get_sample_test_data()
        self.df_updated: list = list()
        self.maxDiff = None
        self.lrec: Dict[str, Union[str, int, dict, list]] = {
            'key': '40', 'variation': 0, 'macro_name': 'TR1GAA',
            'field_data': {
                'TR1G_40_OCC': b64encode(bytes([0xC1, 0xC1])).decode(),
                'TR1G_40_ACSTIERCODE': b64encode(bytes([0xC7, 0xD3, 0xC4])).decode(),
                'TR1G_40_TIER_EFFD': b64encode(bytes([0x47, 0xD3])).decode(),
                'TR1G_40_TIER_DISD': b64encode(bytes([0x7F, 0xFF])).decode(),
                'TR1G_40_PTI': b64encode(bytes([0x80])).decode(),
            }}

    def tearDown(self) -> None:
        for df_id in self.df_updated:
            self.delete(f"/test_data/{self.test_data['id']}/input/tpfdf/{df_id}")

    def test_lrec_add_delete(self) -> None:
        lrec = deepcopy(self.lrec)
        response = self.patch(f"/test_data/{self.test_data['id']}/input/tpfdf", json=lrec)
        self.assertEqual(200, response.status_code)
        lrec['id'] = response.json()['id']
        lrec['field_data'] = [{'field': field, 'data': value} for field, value in lrec['field_data'].items()]
        self.df_updated.append(lrec['id'])
        self.assertEqual(lrec, response.json())
        # Test duplicate add fail
        response = self.patch(f"/test_data/{self.test_data['id']}/input/tpfdf", json=self.lrec)
        self.assertEqual(400, response.status_code)
        # Retrieve the entire test data and check
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        expected_test_data = deepcopy(self.test_data)
        expected_test_data['tpfdf'].append(lrec)
        self.assertEqual(expected_test_data, response.json())
        # Test delete with invalid test data id
        response = self.delete(f"/test_data/invalid_id/input/tpfdf/{lrec['id']}", json=self.lrec)
        self.assertEqual(404, response.status_code)
        # Delete lrec
        response = self.delete(f"/test_data/{self.test_data['id']}/input/tpfdf/{lrec['id']}")
        self.assertEqual(200, response.status_code)
        self.df_updated.remove(lrec['id'])
        self.assertEqual(lrec, response.json())
        # Check if lrec is deleted
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        expected_test_data = deepcopy(self.test_data)
        self.assertEqual(expected_test_data, response.json())
        # Test delete again (Invalid lrec_id)
        response = self.delete(f"/test_data/{self.test_data['id']}/input/tpfdf/{lrec['id']}")
        self.assertEqual(400, response.status_code)

    def test_empty_body(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/tpfdf", json={})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({'message': 'Error in adding Tpfdf lrec', 'error': 'Bad Request'}, response.json())

    def test_invalid_test_data_id(self):
        response = self.patch(f"/test_data/invalid_id/input/tpfdf", json=self.lrec)
        self.assertEqual(404, response.status_code)

    def test_no_variation(self):
        del self.lrec['variation']
        response = self.patch(f"/test_data/{self.test_data['id']}/input/tpfdf", json=self.lrec)
        self.assertEqual(400, response.status_code)

    def test_key_not_str(self):
        self.lrec['key'] = 0x40
        response = self.patch(f"/test_data/{self.test_data['id']}/input/tpfdf", json=self.lrec)
        self.assertEqual(400, response.status_code)

    def test_key_1_character(self):
        self.lrec['key'] = '4'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/tpfdf", json=self.lrec)
        self.assertEqual(400, response.status_code)

    def test_key_invalid_character(self):
        self.lrec['key'] = '4*'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/tpfdf", json=self.lrec)
        self.assertEqual(400, response.status_code)

    def test_extra_fields(self):
        self.lrec['field_bytes'] = 'field'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/tpfdf", json=self.lrec)
        self.assertEqual(400, response.status_code)

    def test_invalid_macro(self):
        self.lrec['macro_name'] = 'INVALID_MACRO'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/tpfdf", json=self.lrec)
        self.assertEqual(400, response.status_code)

    def test_field_data_list(self):
        self.lrec['field_data'] = [{'field': field, 'data': value} for field, value in self.lrec['field_data'].items()]
        response = self.patch(f"/test_data/{self.test_data['id']}/input/tpfdf", json=self.lrec)
        self.assertEqual(400, response.status_code)

    def test_empty_field_data(self):
        self.lrec['field_data'] = dict()
        response = self.patch(f"/test_data/{self.test_data['id']}/input/tpfdf", json=self.lrec)
        self.assertEqual(400, response.status_code)

    def test_variation_not_int(self):
        self.lrec['variation'] = '0'
        response = self.patch(f"/test_data/{self.test_data['id']}/input/tpfdf", json=self.lrec)
        self.assertEqual(400, response.status_code)

    def test_field_not_in_macro(self):
        self.lrec['field_data']['EBW000'] = b64encode(bytes([0x80])).decode()
        response = self.patch(f"/test_data/{self.test_data['id']}/input/tpfdf", json=self.lrec)
        self.assertEqual(400, response.status_code)

    def test_data_not_str(self):
        self.lrec['field_data']['TR1G_40_PTI'] = 0x80
        response = self.patch(f"/test_data/{self.test_data['id']}/input/tpfdf", json=self.lrec)
        self.assertEqual(400, response.status_code)
