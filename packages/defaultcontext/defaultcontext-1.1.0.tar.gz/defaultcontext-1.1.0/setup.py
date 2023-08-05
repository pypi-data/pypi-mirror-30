from os import path
from codecs import open
from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name = "defaultcontext",
    version = "1.1.0",
    author = "Bogdan Kulynych",
    author_email = "hello@bogdankulynych.me",
    description = "Tiny util for creating tensorflow-like context managers for default instances of classes",
    url = "https://github.com/bogdan-kulynych/defaultcontext",
    license = "MIT",
    keywords = "utils",
    packages=find_packages(exclude=["tests"]),
    long_description=long_description,
    classifiers=[
	"Development Status :: 5 - Production/Stable",
	"Intended Audience :: Developers",
	"Natural Language :: English",
	"License :: OSI Approved :: MIT License",
	"Operating System :: OS Independent",
	"Programming Language :: Python",
	"Programming Language :: Python :: 2",
	"Programming Language :: Python :: 2.7",
	"Programming Language :: Python :: 3",
	"Programming Language :: Python :: 3.4",
	"Programming Language :: Python :: 3.5",
	"Programming Language :: Python :: 3.6",
	"Programming Language :: Python :: 3.7",
	"Programming Language :: Python :: Implementation :: CPython",
	"Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
