from setuptools import setup, find_packages
from os.path import join, dirname


setup(
    name='Grebla',
    version="1.0",
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    install_requires=[
        "grab==0.6.38",
        "PyYAML==3.12",
        "validators==0.12.1"
    ],
    entry_points={
        'console_scripts':
            ['gb = Grebla.start:start']
    },
    test_suite='tests',

)