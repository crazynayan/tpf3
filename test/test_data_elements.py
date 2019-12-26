from config import config
from test import TestAPI


class OutputRegisters(TestAPI):

    def setUp(self) -> None:
        self.test_data = self.get_sample_test_data()
        self.reg_updated = False

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
