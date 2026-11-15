"""Dependency contract tests; no service credentials or network required."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DependencyTests(unittest.TestCase):
    def test_security_updates_are_locked_and_exported(self):
        lock = json.loads((ROOT / "Pipfile.lock").read_text())
        exported = dict(re.findall(r"^([\w-]+)==([\w.]+)", (ROOT / "requirements.txt").read_text(), re.M))
        minimums = {"werkzeug": (3, 1, 5), "jinja2": (3, 1, 6),
                    "urllib3": (2, 6, 3), "pyjwt": (2, 12, 1),
                    "certifi": (2024, 7, 4)}
        for name, minimum in minimums.items():
            with self.subTest(package=name):
                version = lock["default"][name]["version"].removeprefix("==")
                self.assertGreaterEqual(tuple(map(int, version.split("."))), minimum)
                self.assertEqual(exported[name], version)
        self.assertEqual(set(exported), set(lock["default"]))
        for name, dependency in lock["default"].items():
            self.assertEqual(exported[name], dependency["version"].removeprefix("=="))
            self.assertTrue(dependency["hashes"])


if __name__ == "__main__":
    unittest.main()
