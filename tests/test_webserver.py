'''
Created on 2020-07-11

@author: wf
'''
import unittest
import warnings
from fb4.app import AppWrap

class TestWebServer(unittest.TestCase):
    ''' see https://www.patricksoftwareblog.com/unit-testing-a-flask-application/ '''

    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)
        self.debug=False
        import  fb4_example.helloweb 
        app=fb4_example.helloweb.helloWeb.app
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
        pass

    def tearDown(self):
        pass
    
    @staticmethod
    def initServer():
        '''
        initialize the server
        '''
        
    def testSplit(self):
        '''
        test splitting the path into site an path
        '''
        paths=['admin/','or/test']
        expected=[('admin','/'),('or','/test')]
        for i,testpath in enumerate(paths):
            site,path=AppWrap.splitPath(testpath)
            if self.debug:
                print("%s:%s" % (site,path))
            esite,epath=expected[i]
            self.assertEqual(esite,site)
            self.assertEqual(epath,path)

    def testWebServer(self):
        ''' 
        test the WebServer
        '''
        queries=['/']
        expected=[
            "Welcome",
        ]
        #self.debug=True
        for i,query in enumerate(queries):
            response=self.app.get(query)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.data is not None)
            html=response.data.decode()
            if self.debug:
                print(html)
            ehtml=expected[i]
            self.assertTrue(ehtml,ehtml in html)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
