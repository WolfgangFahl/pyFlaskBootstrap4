# -*- coding: utf-8 -*-

from fb4.app import AppWrap
from fb4.login_bp import LoginForm
from fb4.sqldb import db
from fb4.login_bp import LoginBluePrint
from fb4.widgets import Link, Icon,Image
from flask import render_template, request, flash, Markup
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import BooleanField,DateField,DateTimeField,FieldList, FileField, \
    FloatField,FormField,IntegerField, RadioField, SelectField,  SelectMultipleField,\
     StringField, SubmitField,  TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length
from sqlalchemy import Column
import sqlalchemy.types as types
import os
import http.client
import re
import time
from sqlalchemy.ext.hybrid import hybrid_property

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

class ButtonForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField()
    delete = SubmitField()
    cancel = SubmitField()

class TelephoneForm(FlaskForm):
    country_code = IntegerField('Country Code')
    area_code = IntegerField('Area Code/Exchange')
    number = StringField('Number')

class IMForm(FlaskForm):
    protocol = SelectField(choices=[('aim', 'AIM'), ('msn', 'MSN')])
    username = StringField()


class ContactForm(FlaskForm):
    first_name = StringField()
    last_name = StringField()
    mobile_phone = FormField(TelephoneForm)
    office_phone = FormField(TelephoneForm)
    emails = FieldList(StringField("Email"), min_entries=3)
    im_accounts = FieldList(FormField(IMForm), min_entries=2)
    
class PingForm(FlaskForm):
    host=SelectField(choices=[('facebook','www.facebook.com'),
        ('google','www.google.com'),
        ('IBM','www.ibm.com'),
        ('twitter','www.twitter.com'),
        ],
        #https://stackoverflow.com/a/38157356/1497139
        render_kw={"onchange":"this.form.submit()"}
    )
    pingState=StringField('ping state')
    
class IconSearchForm(FlaskForm):
    search=StringField('search', render_kw={"onchange":"this.form.submit()"})
    perPage=SelectField(choices=[('twenty','20'),
        ('fifty','50'),
        ('hundred','100'),
        ('twohundred','200'),
        ('all','all'),
        ],
        #https://stackoverflow.com/a/38157356/1497139
        render_kw={"onchange":"this.form.submit()"}
    )
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

        db.init_app(self.app)
        self.db=db
        self.csrf = CSRFProtect(self.app)
        self.loginBluePrint=LoginBluePrint(self.app,'login')
        self.loginBluePrint.hint="'try user: scott, password: tiger2021'"
        app=self.app
        
        #
        # setup global handlers
        #
        @app.before_first_request
        def before_first_request_func():
            self.initDB()
        
        #
        # setup the RESTFUL routes for this application
        #
        @app.route('/')
        def index():
            return self.home()
        
        @app.route('/form', methods=['GET', 'POST'])
        def test_form():
            return self.form()
        
        @app.route('/nav', methods=['GET', 'POST'])
        def test_nav():
            return self.nav()
        
        @app.route('/pagination', methods=['GET', 'POST'])
        def test_pagination():
            return self.pagination()
        
        @app.route('/static', methods=['GET', 'POST'])
        def test_static():
            return self.static()
        
        @app.route('/flash', methods=['GET', 'POST'])
        def test_flash():
            return self.flash()
        
        @app.route('/datatable')
        def test_datatable():
            return self.datatable()
        
        @app.route('/table')
        def test_table():
            return self.table()
        
        @app.route('/table/<message_id>/view')
        def view_message(message_id):
            return self.message_view(message_id)
        
        @app.route('/table/<message_id>/edit')
        def edit_message(message_id):
            return self.message_edit(message_id)
          
        @app.route('/table/<message_id>/delete', methods=['POST'])
        def delete_message(message_id):
            return self.message_delete(message_id)
        
        @app.route('/icon')
        def test_icon():
            return self.icon()
        
        @app.route('/widgets')
        def test_widgets():
            return self.widgets()
        
        @app.route('/ping',methods=['GET', 'POST'])
        def test_ping():
            return self.ping()
        
    def initDB(self,limit=20):
        '''
        initialize the database
        '''
        self.db.drop_all()
        self.db.create_all()
        self.initUsers()
        self.initMessages(limit)
        self.initIcons()
        
    def initUsers(self):
        self.loginBluePrint.addUser(self.db,"scott","tiger2021",userid=100)
        
    def initMessages(self,limit=20):
        '''
        create an initial set of message with the given limit
        Args:
            limit(int): the number of messages to create
        '''
        
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
        
    def initIcons(self):
        '''
        initialize the icons
        '''
        iconNames=Icon.getBootstrapIconsNames()
        for index,iconName in enumerate(iconNames):
            bootstrapIcon=BootstrapIcon(id=iconName,index=index+1)
            self.db.session.add(bootstrapIcon)
        self.db.session.commit()
        
    def getDisplayIcons(self,icons):
        displayIcons=[]
        for icon in icons:
            displayIcons.append("%04d%s%s" % (icon.index,icon.icon,icon.link))
        return displayIcons
            
    def pagePing(self,host, path="/"):
        """ This function retrieves the status code of a website by requesting
            HEAD data from the host. This means that it only requests the headers.
            If the host cannot be reached or something else goes wrong, it returns
            False.
            
            see https://stackoverflow.com/a/1949507/1497139
        """
        startTime=time.time()
        try:
            conn = http.client.HTTPConnection(host)
            conn.request("HEAD", path)
            if re.match("^[23]\d\d$", str(conn.getresponse().status)):
                state=True
        except Exception:
            state=False
        elapsed=time.time()-startTime    
        return state,elapsed
                
        
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
        form = LoginForm()
        return render_template('form.html', form=form, telephone_form=TelephoneForm(), contact_form=ContactForm(), im_form=IMForm(), button_form=ButtonForm(), example_form=ExampleForm())
    
    def home(self):
        return render_template('index.html')
    
    def icon(self):
        return render_template('icon.html')

    def message_delete(self,message_id):    
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
        search_form=IconSearchForm()
        perPageChoice=search_form.perPage.data    
        if perPageChoice is None:
            perPageChoice="twenty"
        choices=dict(search_form.perPage.choices)
        perPageSelection=choices[perPageChoice]
        search_form.perPage.data=perPageChoice
        if perPageChoice=="all":
            per_page=2000
        else:    
            per_page=int(perPageSelection)    
        pagination=None
        icons=None
        if search_form.validate_on_submit() and search_form.search.data:
            search="%{}%".format(search_form.search.data)
            print("searching %s: " % search)
            icons = BootstrapIcon.query.filter(BootstrapIcon.id.like(search)).all()
        if icons is None:
            page = request.args.get('page', 1, type=int)
            pagination = BootstrapIcon.query.paginate(page, per_page=per_page)
            icons = pagination.items
        displayIcons=self.getDisplayIcons(icons)
        return render_template('pagination.html', form=search_form,pagination=pagination, icons=displayIcons)

    def ping(self):
        '''
        ping test
        '''
        ping_form=PingForm()
        if ping_form.validate_on_submit():
            choices=dict(ping_form.host.choices)
            host=choices[ping_form.host.data]
            state,pingTime=self.pagePing(host)
            pingState="%s %5.0f ms" % ("✅" if state else "❌",pingTime*1000)
            ping_form.pingState.data=pingState
            pass
        else:
            ping_form.pingState=""
        return render_template('ping.html',ping_form=ping_form)
    
    def static(self):
        '''
        test static content
        '''
        return render_template('static.html')
    
    def datatable(self):
        '''
        test data table
        '''
        icons=BootstrapIcon.query.all()
        dictList=[]
        for icon in icons:
            dictList.append(icon.asDict())
        return render_template('datatable.html',listOfDicts=dictList)
    
    def table(self):
        '''
        test table
        '''
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

# since db.Model needs to be global the Message class is defined here
class Message(db.Model):
    id = Column(types.Integer, primary_key=True)
    text = Column(types.Text, nullable=False)
    author = Column(types.String(100), nullable=False)
    category = Column(types.String(100), nullable=False)
    draft = Column(types.Boolean, default=False, nullable=False)
    create_time = Column(types.Integer, nullable=False, unique=True)
    
# wget https://raw.githubusercontent.com/twbs/icons/main/bootstrap-icons.svg    
# xq .svg bootstrap-icons.svg | grep -v http | sed 's/@//' | jq .symbol[].id | cut -d'"' -f2  | awk ' { if ( length > x ) { x = length; y = $0 } }END{ print y; print x }'
# file-earmark-spreadsheet-fill
# 29
class BootstrapIcon(db.Model):
    id=Column(types.String(30), primary_key=True)
    index=Column(types.Integer)
    
    @hybrid_property
    def url(self):
        myUrl="https://icons.getbootstrap.com/icons/%s/" % self.id
        return myUrl
    
    @hybrid_property
    def link(self):
        myLink=Link(self.url,self.id)
        return myLink
    
    @hybrid_property
    def icon(self):
        myIcon=Icon(self.id)
        myIcon.userdata['#']=self.index
        return myIcon
    
    def asDict(self):
        myDict={
            'link': self.link,
            'icon': self.icon
        }
        return myDict
         
#
#  Command line entry point
#
if __name__ == '__main__':
    ea=ExampleApp()
    parser=ea.getParser("Flask + Bootstrap4 demo application for bootstrap-flask")
    args=parser.parse_args()
    # allow remote debugging if specified so on command line
    ea.optionalDebug(args)
    ea.run(args)