'''
Created on 2021-01-04

@author: wf
'''
import unittest
from fb4.widgets import Link,Image,MenuItem,Widget

class TestWidgets(unittest.TestCase):
    '''
    test the HTML widgets
    '''


    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass


    def testWidgets(self):
        '''
        test widget handling
        '''
        widgets=[
            Link("http://www.bitplan.com","BITPlan webPage"),
            Image("http://wiki.bitplan.com/images/wiki/thumb/3/38/BITPlanLogoFontLessTransparent.png/132px-BITPlanLogoFontLessTransparent.png",alt='BITPlan Logo'),
            MenuItem("http://test.bitplan.com","BITPlan testSite",True)
        ]
        expectedHtml=[
            "<a href='http://www.bitplan.com'>BITPlan webPage</a>",
            "<img src='http://wiki.bitplan.com/images/wiki/thumb/3/38/BITPlanLogoFontLessTransparent.png/132px-BITPlanLogoFontLessTransparent.png' alt='BITPlan Logo'/>",
            """<li class="nav-item active">
  <a class="nav-link" href="http://test.bitplan.com">BITPlan testSite</a>
</li>"""
            ]
        for i,widget in enumerate(widgets):
            self.assertTrue(isinstance(widget,Widget))
            html=widget.render()
            if self.debug:
                print(html)
            self.assertEqual(expectedHtml[i],html)
            self.assertEqual(expectedHtml[i],str(widget))
        pass
    
    def testJinjaType(self):
        '''
        test Jinja template type check workaround according to
        https://stackoverflow.com/a/38086633/1497139
        '''
        values=[
            "text",
            8,
            Link("http://www.bitplan.com","BITPlan home page")
            ]
        expected=[
            "str","int","Link"]
        for i,value in enumerate(values):
            valueType=value.__class__.__name__
            if self.debug:
                print(valueType)
            self.assertEqual(expected[i],valueType)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()