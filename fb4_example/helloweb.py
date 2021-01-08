'''
Created on 2021

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
        html = render_template("bootstrap.html", content="Welcome to the Flask + Bootstrap4 Demo web application")
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
        