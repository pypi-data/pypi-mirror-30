"""
Flask-RouteBuilder
-------------
A simple automatic route builder for flask 
"""
from setuptools import setup


setup(
    name='Flask-RouteBuilder',
    version='0.5',
    url='https://github.com/apecnascimento/Flask-RouterBuilder',
    license='MIT',
    author='apecnascimento',
    author_email='apecnascimento@gmail.com',
    description='Blueprint route builder for flask',
    long_description=__doc__,
    py_modules=['flask_route_builder'],
    include_package_data=True, 
    zip_safe=False,     
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)