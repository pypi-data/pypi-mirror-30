# coding=utf-8

# Copyright (C) 2017, Alexandre Vaissière
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
# OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
from setuptools import setup, find_packages

import oathguardian

ICON_SIZES = (16, 32, 48, 64, 96, 128, 192, 256, 512)

data_files = []
data_files += [('share/icons/hicolor/{size}x{size}/apps'.format(size=s),
                ['data/icons/{size}/oathguardian.png'.format(size=s)])
               for s in ICON_SIZES]
data_files += [('share/icons/hicolor/scalable/apps', ['data/oathguardian.svg'])]
data_files += [('share/applications', ['data/oathguardian.desktop'])]

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=oathguardian.NAME,
    version=oathguardian.VERSION,
    description=oathguardian.DESCRIPTION,
    license=oathguardian.LICENSE_NAME,
    url=oathguardian.URL,

    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Alexandre Vaissière',
    author_email='avaiss@fmiw.org',

    python_requires='~=3.5',
    keywords='totp authenticator oath gtk one-time-password',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: GTK",
        "Environment :: X11 Applications :: Gnome",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities",
    ],

    packages=find_packages(exclude=['tests']),
    package_dir={'': '.'},
    package_data={
        'oathguardian.gtkui': ['oathguardian.xml', 'oathguardian_menu.xml'],
    },
    include_package_data=True,

    data_files=data_files,

    install_requires=['pyzbar>=0.1.4', 'yubikey-manager>=0.6.0', 'secretstorage>=2.3.1'],

    setup_requires=['nose==1.3.7'],

    entry_points={
        'console_scripts': [
        ],
        'gui_scripts': [
            'oathguardian-gtk = oathguardian.gtkui.__main__:main',
        ]
    },
)
