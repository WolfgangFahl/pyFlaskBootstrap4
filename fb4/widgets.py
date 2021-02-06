'''
Created on 2021-01-04

@author: wf
'''
from flask import render_template_string
import os
import site
import sys
import jinja2
from xml.dom import minidom

class Widget(object):
    '''
    a HTML widget
    '''
    def __init__(self,indent="",userdata=None,useFlask=True):
        self.indent=indent
        self.classes=[]
        self.useFlask=useFlask
        if userdata is None:
            self.userdata={}
        else:
            self.userdata=userdata
        pass
    
    def addClass(self,clazz):
        self.classes.append(clazz)
        
    def getClass(self):
        '''
        get the class attribute for this widget
        '''
        classAttr=' class="%s"' % ' '.join(self.classes) if len(self.classes) else ""
        return classAttr
    
    def __str__(self):
        html=self.render()
        return html
    
    def render_template_string(self,templateContent:str,**args)->str:
        '''
        delegate for flask render_template_string
        
        Args:
            templateContent(str): the content of the template
            args: the arguments
            
        Returns:
            str: the rendered string
        '''
        # https://stackoverflow.com/questions/31830663/how-to-render-template-in-flask-without-using-request-context
        # https://stackoverflow.com/questions/39288706/jinja2-load-template-from-string-typeerror-no-loader-for-this-environment-spec
        if self.useFlask:
            text=render_template_string(templateContent,**args)
        else:
            template = jinja2.Template(templateContent)    
            text=template.render(**args)
        return text

class Link(Widget):   
    '''
    a HTML link
    '''
    def __init__(self,url,title=None,tooltip=None,indent=""):
        '''
        constructor
        
        Args:
            url(str):  the link 
            title(str): the title
            tooltip(str): the tooltip (if any)
        '''
        super().__init__(indent=indent)
        self.url=url
        self.title="" if title is None else title
        self.tooltip="title='%s'" % tooltip if tooltip is not None else ""
        
    def render(self):
        html="%s<a href='%s'%s %s>%s</a>" % (self.indent,self.url,self.getClass(),self.tooltip,self.title)
        return html
        
class Image(Widget):
    '''
    a HTML Image
    '''
    def __init__(self,url,alt=None,title=None,width=None,height=None,indent=""):
        '''
        constructor
        
        Args:
            url(str):  the link 
            alt(str):  alternative image representation (if any)
            title(str): title/tooltip (if any)
            width: width of the image (if any)
            height: height of the image (if any)
        '''
        super().__init__(indent=indent)
        self.url=url
        if alt is not None:
            self.alt=alt
        else:
            self.alt=url
        self.title=title
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
        title=" title='%s'" % self.title if self.title is not None else ""
        html="%s<img src='%s'%s alt='%s'%s%s%s/>" % (self.indent,self.url,self.getClass(),self.alt,title,width,height)
        return html
    
class Icon(Widget):
    ''' 
    an Icon
    '''
    
    def __init__(self,name:str,size='32',color:str='primary',iconType:str='bootstrap',indent=''):
        '''
        constructor
        '''
        super().__init__(indent=indent)
        self.name=name
        self.size=str(size)
        self.color=color
        self.iconType=iconType
        pass
    
    @staticmethod
    def getBootstrapIconsFile():
        proots=[]
        try:
            for proot in [site.getusersitepackages(),site.getsitepackages()]:
                proots.append(proot)
        except Exception:
            # work around https://github.com/pypa/virtualenv/issues/804
            # probably venv issue  ignore
            pass
        iconsFile=None
        for proot in proots:
            iconsFile="%s/flask_bootstrap/static/icons/bootstrap-icons.svg" % proot
            if os.path.isfile(iconsFile):
                break
            else:
                iconsFile=None
        return iconsFile
    
    @staticmethod
    def getBootstrapIconsNames():
        '''
        get the bootstrap icon names
        
        Returns:
            list: a list of string with the icon names
        '''
        names=[]
        iconsFile=Icon.getBootstrapIconsFile()
        if iconsFile is not None:
            iconsDoc=minidom.parse(iconsFile)
            names=[path.getAttribute('id') for path
                in iconsDoc.getElementsByTagName('symbol')]
        return names
    
    
    def render(self)->str:
        '''
        render me as html
        
        Returns:
            str: html code for Icon
        '''
        # https://icons.getbootstrap.com/icons/ is the default
        template="""
{%% from 'bootstrap/utils.html' import render_icon %%}        
{{ render_icon('%s', %s,'%s') }}""" % (self.name,self.size,self.color)
        html=self.render_template_string(template)
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
        self.addClass("nav-item")
        if active: self.addClass("active")
    
    def render(self):
        '''
        render me
        
        Returns:
            str: html code for MenuItem
        '''
        html='''%s<li%s>
%s  <a class="nav-link" href="%s">%s</a>
%s</li>''' % (self.indent,self.getClass(),self.indent,self.url,self.title,self.indent)
        return html
    
class BaseMenu(Widget):
    ''' 
    a menu
    '''
    
    def __init__(self,indent=""):
        super().__init__(indent=indent)
        self.items=[]
        
    def addItem(self,item:MenuItem):
        '''
        add the given item
        
        Args:
            item(MenuItem): the menuitem to add
        '''
        item.indent="      "
        self.items.append(item)
        
    def render(self):
        '''
        render me
        
        Returns:
            str: html code for Menu
        '''
        template="<%s%s>%s</%s>" % (self.tag,self.getClass(),self.template,self.tag)
        html=self.render_template_string(template,menuItemList=self.items)
        return html
    
class Menu(BaseMenu):
    
    def __init__(self,indent=""):
        super().__init__(indent=indent)
        self.template="""
  <div class="collapse navbar-collapse" id="navbarNav">
    <ul class="navbar-nav">
{% if menuItemList %}{% for menuItem in menuItemList %}{{ menuItem|safe }}{% endfor %}{% endif %}
    </ul>
  </div>   
"""
        self.addClass("navbar")
        self.addClass("navbar-expand-lg")
        self.addClass("navbar-light")
        self.addClass("bg-light")
        self.tag="nav"
    
class DropDownMenu(BaseMenu):
    '''
    a drop down menu
    '''

    def __init__(self,title=None,indent=""):
        super().__init__(indent=indent)
        self.title="" if title is None else title
        self.tag="div"
        self.addClass("dropdown")
        # https://www.tutorialrepublic.com/twitter-bootstrap-tutorial/bootstrap-dropdowns.php
        self.template="""
    <a href="#" class="dropdown-toggle" data-toggle="dropdown">"""+self.title+"""</a>
    <div class="dropdown-menu">
{% if menuItemList %}{% for menuItem in menuItemList %}{{ menuItem|safe }}{% endfor %}{% endif %}
    </div>
"""
        pass
        
    def addItem(self,item:MenuItem):
        item.addClass("dropdown-item")
        super().addItem(item)
