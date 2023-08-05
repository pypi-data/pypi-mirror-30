from setuptools import setup

setup(
    name='arkdbtools',
    version='0.2.17',
    ext_packages='arky<1',
    packages=['arkdbtools', 'arkdbtools.tests'],
    url='https://github.com/BlockHub/arkdbtools',
    license='MIT',
    author='karel',
    author_email='karel@blockhub.nl',
    description='toolkit for dealing with the ark blockchain'
)
