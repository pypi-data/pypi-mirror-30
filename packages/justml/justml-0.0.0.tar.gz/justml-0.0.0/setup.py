from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

long_description = "JustML client library"

setup(
    name='justml',
    version='0.0.0',
    description='JustML client library',
    long_description=long_description,
    url='http://justml.io',
    author='JustML',
    author_email='contact@justml.io',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='justml ml machinelearning datascience',
    packages=find_packages(exclude=[]),
    install_requires=[]
)
