import mimetypes
import os
from typing import Callable

from flask import Blueprint, send_file
from markupsafe import Markup


class IconsBlueprint(object):
    """
    a blueprint for bootstrap icon assets
    https://icons.getbootstrap.com/#icons
    """

    def __init__(self, app, name:str, template_folder: str = None, appWrap=None):
        '''
        construct me

        Args:
            app: flask application
            name: name of the blueprint module
            template_folder(str): the template folder
        '''
        self.name = name
        if template_folder is not None:
            self.template_folder = template_folder
        else:
            self.template_folder = 'templates'
        self.blueprint = Blueprint(name, __name__, template_folder=self.template_folder)
        self.app = app
        self.appWrap=appWrap
        self.bootstrapIconsPath=os.path.join('bootstrap-icons', 'bootstrap-icons-1.7.2')
        app.register_blueprint(self.blueprint)

        @app.route('/assets/css/<css>', methods=['GET',])
        def getCss(css: str):
            return self.sendFile(os.path.join("bootstrap", "css", css))

        @app.route('/assets/img/<icon>', methods=['GET'])
        def getIcon(icon:str):
            return self.sendFile(os.path.join(self.bootstrapIconsPath, icon))

        @app.route('/assets/img/fonts/<font>', methods=['GET'])
        def getFont(font: str):
            return self.sendFile(os.path.join(self.bootstrapIconsPath, "fonts", font))

    def sendFile(self, file:str):
        """
        send the given file from the bootstrap icons folder
        """
        scriptdir = os.path.dirname(os.path.abspath(__file__))
        template_folder = os.path.join(scriptdir, '..', 'web')
        icon_path = os.path.join(template_folder, file)
        if os.path.isfile(icon_path):
            mimetype = mimetypes.guess_type(icon_path)[0]
            return send_file(icon_path, mimetype=mimetype)

    def loadBootstrapIconCSS(self):
        url="/assets/img/bootstrap-icons.css"
        if hasattr(self.appWrap, "basedUrl") and isinstance(self.appWrap.basedUrl, Callable):
            url=self.appWrap.basedUrl(url)
        return Markup(f'<link rel="stylesheet" href="{url}">')