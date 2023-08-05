#!/usr/bin/env python

from distutils.core import setup
import sys

import joblib

# For some commands, use setuptools
if len(set(('develop', 'sdist', 'release', 'bdist', 'bdist_egg', 'bdist_dumb',
            'bdist_rpm', 'bdist_wheel', 'bdist_wininst', 'install_egg_info',
            'egg_info', 'easy_install', 'upload',
            )).intersection(sys.argv)) > 0:
    import setuptools

extra_setuptools_args = {}


if __name__ == '__main__':
    setup(name='clearn',
          version='0.0.0',
          author='Gael Varoquaux',
          author_email='gael.varoquaux@normalesup.org',
          packages=['clearn', ],
          **extra_setuptools_args)
