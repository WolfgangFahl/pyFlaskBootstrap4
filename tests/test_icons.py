'''
Created on 2021-01-17

@author: wf
'''
import unittest
from fb4.widgets import Icon
import getpass
from tests.basetest import BaseTest
class TestIcons(BaseTest):
    """
    test Icons
    """


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testIcons(self):
        '''
        test getting the bootstrap Icons File
        '''        
        if self.inPublicCI():
            return
        iconsFile=Icon.getBootstrapIconsFile()
        self.assertTrue(iconsFile is not None)
        iconNames=Icon.getBootstrapIconsNames()
        self.assertTrue(len(iconNames)>1000)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()