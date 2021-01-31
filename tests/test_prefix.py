'''
Created on 2021-01-27

@author: wf
'''
import unittest
import warnings
from fb4_example.helloweb import HelloWeb

class TestPrefix(unittest.TestCase):
    '''
    test using a prefix
    see e.g. https://stackoverflow.com/questions/18967441/add-a-prefix-to-all-flask-routes
    '''

    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)
        self.debug=False
        self.web=HelloWeb()
        app=self.web.app
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
        pass

    def tearDown(self):
        pass

    def checkResponse(self,response,expectedStatus=200):
        self.assertEqual(response.status_code, expectedStatus)
        self.assertTrue(response.data is not None)
        html=response.data.decode()
        if self.debug:
            print(html)
        return html

    def testPrefix(self):
        '''
        test prefix handling
        '''
        query="/"
        response=self.app.get(query)
        html=self.checkResponse(response, 200)
        self.assertTrue("<title>HelloWeb demo application</title>" in html)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()