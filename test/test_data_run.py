from base64 import b64decode

from test import TestAPI


class RunTestData(TestAPI):

    def setUp(self) -> None:
        self.test_data = self.get_sample_test_data()
        self.default_pnr = {'key': 'name', 'locator': str(), 'variation': 0, 'data': str()}

    def test_name_variation(self):
        self.default_pnr['data'] = "2ZAVERI, 6SHAH"
        self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.default_pnr['variation'] = 1
        self.default_pnr['data'] = "C/21TOURS, 2ZAVERI, 6SHAH"
        self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.default_pnr['variation'] = 2
        self.default_pnr['data'] = "2ZAVERI, 6SHAH, I/3ZAVERI"
        self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.default_pnr['variation'] = 3
        self.default_pnr['data'] = "C/21TOURS, 2ZAVERI, 6SHAH, I/3ZAVERI"
        self.patch(f"/test_data/{self.test_data['id']}/input/pnr", json=self.default_pnr)
        self.patch(f"/test_data/{self.test_data['id']}/output/cores/WA0AA/fields",
                   json={'field': 'WA0EXT', 'length': 0, 'base_reg': str()})
        response = self.get(f"/test_data/{self.test_data['id']}/run")
        self.assertEqual(200, response.status_code)
        outputs = response.json()['outputs']
        self.assertEqual('F0F0', b64decode(outputs[0]['cores'][0]['field_data'][0]['data']).hex().upper())
        self.assertEqual('F1F3', b64decode(outputs[1]['cores'][0]['field_data'][0]['data']).hex().upper())
        self.assertEqual('F0F0', b64decode(outputs[2]['cores'][0]['field_data'][0]['data']).hex().upper())
        self.assertEqual('F1F3', b64decode(outputs[3]['cores'][0]['field_data'][0]['data']).hex().upper())
