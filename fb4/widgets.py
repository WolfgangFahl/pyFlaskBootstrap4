'''
Created on 2021-01-04

@author: wf
'''
import re
import uuid

from flask import render_template_string, request, Markup
import os
import site
import jinja2
from xml.dom import minidom

from wtforms import FileField, StringField
from wtforms.widgets import html_params


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
        self.addClass("nav-item")
        # https://www.tutorialrepublic.com/twitter-bootstrap-tutorial/bootstrap-dropdowns.php
        self.template="""
    <a href="#" class="nav-link dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">"""+self.title+"""</a>
    <div class="dropdown-menu">
{% if menuItemList %}{% for menuItem in menuItemList %}{{ menuItem|safe }}{% endfor %}{% endif %}
    </div>
"""
        pass
        
    def addItem(self,item:MenuItem):
        item.addClass("dropdown-item")
        super().addItem(item)


class LodTable(Widget):
    """Converts a LOD to a HTML table"""

    def __init__(self, lod: list, headers: dict = None,name=None, indent="", isDatatable:bool=False):
        """

        Args:
            lod:
            headers: mapping form dict keys to the corresponding headers. If none the dict keys will be used instead
            isDatatable(bool): If true the table will be rendered as a datatable
            name: name of the table str or Markup that is placed above the table
        """
        super(LodTable, self).__init__(indent=indent)
        self.lod = lod
        if headers is None and self.lod:
            headers = {h: h for h in {key for record in lod for key in list(record.keys())}}
        self.headers = headers
        self.isDatatable=isDatatable
        self.id = str(uuid.uuid1())
        self.name=name

    def render(self):
        """renders the lod as table"""
        if not self.lod:
            return ""
        if isinstance(self.name, Markup):
            name=self.name
        else:
            name=Markup(f"<h2>{self.name}</h2>")
        headers = "\n".join([f'<th scope="col">{col}</th>' for col in self.headers.values()])
        rows = []
        for d in self.lod:
            cells = []
            for col in self.headers.keys():
                cellValue = d.get(col)
                cellValue = cellValue if cellValue else ""
                cells.append(f"<td>{cellValue}</td>")
            rows.append("<tr>\n" + "\n".join(cells) + "\n</tr>")
        table = f"""<table id="{self.id}" class="table table-bordered table-hover">
                      <thead class="thead-light">
                        <tr>
                          {headers}
                        </tr>
                      </thead>
                      <tbody>
                        {' '.join(rows)}
                      </tbody>
                    </table>"""
        if self.isDatatable:
            table +=f"""<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.23/css/jquery.dataTables.css">
                        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.23/js/jquery.dataTables.js"></script>
                        <script type="text/javascript">
                        $(document).ready(function() {{
                            $('#{self.id}').DataTable();
                        }});
                        </script>"""
        return name + Markup(table)


class DropZoneField(FileField):
    """
    Mimics the behavior of dropzone.create() and dropzone.config() allowing to define the dropzone inside of an
    flask form.
    """

    def __init__(self, id:str, url:str=None, dzInfoMsg:str=None,uploadId:str="submit", configParams:dict=None, **kwargs):
        """

        Important config params:
           * acceptedFiles: e.g. "image/*,application/pdf,.psd,.ods,.xlsx,text/*"

        Args:
            id: id of the dropzone field
            url(str): target of the action. If used in form the file are submitted wwith the form
            dzInfoMsg(str): Mseeage to be shown as hint how to use the dropzone
            uploadId(str): id of the button that is used to initiate the upload
            configParams(dict): Dropzone configuration. Overwrites the default config. see https://docs.dropzone.dev/configuration/basics/configuration-options
        """
        self.fieldId=id
        super(DropZoneField, self).__init__(render_kw={"id":self.fieldId}, **kwargs)
        if url is None:
            if request:
                url=request.url_rule.rule
        self.url=url
        if dzInfoMsg is None:
            dzInfoMsg="Please drop a file or click to select a file."
        self.dzInfoMsg=dzInfoMsg
        self.uploadId=uploadId
        self.config={
            'url': self.url,
            'createImageThumbnails':True,
            'thumbnailMethod':"contain",
            'thumbnailWidth':"120px",
            'thumbnailHeight':"250px",
            'autoProcessQueue': False,
            'uploadMultiple': True,
            'parallelUploads': 30,
            'paramName': self.id,
            'previewsContainer': f"#{self.fieldId}Field",
            'addRemoveLinks':True,
            'maxFilesize': 5,
            'acceptedFiles': ".ods, .pdf, .xlsx",
            'maxFiles': 30,
            'dictDefaultMessage': "Drop files here or click to upload.",
            'dictFallbackMessage': "Your browser does not support drag'n'drop file uploads.",
            'dictInvalidFileType': "You can't upload files of this type.",
            'dictFileTooBig': "File is too big {{filesize}}. Max filesize: {{maxFilesize}}MiB.",
            'dictResponseError': "Server error: {{statusCode}}",
            'dictMaxFilesExceeded': "You can't upload any more files.",
            'dictCancelUpload': "Cancel upload",
            'dictRemoveFile': "Remove file",
            'dictCancelUploadConfirmation': "You really want to delete this file?",
            'dictUploadCanceled': "Upload canceled",
        }
        if configParams:
            self.updateConfigParams(**configParams)

    def updateConfigParams(self, **configParams):
        """
        Updates the config prams with the given values

        Args:
            configParams(dict): Dropzone configuration. Overwrites the default config. see https://docs.dropzone.dev/configuration/basics/configuration-options

        """
        if configParams:
            for param, value in configParams.items():
                # overwrite default config
                self.config[param] = value

    def process_formdata(self, valuelist):
        """
        If files are submitted they will be put into the data property
        """
        files=[]
        regex = re.compile(fr"({self.config.get('paramName')})(\[\d+\])?")
        for fileName, file in request.files.items():
            if re.match(regex, fileName):
                files.append(file)
        self.data=files

    def jsConfig(self):
        """
        java script clause configuring the dropzone
        """
        configParams={}
        for param, value in self.config.items():
            if isinstance(value, bool):
                if value:
                    configParams[param]="true"
                else:
                    configParams[param]="false"
            elif isinstance(value, str):
                configParams[param] = f'"{value}"'
            else:
                configParams[param] = value
        processedParams=[f'{param}: {value}' for param,value in configParams.items()]
        processedParams.append(f"'headers': {{'X-CSRF-Token': document.getElementById('{self.fieldId}').querySelector('#csrf_token').value }}")
        configParamsStr=r','.join(processedParams)
        thumbnails="""this.on("addedfile", function(file, response) { 
                       var ext = file.name.split('.').pop().toLowerCase(); 
                       if (file.type==='application/pdf') { 
                          this.emit("thumbnail", file, "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/PDF_file_icon.svg/80px-PDF_file_icon.svg.png"); 
                       } else if (file.type==='doc' || ext==='docx') { 
                          this.emit("thumbnail", file, "/img/word.png"); 
                       } else if (file.type==='application/vnd.ms-excel' || file.type==='application/vnd.ms-excel.sheet.macroEnabled.12' || file.type==='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') { 
                          this.emit("thumbnail", file, "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Microsoft_Office_Excel_%282019%E2%80%93present%29.svg/120px-Microsoft_Office_Excel_%282019%E2%80%93present%29.svg.png");
                       }
                       });
                     """
        config=f'''Dropzone.options.{self.fieldId} = {{
                      init: function() {{
                            dz = this;                             
                            document.getElementById('{self.fieldId}').querySelector("#{self.uploadId}").addEventListener("click", function handler(e) {{
                                e.currentTarget.removeEventListener(e.type, handler);
                                e.preventDefault();
                                e.stopPropagation();
                                dz.processQueue();
                            }});
                            this.on("queuecomplete", function(file) {{
                                document.getElementById('{self.fieldId}').querySelector("#{self.uploadId}").click();
                            }});
                            this.on("complete", function(file) {{
                                this.removeFile(file);
                            }});
                            {thumbnails}
                      }},
                       success:function(file, response){{
                            var newDoc = document.open("text/html", "replace");
                            newDoc.write(response);
                            newDoc.close();
                        }},
                      { configParamsStr }
                  }};'''

        return f"<script>{config}</script>"

    def __call__(self, **kwargs):
        """
        renders the dropzone to html
        """
        makeProgresBarTransparent="<style>.dz-progress{background-color:transparent !important;}</style>"  # we only upload on submit → make transparent to show file name
        setClass = f"<script>document.getElementById('{self.fieldId}Field').parentNode.parentNode.classList.add('dropzone');document.getElementById('{self.fieldId}Field').parentNode.parentNode.id='{self.fieldId}';</script>{makeProgresBarTransparent}"
        return Markup(f'<div class="dropzone-previews" id="{self.fieldId}Field" action="submit"></div> <div class="dz-default dz-message" data-dz-message><span>{self.dzInfoMsg}</span></div>') + Markup(setClass) + Markup(self.jsConfig())



class ButtonWidget(object):
    """
    See https://gist.github.com/doobeh/239b1e4586c7425e5114
    Renders a multi-line text area.
    `rows` and `cols` ought to be passed as keyword args when rendering.
    """
    input_type = 'button'

    html_params = staticmethod(html_params)

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        params = self.html_params(name=field.name, **kwargs)
        label = field.label.text
        return Markup(f'<button {params}>{label}</button>')


class ButtonField(StringField):
    widget = ButtonWidget()