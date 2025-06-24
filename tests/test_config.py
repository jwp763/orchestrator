import os, sys; sys.path.insert(0, os.path.abspath("src"))
import unittest
import os
from src.config import Settings

class TestSettings(unittest.TestCase):
    def test_model_for_task(self):
        os.environ['ANTHROPIC_API_KEY'] = 'key'
        s = Settings()
        provider, model = s.get_model_for_task('complex_reasoning')
        self.assertTrue(provider in ['anthropic','openai'])
        self.assertIsNotNone(model)

if __name__ == '__main__':
    unittest.main()
