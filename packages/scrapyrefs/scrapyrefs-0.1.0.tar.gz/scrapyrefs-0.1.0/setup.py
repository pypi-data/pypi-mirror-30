#!/usr/bin/env python
from setuptools import setup, find_packages

from scrapyrefs import VERSION

test_requires = []

install_requires = [
    'lxml'
]

setup(
    name="scrapyrefs",
    version=VERSION,
    description="Library that implements the endpoints of the Crossref API",
    author="Erudit",
    author_email="fabio.batalha@erudit.org",
    maintainer="Fabio Batalha",
    maintainer_email="fabio.batalha@erudit.org",
    url="http://github.com/erudit/scrapyrefs",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
    dependency_links=[],
    tests_require=test_requires,
    test_suite='tests',
    install_requires=install_requires,
    entry_points="""
    [console_scripts]
    scrapyrefs=scrapyrefs.scrapyrefs:main
    """
)
