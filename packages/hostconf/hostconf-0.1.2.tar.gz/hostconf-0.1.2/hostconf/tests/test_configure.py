"""
Unit testing for parts of the editline and _editline modules.
"""
import os
import sys
import unittest
import subprocess
from test.support import import_module

class TestEditline(unittest.TestCase):

    def test_001_import_pkg(self):
        hostconf = import_module('hostconf')

    def test_002_import_module(self):
        configure = import_module('hostconf.configure')

    def test_003_build_instance(self):
        cfm = import_module('hostconf.configure')
        cfg = cfm.Configure('test_conf')
        self.assertIsNotNone(cfg)


if __name__ == "__main__":
    unittest.main()
