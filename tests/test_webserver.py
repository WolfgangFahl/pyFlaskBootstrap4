'''
Created on 2020-07-11

@author: wf
'''
import unittest
import warnings
from flask import current_app
from fb4.app import AppWrap
from fb4_example.bootstrap_flask.exampleapp import ExampleApp
import socket

class TestWebServer(unittest.TestCase):
    ''' see https://www.patricksoftwareblog.com/unit-testing-a-flask-application/ '''

    @staticmethod
    def getApp():
        warnings.simplefilter("ignore", ResourceWarning)
        ea=ExampleApp()
        app=ea.app
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        #hostname=socket.getfqdn()
        #app.config['SERVER_NAME'] = "http://"+hostname
        app.config['DEBUG'] = False
        test_app = app.test_client()
        return ea, test_app
        
    def setUp(self):
        self.debug=False
        self.ea,self.app=TestWebServer.getApp()
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
        
    def checkResponse(self,response,expectedStatus=200):
        self.assertEqual(response.status_code, expectedStatus)
        self.assertTrue(response.data is not None)
        html=response.data.decode()
        if self.debug:
            print(html)
        return html
        

    def testWebServer(self):
        ''' 
        test the WebServer
        '''
        queries=['/','/form']
        expected=[
            "Welcome","Country Code"
        ]
        self.debug=False
        for i,query in enumerate(queries):
            url=self.ea.basedUrl(query)
            self.assertTrue(url.startswith("http://"))
            response=self.app.get(query)
            html=self.checkResponse(response)
            ehtml=expected[i]
            self.assertTrue(ehtml,ehtml in html)
            
    def testLogin(self):
        '''
        test the login functionality
        
        including https://github.com/WolfgangFahl/pyFlaskBootstrap4/issues/15
        add function to retrieve details of currently logged in User
        '''
        response=self.app.post('/login',data=dict(username='drWho',password='notvalid'),follow_redirects=True);
        html=self.checkResponse(response)
        self.assertTrue('Invalid username or password' in html)
        self.assertFalse('logout' in html)
        response=self.app.post('/login',data=dict(username='scott',password='tiger2021'),follow_redirects=True);
        html=self.checkResponse(response)
        self.assertTrue('logout' in html)
        response=self.app.get('/logout',follow_redirects=True)
        html=self.checkResponse(response)
        #print(html)
        self.assertTrue('login' in html)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
