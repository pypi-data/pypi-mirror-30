from setuptools import setup, find_packages
from os import path
from rancher_autobackup import VERSION

here = path.abspath(path.dirname(__file__))

setup(
    name='rancher_autobackup',
    version=VERSION,
    packages=['rancher_autobackup'],
    url='https://github.com/oscarsix/rancher_autobackup',
    license='MIT',
    author='Oskar Malnowicz',
    author_email='oscarsix@protonmail.ch',
    description='Rancher stack backups to git repository',
    scripts=['bin/rancher-autobackup'],
    python_requires='>=3.6',
    install_requires=['requests'],
)
