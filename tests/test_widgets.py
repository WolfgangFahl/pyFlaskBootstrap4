'''
Created on 2021-01-04

@author: wf
'''
import unittest
from fb4.widgets import Link,Image,Menu,MenuItem,Widget, DropDownMenu

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
        menu=Menu()
        menuItem1=MenuItem("http://test.bitplan.com","BITPlan testSite",True)
        menu.addItem(menuItem1)
        dropDownMenu=DropDownMenu()
        dropDownMenu.addItem(Link("http://www.bitplan.com","BITPlan webPage"))
        widgets=[
            Link("http://www.bitplan.com","BITPlan webPage",tooltip="BITPlan GmbH"),
            Image("http://wiki.bitplan.com/images/wiki/thumb/3/38/BITPlanLogoFontLessTransparent.png/132px-BITPlanLogoFontLessTransparent.png",alt='BITPlan Logo'),
            MenuItem("http://test.bitplan.com","BITPlan testSite",True),
            menu,
            dropDownMenu
        ]
        expectedHtml=[
            "<a href='http://www.bitplan.com' title='BITPlan GmbH'>BITPlan webPage</a>",
            "<img src='http://wiki.bitplan.com/images/wiki/thumb/3/38/BITPlanLogoFontLessTransparent.png/132px-BITPlanLogoFontLessTransparent.png' alt='BITPlan Logo'/>",
            """<li class="nav-item active">
  <a class="nav-link" href="http://test.bitplan.com">BITPlan testSite</a>
</li>""",
            """<nav class="navbar navbar-expand-lg navbar-light bg-light">
  <div class="collapse navbar-collapse" id="navbarNav">
    <ul class="navbar-nav">
      <li class="nav-item active">
        <a class="nav-link" href="http://test.bitplan.com">BITPlan testSite</a>
      </li>
    </ul>
  </div>   
</nav>""",
        """<div class="dropdown">
    <a href="#" class="dropdown-toggle" data-toggle="dropdown">Dropdown</a>
    <div class="dropdown-menu">
      <a href='http://www.bitplan.com' class="dropdown-item" >BITPlan webPage</a>
    </div>
</div>"""
            ]
        for i,widget in enumerate(widgets):
            widget.useFlask=False
            self.assertTrue(isinstance(widget,Widget))
            html=widget.render()
            self.debug=False
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
            Link("http://www.bitplan.com","BITPlan home page",tooltip="BITPlan")
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