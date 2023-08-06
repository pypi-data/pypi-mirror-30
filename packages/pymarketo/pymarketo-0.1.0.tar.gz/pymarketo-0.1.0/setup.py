from setuptools import setup, find_packages

import os
import sys


# Don't import analytics-python module here, since deps may not be installed
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pymarketo'))

# python setup.py register -r pypi
# python setup.py sdist upload -r pypi

long_description = '''
PyMarketo is a Python3.x client that wraps the MarketoRestPython project to provide a human friendly module and add bulk export capability.
'''

setup(
    name='pymarketo',
    version='0.1.0',
    description='Python Client for the Marketo REST API',
    url='https://github.com/osamakhn/pymarketo',
    author='Osama Khan',
    author_email='osamakhn@gmail.com',
    license='MIT License',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'requests',
        'marketorestpython'
    ],
    long_description=long_description,
    keywords='Marketo REST API Wrapper Client',
    classifier=['Intended Audience :: Developers',
                'Programming Language :: Python :: 3'],
    project_urls={
        'Source': 'https://www.github.com/osamakhn/pymarketo'
    }
)
