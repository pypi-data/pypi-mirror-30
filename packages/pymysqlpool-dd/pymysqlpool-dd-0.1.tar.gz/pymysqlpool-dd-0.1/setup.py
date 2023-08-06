import os
from setuptools import setup, find_packages


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

setup(
    name='pymysqlpool-dd',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/waipbmtd/pymysqlpool',
    license='MIT',
    author='Devin',
    author_email='waipbmtd@gmail.com',
    requires=['pymysql'],
    description='MySQL connection pool utility.',
)