import os
from tests import TempDirFixture
from unittest import TestCase
from tests.context import globalite

_test_db = "test.db"
_test_table = "globals"

class TestGlobalite(TempDirFixture, TestCase):
    
    def setUp(self):
        super().setUp()

        self.globalite = _Globalite(_test_db, _test_table)
        self.globalite.test_int = 20
        self.globalite.test_string = "test string"
        self.globalite.test_bool = False
        self.globalite.test_dict = {
            "valueOne": True,
            "valueTwo": 5,
            "valueThree": "Hello World",
            "valueFour": {"valueFourOne": 2}
        }
        self.globalite.test_float = 2.1

    def tearDown(self):
        if os.path.isfile(_test_db):
            os.remove(_test_db)
        
        super().tearDown()

class TestGlobaliteInitialization(TestCase):
    pass

class TestGlobalsPersistency(TestCase):
    pass
