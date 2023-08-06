from setuptools import setup, find_packages
from os import path
import mtchecker
# from distutils.core import setup

setup(
    name='mtchecker',
    version=mtchecker.__version__,
    py_modules=['mtchecker'],
    install_requires=[
        'scapy',
        'ujson',
        'requests',
        'SpoofMAC',
    ],
    packages=find_packages(),
    long_description=open(path.join(path.dirname(__file__), 'README.md')).read(),
    entry_points='''
        [console_scripts]
        mtchecker=mtchecker.mtchecker:run_app
    ''',

)

# python setup.py register sdist upload
