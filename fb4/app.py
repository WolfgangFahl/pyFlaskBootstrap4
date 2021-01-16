'''
Created on 2020-12-30

@author: wf
'''
from flask import Flask
from flask import render_template
import argparse
import os
import sys
from flask_httpauth import HTTPBasicAuth
from pydevd_file_utils import setup_client_server_paths
from flask_bootstrap import Bootstrap

class AppWrap:
    ''' 
    Wrapper for Flask Web Application 
    '''
    
    def __init__(self, host:str='0.0.0.0', port:int=8234, debug:bool=False,template_folder=None):
        '''
        constructor
        
        Args:
            host(str): flask host
            port(int): the port to use for http connections
            debug(bool): True if debugging should be switched on
        '''
        self.debug = debug
        self.port = port
        self.host = host    
        if template_folder is None:
            scriptdir = os.path.dirname(os.path.abspath(__file__))
            template_folder=scriptdir + '/../templates'
    
        self.app = Flask(__name__, template_folder=template_folder)
        # pimp up jinja2
        self.app.jinja_env.globals.update(isinstance=isinstance)
        self.auth= HTTPBasicAuth()
        self.baseUrl=""
        self.bootstrap = Bootstrap(self.app)
        # should be configurable again
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        # set default bootstrap button style and size
        self.app.config['BOOTSTRAP_BTN_STYLE'] = 'primary'
        self.app.config['BOOTSTRAP_BTN_SIZE'] = 'sm'
        
    @staticmethod
    def splitPath(path:str):
        '''
        split the given path
        
        Args:
            path(str): the path to split
        Returns:
            str: the site of the path an the actual path
        '''
        # https://stackoverflow.com/questions/2136556/in-python-how-do-i-split-a-string-and-keep-the-separators
        parts = path.split(r"/")
        site = ""
        if len(parts) > 0:
            site = parts[0]
        path = ""
        if len(parts) > 1:
            for part in parts[1:]:
                path = path + "/%s" % (part)
        return site, path
    
    def error(self,title:str,error:str):
        '''
        render the given error with the given title
        
        Args:
            title(str): the title to display
            error(str): the error to display
    
        Returns:
            str: the html code
        '''
        template="bootstrap.html"
        title=title
        content=None
        html=render_template(template, title=title, content=content, error=error)
        return html
    
    def run(self,args):
        '''
        start the flask webserver
        
        Args:
            args(): the parser args
        '''
        self.debug=args.debug
        self.baseUrl=args.baseUrl
        self.app.run(debug=self.debug, port=self.port, host=self.host)   
        pass
    
    @staticmethod
    def getParser(description:str):
        '''
        get the parser with the given description
        
        Args:
            description(str): the description text to be shown in the usage
            
        Returns:
            ArgumentParser: the parser
        '''
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('--baseUrl',default='',help='base url to use for links to this site')
        parser.add_argument('--debug',
                                     action='store_true',
                                     help="run in debug mode")
        parser.add_argument('--debugServer',
                                     help="remote debug Server")
        parser.add_argument('--debugPort',type=int,
                                     help="remote debug Port",default=5678)
        parser.add_argument('--debugPathMapping',nargs='+',help="remote debug Server path mapping - needs two arguments 1st: remotePath 2nd: local Path")
        return parser
        
    def optionalDebug(self,args):   
        '''
        start the remote debugger if the arguments specify so
        
        Args:
            args(): The command line arguments
        '''
        if args.debugServer:
            import pydevd
            print (args.debugPathMapping,flush=True)
            if args.debugPathMapping:
                if len(args.debugPathMapping)==2:
                    remotePath=args.debugPathMapping[0] # path on the remote debugger side
                    localPath=args.debugPathMapping[1]  # path on the local machine where the code runs
                    MY_PATHS_FROM_ECLIPSE_TO_PYTHON = [
                        (remotePath, localPath),
                    ]
                    setup_client_server_paths(MY_PATHS_FROM_ECLIPSE_TO_PYTHON)
                    #os.environ["PATHS_FROM_ECLIPSE_TO_PYTHON"]='[["%s", "%s"]]' % (remotePath,localPath)
                    #print("trying to debug with PATHS_FROM_ECLIPSE_TO_PYTHON=%s" % os.environ["PATHS_FROM_ECLIPSE_TO_PYTHON"]);
         
            pydevd.settrace(args.debugServer, port=args.debugPort,stdoutToServer=True, stderrToServer=True)
            print("command line args are: %s" % str(sys.argv))