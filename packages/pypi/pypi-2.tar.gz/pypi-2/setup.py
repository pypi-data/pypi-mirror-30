#! /usr/bin/env python
#
# $Id$

from distutils.core import setup

# perform the setup action
setup(
    name = "pypi",
    version = '2',
    description = "PyPI is the Python Package Index at http://pypi.org/",
    author = "Warehouse Maintainers",
    author_email = 'richard@python.org',
    url = 'http://wiki.python.org/moin/CheeseShopDev',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],
)

# vim: set filetype=python ts=4 sw=4 et si
