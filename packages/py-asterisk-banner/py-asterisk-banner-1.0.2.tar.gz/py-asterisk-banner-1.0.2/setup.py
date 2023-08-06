# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from sys import platform
import os


def read(file):
    """ Utility function to read file. """
    return open(os.path.join(os.path.dirname(__file__), file)).read()


setup(
    name='py-asterisk-banner',
    version='1.0.2',
    description='Baneador de IPs en Asterisk con soporte para SIP y PJSIP',
    long_description=read('README.md'),
    author='Sergio Andres Virviescas Santana',
    author_email='developersavsgio@gmail.com',
    url='https://github.com/savsgio/py-asterisk-banner.git',
    license='GPL',
    packages=find_packages(),
    # include_package_data=True,
    data_files=[
        ('/etc', ['etc/pjsipcheck.conf']),
        ('/etc/init.d', ['init.d/pjsipcheckd']),
        ('pjsipcheck/templates/', [
            'pjsipcheck/templates/block_email.html',
            'pjsipcheck/templates/block_email.txt',
        ]),
        ('pjsipcheck', ['README.md']),
    ],
    scripts=['bin/pjsipcheck'],
    install_requires=['Jinja2'],
    zip_safe=False,
    classifiers=['Development Status :: 7 - Inactive',
                 'Programming Language :: Python :: 3',
                 'Topic :: Utilities'],
)

# update-rc
if platform == "linux" or platform == "linux2":
    os.system('cd /etc/init.d && update-rc.d pjsipcheckd defaults')
elif platform == "darwin":
    pass
elif platform == "win32":
    pass
else:
    pass
