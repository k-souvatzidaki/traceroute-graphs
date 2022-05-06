import sys
sys.path.append('..\\traceroute')

from traceroute.helpers import *
import unittest
from unittest.mock import patch


class TestHelpers(unittest.TestCase):

    def test_is_compatible_windows_macos(self):
        self.assertRaises(CompatibilityError, is_compatible, 'Windows')
        self.assertRaises(CompatibilityError, is_compatible, 'Darwin')

    def test_is_compatible_linux(self):
        self.assertTrue(is_compatible('Linux'))

    def test_resolve_invalid(self):
        self.assertRaises(ResolutionError, resolve, 'www.xxxxxx.invalid')
        self.assertRaises(ResolutionError, resolve, '1.2.3.4.5')

    def test_resolve_valid(self):
        self.assertEqual(resolve('localhost'), '127.0.0.1')
        self.assertEqual(resolve('172.217.17.238'), '172.217.17.238')
        self.assertEqual(resolve('192.168.2.1'), '192.168.2.1')

    @patch('socket.gethostbyname')
    def test_resolve_valid_url_mock(self, gethostbyname):
        gethostbyname.return_value = '172.217.169.110'
        self.assertEqual(resolve('www.google.com'), '172.217.169.110')