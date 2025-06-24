import os, sys; sys.path.insert(0, os.path.abspath("src"))
import unittest
from unittest.mock import MagicMock
from src.storage import DeltaManager

class TestDeltaManager(unittest.TestCase):
    def test_generate_id_unique(self):
        dm = DeltaManager(spark=MagicMock())
        a = dm._generate_id()
        b = dm._generate_id()
        self.assertNotEqual(a,b)

    def test_table_path(self):
        dm = DeltaManager(spark=MagicMock())
        path = dm._get_table_path('users')
        self.assertTrue(path.endswith('.users'))

if __name__ == '__main__':
    unittest.main()
