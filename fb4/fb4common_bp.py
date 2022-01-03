'''
Created on 2022-01-03

@author: wf
'''
from flask import Blueprint

class Fb4CommonBluePrint(object):
    '''
    pyFlaskBootstrap4 common functions and templates
    
    https://github.com/WolfgangFahl/pyFlaskBootstrap4
    '''
    
    def __init__(self,app,name:str,template_folder:str=None):
        '''
        construct me
        
        Args:
            app(Appwrap): the application to register me for
            name(str): my name
            template_folder(str): the template folder
        '''
        if template_folder is not None:
            self.template_folder=template_folder
        else:
            self.template_folder='templates'    
        self.blueprint=Blueprint(name,__name__,template_folder=self.template_folder)
        self.app=app
        app.register_blueprint(self.blueprint)