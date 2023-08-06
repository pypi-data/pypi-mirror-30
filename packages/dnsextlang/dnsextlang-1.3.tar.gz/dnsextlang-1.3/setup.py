#/usr/bin/env python3
# setup for dnsextlang package

from setuptools import setup, find_packages

setup(
    name="dnsextlang",
    version="1.3",
    packages=['dnsextlang'],
    scripts=['extconvert.py'],
 
    install_requires=['dnspython>=1.10'],

    include_package_data=True,

    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6',
    ],
    # metadata for upload to PyPI
    author="John Levine",
    author_email="johnl@taugh.com",
    description="DNS extension language parser and web form helper",
    long_description="""DNS extension language defined in draft-levine-dnsextlang.
    Can load rrtype descriptions from files or the DNS, parse and deparse blocks of
    rrtypes, create and process HTML forms for rrtypes.""",
    license="BSD",
    keywords="dns rrtypes extensions",
    url="https://www.taugh.com/dnsextlang/"
)