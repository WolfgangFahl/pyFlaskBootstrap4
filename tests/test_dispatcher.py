'''
Created on 2021-02-10

@author: wf
'''
import unittest
from pydispatch import dispatcher

class TestPyDispatcher(unittest.TestCase):
    '''
    http://pydispatcher.sourceforge.net/
    '''

    def setUp(self):
        self.messages=[]
        pass


    def tearDown(self):
        pass

    
    def handle_event(self,sender,msg):
        if sender is not None:
            self.messages.append(msg)

    def testDispatcher(self):
        signal="signal"
        dispatcher.connect(self.handle_event,signal=signal,sender=dispatcher.Any)
        sender=object();
        for i in range(10):
            dispatcher.send(signal=signal,sender=sender,msg="Message %d " % i)
        self.assertEqual(10,len(self.messages))
        print (self.messages)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()