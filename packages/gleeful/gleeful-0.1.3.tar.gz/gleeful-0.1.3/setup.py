from setuptools import setup, find_packages
from pathlib import Path


with (Path(__file__).parent / 'README.rst').open() as fp:
    long_description = fp.read()


setup(
    name='gleeful',
    version='0.1.3',
    description='HomeKit Accessory Protocol (HAP) wrapper for Python',
    long_description=long_description,
    url='https://bitbucket.org/schinckel/gleeful/',
    author='Matthew Schinckel',
    author_email='matt@schinckel.net',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=[
        'hap-python',
    ],
)
