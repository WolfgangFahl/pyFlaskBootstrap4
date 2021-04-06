'''
Created on 2021-02-06

@author: wf
'''
import unittest
from tests.test_webserver import TestWebServer
from fb4.sse_bp import PubSub
import datetime
import time

class Test_ServerSentEvents(unittest.TestCase):
    '''
    test the Server-Sent Event Blueprint
    '''   
    def setUp(self):
        self.debug=False
        self.ea,self.app,self.client=TestWebServer.getApp()
        PubSub.reinit()
        self.bp=self.ea.sseBluePrint
        self.bp.enableDebug(self.debug)
        pass

    def tearDown(self):
        pass
    
    def test_generate(self):
        '''
        check generator handling
        '''
        self.count=0
        def inc():
            self.count+=1
            return self.count
        gen=self.bp.generate(inc,3)
        genresult=list(gen)
        self.assertEqual([1,2,3],genresult)
        gen=self.bp.generate(inc,2)
        ssegen=self.bp.generateSSE(gen)
        genresult=list(ssegen)
        self.assertEqual(['data: 4\n\n', 'data: 5\n\n'],genresult)

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
        #self.debug=True
        limit=15
        # 0.5 msecs per Job
        timePerJob=0.5/1000
        for i in range(limit):
            run_date=now+datetime.timedelta(seconds=timePerJob)
            self.bp.scheduler.add_job(self.bp.publish, 'date',run_date=run_date,kwargs={"message":"message %d" %(i+1),"debug":self.debug})   
        sleepTime=(limit+2)*(timePerJob)
        time.sleep(sleepTime)
        #url=self.ea.basedUrl("/sse/sse")
        #print(url)
        response=self.client.get("/sse/sse")
        self.assertEqual(200,response.status_code)
        #req = requests.get(url, stream = True)
        #for r in req.iter_content():
        #    print(r)
        if self.debug:
            print(response.data)
        pubsub=PubSub.forChannel('sse')
        self.assertEqual(limit,pubsub.receiveCount)
        
   
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()