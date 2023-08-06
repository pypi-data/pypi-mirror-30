from setuptools import setup
import src

setup(
    name='mcsrv',
    version=src.__version__,
    install_requires=[
        "aioredis",
        "aioamqp",
        "aiopg",
    ],
    description="Package for small service start",
    author='Stepan Pyzhov',
    maintainer='Stepan Pyzhov',
    packages=['mcsrv'],
    package_dir={'mcsrv': 'src'},
)
