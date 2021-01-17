# -*- coding: utf-8 -*-
from fb4.app import AppWrap
from fb4.widgets import Link, Icon,Image
from flask import Flask, render_template, request, flash, Markup, jsonify

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, TextField,\
    FormField, SelectField, FieldList
from wtforms.validators import DataRequired, Length
from wtforms.fields import *

from flask_sqlalchemy import SQLAlchemy
import os

class ExampleForm(FlaskForm):
    """An example form that contains all the supported bootstrap style form fields."""
    date = DateField(description="We'll never share your email with anyone else.")  # add help text with `description`
    datetime = DateTimeField(render_kw={'placeholder': 'this is placeholder'})  # add HTML attribute with `render_kw`
    image = FileField(render_kw={'class': 'my-class'})  # add your class
    option = RadioField(choices=[('dog', 'Dog'), ('cat', 'Cat'), ('bird', 'Bird'), ('alien', 'Alien')])
    select = SelectField(choices=[('dog', 'Dog'), ('cat', 'Cat'), ('bird', 'Bird'), ('alien', 'Alien')])
    selectmulti = SelectMultipleField(choices=[('dog', 'Dog'), ('cat', 'Cat'), ('bird', 'Bird'), ('alien', 'Alien')])
    bio = TextAreaField()
    title = StringField()
    secret = PasswordField()
    remember = BooleanField('Remember me')
    submit = SubmitField()


class HelloForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 150)])
    remember = BooleanField('Remember me')
    submit = SubmitField()


class ButtonForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField()
    delete = SubmitField()
    cancel = SubmitField()


class TelephoneForm(FlaskForm):
    country_code = IntegerField('Country Code')
    area_code = IntegerField('Area Code/Exchange')
    number = TextField('Number')


class IMForm(FlaskForm):
    protocol = SelectField(choices=[('aim', 'AIM'), ('msn', 'MSN')])
    username = TextField()


class ContactForm(FlaskForm):
    first_name = TextField()
    last_name = TextField()
    mobile_phone = FormField(TelephoneForm)
    office_phone = FormField(TelephoneForm)
    emails = FieldList(TextField("Email"), min_entries=3)
    im_accounts = FieldList(FormField(IMForm), min_entries=2)

class ExampleApp(AppWrap):
    '''
    flask app wrapped in class 
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        scriptdir = os.path.dirname(os.path.abspath(__file__))
        template_folder=scriptdir + '/templates'
   
        super().__init__(template_folder=template_folder)
        
        self.app.secret_key = 'dev'
        
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        # set default button style and size, will be overwritten by macro parameters
        self.app.config['BOOTSTRAP_BTN_STYLE'] = 'primary'
        self.app.config['BOOTSTRAP_BTN_SIZE'] = 'sm'
        # app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'lumen'  # uncomment this line to test bootswatch theme

        self.db = SQLAlchemy(self.app)
        self.csrf = CSRFProtect(self.app)
        
    def initMessages(self,limit=20):
        '''
        create an initial set of message with the given limit
        
        Args:
            limit(int): the number of messages to create
        '''
        self.db.drop_all()
        self.db.create_all()
        for i in range(limit):
            m = Message(
                text='Test message {}'.format(i+1),
                author='Author {}'.format(i+1),
                category='Category {}'.format(i+1),
                create_time=4321*(i+1)
            )
            if i % 4:
                m.draft = True
            self.db.session.add(m)
        self.db.session.commit()
        
    def flash(self):
        flash('A simple default alert—check it out!')
        flash('A simple primary alert—check it out!', 'primary')
        flash('A simple secondary alert—check it out!', 'secondary')
        flash('A simple success alert—check it out!', 'success')
        flash('A simple danger alert—check it out!', 'danger')
        flash('A simple warning alert—check it out!', 'warning')
        flash('A simple info alert—check it out!', 'info')
        flash('A simple light alert—check it out!', 'light')
        flash('A simple dark alert—check it out!', 'dark')
        flash(Markup('A simple success alert with <a href="#" class="alert-link">an example link</a>. Give it a click if you like.'), 'success')
        return render_template('flash.html')       
    
    def form(self):
        form = HelloForm()
        return render_template('form.html', form=form, telephone_form=TelephoneForm(), contact_form=ContactForm(), im_form=IMForm(), button_form=ButtonForm(), example_form=ExampleForm())
    
    def home(self):
        return render_template('index.html')
    
    def icon(self):
        return render_template('icon.html')

    def messag_delete(self,message_id):    
        message = Message.query.get(message_id)
        if message:
            db.session.delete(message)
            db.session.commit()
            return f'Message {message_id} has been deleted. Return to <a href="/table">table</a>.'
        return f'Message {message_id} did not exist and could therefore not be deleted. Return to <a href="/table">table</a>.'
 
    def message_edit(self,message_id):
        message = Message.query.get(message_id)
        if message:
            message.draft = not message.draft
            db.session.commit()
            return f'Message {message_id} has been edited by toggling draft status. Return to <a href="/table">table</a>.'
        return f'Message {message_id} did not exist and could therefore not be edited. Return to <a href="/table">table</a>.'

    def message_view(self,message_id):   
        message = Message.query.get(message_id)
        if message:
            return f'Viewing {message_id} with text "{message.text}". Return to <a href="/table">table</a>.'
        return f'Could not view message {message_id} as it does not exist. Return to <a href="/table">table</a>.'

    def nav(self):
        return render_template('nav.html')
  
    def pagination(self):
        '''
        pagination example
        
        Returns:
            rendered html for pagination
        '''
        self.initMessages(100)
        page = request.args.get('page', 1, type=int)
        pagination = Message.query.paginate(page, per_page=10)
        messages = pagination.items
        return render_template('pagination.html', pagination=pagination, messages=messages)

    def static(self):
        return render_template('static.html')
    
    def table(self):
        page = request.args.get('page', 1, type=int)
        pagination = Message.query.paginate(page, per_page=10)
        messages = pagination.items
        titles = [('id', '#'), ('text', 'Message'), ('author', 'Author'), ('category', 'Category'), ('draft', 'Draft'), ('create_time', 'Create Time')]
        return render_template('table.html', messages=messages, titles=titles)

    def widgets(self):
        '''
        test widgets 
        '''
        widgetList=[
            [
                Link("https://github.com/WolfgangFahl/pyFlaskBootstrap4","pyFlaskBootstrap4","Extended Flask + Bootstrap4 Library"),
                Link("http://wiki.bitplan.com/index.php/PyFlaskBootstrap4","Wiki","pyFlaskBootstrap4 wiki"),
                Link("https://github.com/greyli/bootstrap-flask","bootstrap-flask","Flask + Bootstrap4 Library by Grey Li"),
                Link("https://palletsprojects.com/p/flask/","flask","web application framework"),
                Link("https://getbootstrap.com/","bootstrap","Open source web toolkit")
            ],
            [
                Image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Tux.svg/299px-Tux.svg.png",alt="Tux",height=150,title='Tux - the Linux kernel penguin mascot'),
                Image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Eiffel_Tower_Paris.jpg/180px-Eiffel_Tower_Paris.jpg",alt="Eiffel Tower",height=150,title='Eiffel Tower, Paris'),
                Image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Croce-Mozart-Detail.jpg/185px-Croce-Mozart-Detail.jpg",alt="Mozart",height=150,title='Wolfgang Amadeus Mozart'),
                Image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/The_Blue_Marble.jpg/240px-The_Blue_Marble.jpg",alt="Earth",width=150,title='Earth as seen from Apollo 17 mission')
            ],    
            [
                Icon("award"),Icon("battery"),Icon("book"),Icon("heart"),
                Icon("calculator",size=48),Icon("person",size=48,color='red'),
                Icon("wifi",size=64),Icon("wrench",size=64)
            ]    
        ]
        return render_template('widgets.html',widgetList=widgetList)
    
# initialization of flask globals
# we can't help that these are needed and can't be wrapped
ea=ExampleApp()
app=ea.app 
db=ea.db

# since db.Model needs to be global the Message class is defined here
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    draft = db.Column(db.Boolean, default=False, nullable=False)
    create_time = db.Column(db.Integer, nullable=False, unique=True)

#
# setup the RESTFUL routes for this application
#

@app.route('/')
def index():
    return ea.home()

@app.route('/form', methods=['GET', 'POST'])
def test_form():
    return ea.form()

@app.route('/nav', methods=['GET', 'POST'])
def test_nav():
    return ea.nav()

@app.route('/pagination', methods=['GET', 'POST'])
def test_pagination():
    return ea.pagination()

@app.route('/static', methods=['GET', 'POST'])
def test_static():
    return ea.static()

@app.route('/flash', methods=['GET', 'POST'])
def test_flash():
    return ea.flash()

@app.before_first_request
def before_first_request_func():
    ea.initMessages()

@app.route('/table')
def test_table():
    return ea.table()

@app.route('/table/<message_id>/view')
def view_message(message_id):
    return ea.message_view(message_id)

@app.route('/table/<message_id>/edit')
def edit_message(message_id):
    return ea.message_edit(message_id)
  
@app.route('/table/<message_id>/delete', methods=['POST'])
def delete_message(message_id):
    return ea.message_delte(message_id)

@app.route('/icon')
def test_icon():
    return ea.icon()

@app.route('/widgets')
def test_widgets():
    return ea.widgets()


#
#  Command line entry point
#
if __name__ == '__main__':
    parser=ea.getParser("Flask + Bootstrap4 demo application for bootstrap-flask")
    args=parser.parse_args()
    # allow remote debugging if specified so on command line
    ea.optionalDebug(args)
    ea.run(args)
 