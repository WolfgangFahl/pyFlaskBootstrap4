from setuptools import setup
import os
from collections import OrderedDict

try:
    long_description = ""
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()

except:
    print('Curr dir:', os.getcwd())
    long_description = open('../../README.md').read()

setup(name='pyFlaskBootstrap4',
      version='0.4.0',
      description='python flask + Bootstrap 4 static components and templates for webprojects',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/WolfgangFahl/pyFlaskBootstrap4',
      download_url='https://github.com/WolfgangFahl/pyFlaskBootstrap4',
      author='Wolfgang Fahl',
      author_email='wf@bitplan.com',
      license='Apache',
      project_urls=OrderedDict(
        (
            ("Documentation", "http://wiki.bitplan.com/index.php/pyFlaskBootstrap4"),
            ("Code", "https://github.com/WolfgangFahl/pyFlaskBootstrap4"),
            ("Issue tracker", "https://github.com/WolfgangFahl/pyFlaskBootstrap4/issues"),
        )
      ),
      classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9'
      ],
      packages=['fb4'],
      package_data={
          'fb4': ['templates/sse/*.html','templates/fb4common/*.html'],
      },
      install_requires=[
          'Bootstrap-Flask~=1.8.0',
          'Flask-Dropzone~=1.6.0',	
          'Flask~=2.02',
          'Flask-HTTPAuth~=4.5.0',
          'Flask-Login~=0.5.0',
          'Flask-SQLAlchemy~=2.5.1',
          'Flask-WTF~=1.0.0',
          'WTForms~=3.0.0',
          'SQLAlchemy-Utils',
          'requests',
          'pydevd',
          'pyDispatcher',
          'APScheduler~=3.8.1'
      ],
      zip_safe=False)
