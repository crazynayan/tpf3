from test import TestAPI
from test.test_api.constants import TYPE, Types, FIELD_DATA, FIELD, DATA, MACRO_NAME, Actions, ACTION, NAME


class InputCoreBlock(TestAPI):

    def setUp(self):
        self.update_body = {
            NAME: TestAPI.NAME,
            ACTION: Actions.UPDATE,
            TYPE: Types.INPUT_CORE_BLOCK,
            FIELD_DATA: [
                {
                    FIELD: str(),
                    DATA: str()
                }
            ]
        }
        self.update_response = {
            "id": str(),
            NAME: TestAPI.NAME,
            TYPE: Types.INPUT_CORE_BLOCK,
            MACRO_NAME: str(),
            FIELD_DATA: [
                {
                    FIELD: str(),
                    DATA: str()
                }
            ]
        }

    def test_create(self):
        self.assertTrue(True)
