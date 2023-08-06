import os

from distutils.core import setup


def read(file):
    """ Utility function to read file. """
    return open(os.path.join(os.path.dirname(__file__), file)).read()


setup(
    name='pyvarnish',
    version='1.0.1',
    long_description=read('README.md'),
    description='Lighweight Python interface for Varnish Manager',
    author='Sergio Andres Virviescas Santana',
    author_email='developersavsgio@gmail.com',
    url='https://github.com/savsgio/pyvarnish',
    py_modules=['pyvarnish'],
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Programming Language :: Python',
                 'Topic :: Utilities'],

)
