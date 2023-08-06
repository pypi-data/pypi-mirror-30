#!/usr/bin/env python

from setuptools import setup

setup(name='menuplaceholder',
    version='0.0.1.2',
    description='Placeholder items for Mezzanine menus.',
    author='Peter Murphy',
    author_email='peterkmurphy@gmail.com',
#    url='http://pypi.python.org/pypi/glyphviewer/',
    packages=['menuplaceholder'],
    package_data={
        'menuplaceholder': ['templates/*.html', 'templates/**/*.html'],
    },
#    keywords = 'font glyph web woff ttf otf TrueType OpenType Django',
    license='LICENSE.txt',
    classifiers = [
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        ],
    long_description=open('README.rst').read(),
    install_requires = ["Django >= 1.0", "Mezzanine >= 4.0"],
    zip_safe = False,
)
