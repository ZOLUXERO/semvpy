import unittest
from semvpy.formater import parse_version


class TestParseVersion(unittest.TestCase):
    def test_parse_version(self):
        self.assertEqual(parse_version("v1.0.0"), [1, 0, 0])
