import sys

sys.path.append('..\\traceroute')

from traceroute.traceroute import *
import unittest
from unittest.mock import patch


class TestTraceroute(unittest.TestCase):

    @patch('platform.system')
    def test_traceroute_incompatible_system(self, system):
        system.return_value = 'Darwin'
        self.assertRaises(CompatibilityError, trace, "192.168.2.1")

    def test_traceroute_invalid_host(self):
        self.assertRaises(ResolutionError, trace, "x.x.x.x")