import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "dostack",
    version = "0.5.4",
    author = "Rikki Guy @ MHN",
    author_email = "r.guy@mhnltd.co.uk",
    description = "A tool to build/help deploy docker containers. Make for docker.",
    license = "Copyright MHN Ltd",
    keywords = "docker build deploy container",
    long_description=read('README.md'),
    py_modules=['dobuild', 'dostack', 'dotempl', 'doutils'],
    install_requires=[
        'click==6.7',
        'Jinja2==2.9.6',
        'PyYAML==3.12',
        'sh==1.12.13',
    ],
    entry_points={
        'console_scripts': [
            'dobuild=dobuild:main',
            'dotempl=dotempl:dotempl',
            'dostack=dostack:dostack',
        ]
    }
)
