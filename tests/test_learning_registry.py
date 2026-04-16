import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "ai-factory-v2"
sys.path.insert(0, str(APP_DIR))

import config
from learning.registry import LearningRegistry


class LearningRegistryPathTests(unittest.TestCase):
    def test_learning_file_config_uses_absolute_app_path(self):
        expected = APP_DIR / "learning" / "history.json"
        self.assertTrue(Path(config.LEARNING_FILE).is_absolute())
        self.assertEqual(Path(config.LEARNING_FILE).resolve(), expected.resolve())

    def test_relative_learning_path_resolves_inside_app_dir(self):
        registry = LearningRegistry("learning/history.json")
        expected = APP_DIR / "learning" / "history.json"
        self.assertEqual(registry.history_path.resolve(), expected.resolve())


if __name__ == "__main__":
    unittest.main()
