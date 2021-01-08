'''
Created on 2021-01-04

@author: wf
'''

class Widget(object):
    '''
    a HTML widget
    '''
    def __init(self):
        pass
    
    def __str__(self):
        html=self.render()
        return html

class Link(Widget):   
    '''
    a HTML link
    '''
    def __init__(self,url,title,tooltip=None):
        '''
        constructor
        
        Args:
            url(str):  the link 
            title(str): the title
            tooltip(str): the tooltip (if any)
        '''
        self.url=url
        self.title=title
        self.tooltip=tooltip
        
    def render(self):
        html="<a href='%s'>%s</a>" % (self.url,self.title)
        return html
        
class Image(Widget):
    '''
    a HTML Image
    '''
    def __init__(self,url,alt=None,width=None,height=None):
        '''
        constructor
        
        Args:
            url(str):  the link 
            alt(str):  alternative image representation (if any)
        '''
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
        
        html="<img src='%s' alt='%s'%s%s/>" % (self.url,self.alt,width,height)
        return html
    
class MenuItem(Widget):
    '''
    a menu item
    '''
    
    def __init__(self,url:str,title:str,active:bool=False):
        '''
        constructor
        
        Args:
            url(str):  the link
            title(str): the title of the menu item
            active(bool): whether the link is initially active 
        '''
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
        html='''<li class="nav-item %s">
        <a class="nav-link" href="%s">%s</a>
      </li>''' % (activeState,self.url,self.title)
        return html