'''
Created on 2021-01-08

This is a demo application for https://github.com/WolfgangFahl/pyFlaskBootstrap4

@author: wf
'''
from fb4.app import AppWrap
from flask import render_template

class HelloWeb(AppWrap):
    '''
    a sample web application
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        
    def home(self):
        '''
        render the home page of the HelloWeb application
        '''
        html = render_template("bootstrap.html", title="HelloWeb demo application",content="Welcome to the Flask + Bootstrap4 Demo web application",error=None)
        return html
    
helloWeb=HelloWeb()
app=helloWeb.app 
@app.route('/')
def home():
    return helloWeb.home()

if __name__ == '__main__':
    parser=helloWeb.getParser("Flask + Bootstrap4 Demo Web Application")
    args=parser.parse_args()
    helloWeb.optionalDebug(args)
    helloWeb.run(args)
        