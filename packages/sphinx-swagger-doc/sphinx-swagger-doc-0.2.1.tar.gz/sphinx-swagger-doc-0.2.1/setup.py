import sys
import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='sphinx-swagger-doc',
    version='0.2.1',
    author='Jam Risser',
    author_email='jamrizzi@gmail.com',
    description='Sphinx extension for documenting Swagger 2.0 APIs',
    long_description=read('README.rst'),
    license='MIT',
    keywords='',
    url='https://github.com/jamrizzi/sphinx-swagger-doc',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities'
    ],
    packages=find_packages(),
    install_requires=['sphinx', 'requests', 'requests-file', 'future']
)
