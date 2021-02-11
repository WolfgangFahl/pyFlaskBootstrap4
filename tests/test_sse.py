'''
Created on 2021-02-06

@author: wf
'''
import unittest
from unittest.mock import patch
from tests.test_webserver import TestWebServer
from fb4.sse_bp import PubSub
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

class Test_ServerSentEvents(unittest.TestCase):
    '''
    test the Server-Sent Event Blueprint
    '''

    def setUp(self):
        self.debug=False
        self.ea,self.app=TestWebServer.getApp()
        PubSub.reinit()
        self.bp=self.ea.sseBluePrint
        self.scheduler = BackgroundScheduler()
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
            self.assertEqual("publish() missing 1 required positional argument: 'message'",msg)
        self.assertEqual({},PubSub.pubSubByChannel)
        
    def test_publish(self):
        '''
        test publishing a thing
        '''
        self.bp.publish("thing")
        self.assertTrue("sse" in PubSub.pubSubByChannel)
        self.assertEqual(1,len(PubSub.pubSubByChannel))
        
    def test_publish_channel(self):
        '''
        test publishing a thing via the channel garden
        '''
        pubSub=self.bp.publish("thing", channel='garden')
        self.assertTrue("garden" in PubSub.pubSubByChannel)
        self.assertEqual("garden",pubSub.channel)
        
    def test_messages(self):
        '''
        test message handling
        '''
        now=datetime.datetime.now()
        for i in range(15):
            run_date=now+datetime.timedelta(seconds=0.005+i*0.01)
            self.scheduler.add_job(self.bp.publish, 'date',run_date=run_date,kwargs={"message":"message %d" %i})
        # kwargs={'type':'example'}
        
        self.scheduler.start()
        self.debug=True
        response=self.bp.subscribe('sse',debug=self.debug)
        if self.debug:
            print(response.data)
   
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()