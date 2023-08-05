#!/usr/bin/env python

import unittest
import TestCeroCoinHashing

class CeroCoinTestCase( unittest.TestCase ):
    def checkVersion(self):
        import CeroCoinClient

testSuites = [unittest.makeSuite(CeroCoinTestCase, 'test')] 

for test_type in [
            TestCeroCoinHashing
    ]:
    testSuites.append(test_type.getTestSuites('test'))


def getTestDirectory():
    try:
        return os.path.abspath(os.path.dirname(__file__))
    except:
        return '.'

import os
os.chdir(getTestDirectory())

runner = unittest.TextTestRunner()
runner.run(unittest.TestSuite(testSuites))
