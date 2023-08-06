import re
import ast
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')


setup(
    name='plonecli-click',
    author='Maik Derstappen',
    author_email='md@derico.de',
    version="7.0.dev0",
    url='https://github.com/MrTango/click',
    packages=['click'],
    description='A simple wrapper around optparse for '
                'powerful command line utilities.',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
