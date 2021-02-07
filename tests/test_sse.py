'''
Created on 2021-02-06

@author: wf
'''
import unittest
from tests.test_webserver import TestWebServer
from fb4.sse_bp import Message

class Test_ServerSentEvents(unittest.TestCase):
    '''
    test the Server-Sent Event Blueprint
    '''

    def setUp(self):
        self.ea,self.app=TestWebServer.getApp()
        self.bp=self.ea.sseBluePrint
        pass


    def tearDown(self):
        pass


    def test_publish_nothing(self):
        '''
        test publishing nothing
        '''
        try:
            self.bp.publish()
            self.fail("should raise an exception")
        except Exception as ex:
            msg=str(ex)
            self.assertEqual("publish() missing 1 required positional argument: 'data'",msg)
        self.assertEqual({},self.bp.pubsub.publisherByChannel)
        
    def test_publish(self):
        '''
        test publishing a thing
        '''
        self.bp.publish("thing")
        self.assertTrue("sse" in self.bp.pubsub.publisherByChannel)
        self.assertEqual(1,len(self.bp.pubsub.publisherByChannel))
        
    def test_publish_channel(self):
        '''
        test publishing a thing via the channel garden
        '''
        self.bp.publish("thing", channel='garden')
        self.assertTrue("garden" in self.bp.pubsub.publisherByChannel)
        self.assertEqual(1,len(self.bp.pubsub.publisherByChannel))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()