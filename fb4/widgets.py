'''
Created on 2021-01-04

@author: wf
'''

class Widget(object):
    '''
    a HTML widget
    '''
    def __init__(self,indent=""):
        self.indent=indent
        pass
    
    def __str__(self):
        html=self.render()
        return html

class Link(Widget):   
    '''
    a HTML link
    '''
    def __init__(self,url,title,tooltip=None,indent=""):
        '''
        constructor
        
        Args:
            url(str):  the link 
            title(str): the title
            tooltip(str): the tooltip (if any)
        '''
        super().__init__(indent=indent)
        self.url=url
        self.title=title
        self.tooltip=tooltip
        
    def render(self):
        html="%s<a href='%s'>%s</a>" % (self.indent,self.url,self.title)
        return html
        
class Image(Widget):
    '''
    a HTML Image
    '''
    def __init__(self,url,alt=None,width=None,height=None,indent=""):
        '''
        constructor
        
        Args:
            url(str):  the link 
            alt(str):  alternative image representation (if any)
        '''
        super().__init__(indent=indent)
        self.url=url
        if alt is not None:
            self.alt=alt
        else:
            self.alt=url
        self.width=width
        self.height=height
        
    def render(self):
        '''
        render me
        
        Returns:
            str: html code for Image
        '''
        width=" width='%d'" % self.width if self.width is not None else ""
        height=" height='%d'" % self.height if self.height is not None else ""
        
        html="%s<img src='%s' alt='%s'%s%s/>" % (self.indent,self.url,self.alt,width,height)
        return html
    
class MenuItem(Widget):
    '''
    a menu item
    '''
    
    def __init__(self,url:str,title:str,active:bool=False,indent=""):
        '''
        constructor
        
        Args:
            url(str):  the link
            title(str): the title of the menu item
            active(bool): whether the link is initially active 
        '''
        super().__init__(indent=indent)
        self.url=url
        self.title=title
        self.active=active
    
    def render(self):
        '''
        render me
        
        Returns:
            str: html code for MenuItem
        '''
        activeState='active' if self.active else ''
        html='''%s<li class="nav-item %s">
%s  <a class="nav-link" href="%s">%s</a>
%s</li>''' % (self.indent,activeState,self.indent,self.url,self.title,self.indent)
        return html