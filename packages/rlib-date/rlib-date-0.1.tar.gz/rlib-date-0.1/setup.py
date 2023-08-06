# rdate: Alternative to standard datetime library.
# Copyright: (c) 2018, t5w5h5@gmail.com. All rights reserved.
# License: MIT, see LICENSE for details.

import codecs
import os
from setuptools import setup, Command


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -vrf ./build ./dist ./*.egg-info')


def read_file(filename):
    """Read a utf8 encoded text file and return its contents."""
    with codecs.open(filename, 'r', 'utf8') as f:
        return f.read()


setup(
    name='rlib-date',
    packages=['rdate'],
    version='0.1',
    description='Alternative to standard datetime library.',
    long_description=read_file('README.rst'),
    author='t5w5h5',
    author_email='t5w5h5@gmail.com',
    url='https://github.com/t5w5h5/rdate',
    download_url = 'https://github.com/t5w5h5/rdate/archive/0.1.tar.gz',
    keywords=['date', 'time', 'datetime'],
    license='MIT',
    platforms='any',
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    cmdclass={'clean': CleanCommand}
)
