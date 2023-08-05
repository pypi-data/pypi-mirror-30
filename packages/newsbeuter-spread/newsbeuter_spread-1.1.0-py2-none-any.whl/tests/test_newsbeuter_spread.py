import sys
import unittest
try:
    from unittest import mock
except ImportError:
    from mock import mock


class TestNewsbeuterSpread(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_newsbeuter_spread(self):
        # theres not much logic/model yet. but when theres is we'll be ready!
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
