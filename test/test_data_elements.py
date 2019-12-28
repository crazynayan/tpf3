from copy import deepcopy
from typing import List, Tuple

from requests.utils import quote

from config import config
from test import TestAPI


class OutputRegisters(TestAPI):

    def setUp(self) -> None:
        self.test_data: dict = self.get_sample_test_data()
        self.reg_updated: bool = False

    def tearDown(self) -> None:
        if self.reg_updated:
            self.patch(f"/test_data/{self.test_data['id']}/output/regs", json={'regs': []})

    def test_empty(self):
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(dict(), response.json()['outputs'][0]['regs'])

    def test_few_reg(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/regs", json={'regs': ['R1', 'R3']})
        self.assertEqual(200, response.status_code)
        self.reg_updated = True
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual({'R1': 0, 'R3': 0}, response.json()['outputs'][0]['regs'])

    def test_all_reg(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/regs", json={'regs': list(config.REGISTERS)})
        self.assertEqual(200, response.status_code)
        self.reg_updated = True
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual({reg: 0 for reg in config.REGISTERS}, response.json()['outputs'][0]['regs'])

    def test_invalid_id(self):
        response = self.patch(f"/test_data/invalid_id/output/regs", json={'regs': list(config.REGISTERS)})
        self.assertEqual(404, response.status_code)

    def test_invalid_key(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/regs", json={'invalid': ['R1']})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({'message': 'Invalid format of Registers', 'error': 'Bad Request'}, response.json())

    def test_invalid_reg(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/regs", json={'regs': ['R1', 'R16']})
        self.assertEqual(400, response.status_code)

    def test_reg_tuple(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/regs", json={'regs': ('R1', 'R15')})
        self.assertEqual(200, response.status_code)
        self.reg_updated = True
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual({'R1': 0, 'R15': 0}, response.json()['outputs'][0]['regs'])


class OutputFields(TestAPI):

    def setUp(self) -> None:
        self.test_data: dict = self.get_sample_test_data()
        self.macro_fields: List[Tuple[str, str]] = list()
        self.maxDiff = None

    def tearDown(self) -> None:
        for macro_name, field_name in self.macro_fields:
            self.delete(f"/test_data/{self.test_data['id']}/output/cores/{macro_name}/fields/{quote(field_name)}")

    def _check_field_byte(self, macro_name: str, field_name: str, length: int, input_len: int = None,
                          input_base_reg: str = None) -> dict:
        body: dict = {'field': f"{field_name}"}
        if input_len is not None:
            body['length'] = length
        if input_base_reg is not None:
            body['base_reg'] = input_base_reg
        response = self.patch(f"/test_data/{self.test_data['id']}/output/cores/{macro_name}/fields", json=body)
        self.assertEqual(200, response.status_code)
        self.macro_fields.append((macro_name, field_name))
        body['data'] = str()
        body['id'] = response.json()['id']
        body['length'] = length
        body.pop('base_reg', None)
        self.assertDictEqual(body, response.json())
        return body

    def _check_core(self, macro_name: str, field_bytes: List[dict], base_reg: str = None):
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        actual_test_data = response.json()
        expected_test_data = deepcopy(self.test_data)
        core_id = actual_test_data['outputs'][0]['cores'][0]['id']
        base_reg = base_reg if base_reg else str()
        core = {'id': core_id, 'base_reg': base_reg, 'field_bytes': list(), 'macro_name': macro_name}
        expected_test_data['outputs'][0]['cores'].append(core)
        expected_test_data['outputs'][0]['cores'][0]['field_bytes'].extend(field_bytes)
        self.assertDictEqual(expected_test_data, actual_test_data)

    def test_default_field_no_length(self) -> None:
        field_byte1 = self._check_field_byte('WA0AA', 'WA0BBR', 2)
        field_byte2 = self._check_field_byte('WA0AA', '#WA0TTY', 2, input_len=0, input_base_reg='R0')
        self._check_core('WA0AA', [field_byte1, field_byte2])

    def test_default_field_with_length_change_it(self) -> None:
        self._check_field_byte('EB0EB', 'EBW000', 10, input_len=10)
        field_byte = self._check_field_byte('EB0EB', 'EBW000', 6, input_len=6)
        self._check_core('EB0EB', [field_byte])

    def test_based_field_delete(self) -> None:
        field_byte1 = self._check_field_byte('UI2PF', 'UI2CNN', 1, input_base_reg='R7')
        field_byte2 = self._check_field_byte('UI2PF', 'UI2INC', 3, input_len=3, input_base_reg='R6')
        self._check_core('UI2PF', [field_byte1, field_byte2], base_reg='R6')
        # Delete 1st field
        response = self.delete(f"/test_data/{self.test_data['id']}/output/cores/UI2PF/fields/UI2CNN")
        self.assertEqual(200, response.status_code)
        del self.macro_fields[0]
        self.assertDictEqual(field_byte1, response.json())
        self._check_core('UI2PF', [field_byte2], base_reg='R6')
        # Deleting the 1st field again will give an error
        response = self.delete(f"/test_data/{self.test_data['id']}/output/cores/UI2PF/fields/UI2CNN")
        self.assertEqual(400, response.status_code)
        # Delete 2nd field
        response = self.delete(f"/test_data/{self.test_data['id']}/output/cores/UI2PF/fields/UI2INC")
        self.assertEqual(200, response.status_code)
        del self.macro_fields[0]
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        self.assertEqual(list(), response.json()['outputs'][0]['cores'])

    def test_invalid_id(self):
        response = self.patch(f"/test_data/invalid_id/output/cores/WA0AA/fields", json={'field': 'WA0BBR'})
        self.assertEqual(404, response.status_code)

    def test_no_field(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/cores/WA0AA/fields", json={})
        self.assertEqual(400, response.status_code)

    def test_empty_field(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/cores/WA0AA/fields", json={'field': str()})
        self.assertEqual(400, response.status_code)

    def test_invalid_macro(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/cores/INVALID_MACRO/fields",
                              json={'field': 'WA0BBR'})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({'message': 'Error in adding field', 'error': 'Bad Request'}, response.json())

    def test_invalid_length(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/cores/WA0AA/fields",
                              json={'field': 'WA0BBR', 'length': 'invalid_type'})
        self.assertEqual(400, response.status_code)

    def test_invalid_data(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/cores/WA0AA/fields",
                              json={'field': 'WA0BBR', 'data': 123})
        self.assertEqual(400, response.status_code)

    def test_field_not_in_macro(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/cores/WA0AA/fields", json={'field': 'EBW000'})
        self.assertEqual(400, response.status_code)
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(self.test_data, response.json())

    def test_data_in_body(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/cores/WA0AA/fields",
                              json={'field': 'WA0BBR', 'data': 'some_data'})
        self.assertEqual(400, response.status_code)

    def test_base_reg_for_default_macros(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/cores/WA0AA/fields",
                              json={'field': 'WA0BBR', 'base_reg': 'R1'})
        self.assertEqual(400, response.status_code)

    def test_no_base_reg_for_non_default_macros(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/cores/UI2PF/fields",
                              json={'field': 'UI2CNN'})
        self.assertEqual(400, response.status_code)

    def test_base_reg_R0_for_non_default_macros(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/cores/UI2PF/fields",
                              json={'field': 'UI2CNN', 'base_reg': 'R0'})
        self.assertEqual(400, response.status_code)

    def test_invalid_base_reg_number(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/cores/UI2PF/fields",
                              json={'field': 'UI2CNN', 'base_reg': 12})
        self.assertEqual(400, response.status_code)

    def test_invalid_base_reg(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/output/cores/UI2PF/fields",
                              json={'field': 'UI2CNN', 'base_reg': 'R16'})
        self.assertEqual(400, response.status_code)

    def test_delete_invalid_id(self):
        response = self.delete(f"/test_data/invalid_id/output/cores/WA0AA/fields/WA0BBR")
        self.assertEqual(404, response.status_code)

    def test_delete_macro_name_not_in_core(self):
        response = self.delete(f"/test_data/{self.test_data['id']}/output/cores/WA0AA/fields/WA0BBR")
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({'message': 'Error in deleting field', 'error': 'Bad Request'}, response.json())


class InputFields(TestAPI):

    def setUp(self) -> None:
        self.test_data: dict = self.get_sample_test_data()
        self.macro_fields: List[Tuple[str, str]] = list()
        self.maxDiff = None

    def tearDown(self) -> None:
        for macro_name, field_name in self.macro_fields:
            self.delete(f"/test_data/{self.test_data['id']}/input/cores/{macro_name}/fields/{quote(field_name)}")

    def _check_field_byte(self, macro_name: str, field_name: str, data: str) -> dict:
        body: dict = {'field': f"{field_name}", 'data': data}
        response = self.patch(f"/test_data/{self.test_data['id']}/input/cores/{macro_name}/fields", json=body)
        self.assertEqual(200, response.status_code)
        self.macro_fields.append((macro_name, field_name))
        body['id'] = response.json()['id']
        body['length'] = 0
        self.assertDictEqual(body, response.json())
        return body

    def _check_core(self, macro_name: str, field_bytes: List[dict]):
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        actual_test_data = response.json()
        expected_test_data = deepcopy(self.test_data)
        core_id = actual_test_data['cores'][0]['id']
        core = {'id': core_id, 'base_reg': str(), 'field_bytes': list(), 'macro_name': macro_name}
        expected_test_data['cores'].append(core)
        expected_test_data['cores'][0]['field_bytes'].extend(field_bytes)
        self.assertDictEqual(expected_test_data, actual_test_data)

    def test_default_field(self) -> None:
        field_byte1 = self._check_field_byte('WA0AA', 'WA0BBR', 'F1F2')
        field_byte2 = self._check_field_byte('WA0AA', '#WA0TTY', '01')
        self._check_core('WA0AA', [field_byte1, field_byte2])

    def test_based_field_delete(self) -> None:
        field_byte1 = self._check_field_byte('EB0EB', 'EBW000', '80')
        field_byte2 = self._check_field_byte('EB0EB', 'EBW001', 'C1C2C3C4')
        self._check_core('EB0EB', [field_byte1, field_byte2])
        # Delete 1st field
        response = self.delete(f"/test_data/{self.test_data['id']}/input/cores/EB0EB/fields/EBW000")
        self.assertEqual(200, response.status_code)
        del self.macro_fields[0]
        self.assertDictEqual(field_byte1, response.json())
        self._check_core('EB0EB', [field_byte2])
        # Deleting the 1st field again will give an error
        response = self.delete(f"/test_data/{self.test_data['id']}/input/cores/EB0EB/fields/EBW000")
        self.assertEqual(400, response.status_code)
        # Delete 2nd field
        response = self.delete(f"/test_data/{self.test_data['id']}/input/cores/EB0EB/fields/EBW001")
        self.assertEqual(200, response.status_code)
        del self.macro_fields[0]
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(200, response.status_code)
        self.assertEqual(list(), response.json()['cores'])

    def test_invalid_id(self):
        response = self.patch(f"/test_data/invalid_id/input/cores/WA0AA/fields", json={'field': 'WA0BBR', 'data': '01'})
        self.assertEqual(404, response.status_code)

    def test_no_field(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/cores/WA0AA/fields", json={'data': '01'})
        self.assertEqual(400, response.status_code)

    def test_empty_field(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/cores/WA0AA/fields",
                              json={'field': str(), 'data': '01'})
        self.assertEqual(400, response.status_code)

    def test_invalid_macro(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/cores/INVALID_MACRO/fields",
                              json={'field': 'WA0BBR', 'data': '01'})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({'message': 'Error in adding field', 'error': 'Bad Request'}, response.json())
        response = self.get(f"/test_data/{self.test_data['id']}")
        self.assertEqual(self.test_data, response.json())

    def test_invalid_length(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/cores/WA0AA/fields",
                              json={'field': 'WA0BBR', 'length': 'invalid_type', 'data': '01'})
        self.assertEqual(400, response.status_code)

    def test_invalid_data(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/cores/WA0AA/fields",
                              json={'field': 'WA0BBR', 'data': 123})
        self.assertEqual(400, response.status_code)

    def test_field_not_in_macro(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/cores/WA0AA/fields",
                              json={'field': 'EBW000', 'data': '01'})
        self.assertEqual(400, response.status_code)

    def test_no_data(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/cores/WA0AA/fields",
                              json={'field': 'WA0BBR'})
        self.assertEqual(400, response.status_code)

    def test_empty_data(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/cores/WA0AA/fields",
                              json={'field': 'WA0BBR', 'data': ''})
        self.assertEqual(400, response.status_code)

    def test_length_in_body(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/cores/WA0AA/fields",
                              json={'field': 'WA0BBR', 'data': '01', 'length': 1})
        self.assertEqual(400, response.status_code)

    def test_base_reg_in_body(self):
        response = self.patch(f"/test_data/{self.test_data['id']}/input/cores/WA0AA/fields",
                              json={'field': 'WA0BBR', 'data': '01', 'base_reg': 'R1'})
        self.assertEqual(400, response.status_code)

    def test_delete_invalid_id(self):
        response = self.delete(f"/test_data/invalid_id/input/cores/WA0AA/fields/WA0BBR")
        self.assertEqual(404, response.status_code)

    def test_delete_macro_name_not_in_core(self):
        response = self.delete(f"/test_data/{self.test_data['id']}/input/cores/WA0AA/fields/WA0BBR")
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({'message': 'Error in deleting field', 'error': 'Bad Request'}, response.json())
