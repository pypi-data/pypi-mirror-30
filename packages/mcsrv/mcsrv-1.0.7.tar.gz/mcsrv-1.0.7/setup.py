from setuptools import setup

setup(
    name='mcsrv',
    version='1.0.7',
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
    url='https://github.com/Turin-tomsk/mcsrv',
)
