import re
import ast

from setuptools import setup, find_packages


_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('profilelog/__init__.py', 'rb') as f:
    __version__ = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='profilelog-middleware',
    version=__version__,
    description="""WSGI middleware for logging profiling data.

Provides profiling results through console.log.""",
    long_description=open('README.md', 'r').read(),
    maintainer="Carlos H. Romano",
    maintainer_email='chromano@gmail.com',
    url="https://github.com/chromano/profilelog",
    packages=find_packages(exclude=["tests"]),
)
