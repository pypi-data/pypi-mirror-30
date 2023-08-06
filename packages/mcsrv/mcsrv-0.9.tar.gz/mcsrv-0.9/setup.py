from setuptools import setup
from os.path import join, dirname
import src

setup(
    name='mcsrv',
    version=src.__version__,
    install_requires=open(join(dirname(__file__), 'requirements.txt')).readlines(),
    description="Package for small service start",
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    author='Stepan Pyzhov',
    maintainer='Stepan Pyzhov',
    packages=['mcsrv'],
    package_dir={'mcsrv': 'src'},
)
