# -*- coding: utf-8 -*-
#
# Copyright 2016 - 2018, Ternaris and the MARV contributors.
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import absolute_import, division, print_function

import os
import sys

from setuptools import setup


HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'README.rst')) as f:
    README = f.read()


STATIC = os.path.join(os.path.abspath(os.curdir), 'marv_ludwig', 'static')
if not os.path.isdir(STATIC):
    print('ERROR: Ludwig needs to be built and placed at {}'.format(STATIC),
          file=sys.stderr)
    sys.exit(1)


setup(name='marv-ludwig',
      version='3.3.1',
      description='MARV Robotics web frontend bundle',
      long_description=README,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          "Framework :: Flask",
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Operating System :: POSIX :: Linux',  # for now
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 2 :: Only',  # for now
          'Programming Language :: Python :: Implementation :: CPython',  # for now
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
          'Topic :: Scientific/Engineering',
      ],
      author='Ternaris',
      author_email='team@ternaris.com',
      url='https://ternaris.com/marv-robotics',
      license='AGPL-3.0-only',
      packages=[
          'marv_ludwig',
      ],
      include_package_data=True,
      zip_safe=False)
