#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

import versioneer


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()

setup(
    name='Cipher-Bot',
    version=versioneer.get_version(),
    license='Apache Software License 2.0',
    description='A multi-platform chat bot framework.',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='John Lage',
    author_email='me@johnlage.com',
    url='https://github.com/johnlage/Cipher',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Communications :: Chat',
        'Topic :: Communications :: Chat :: Internet Relay Chat'
    ],
    keywords=[],
    install_requires=['bottom', 'aiotg', 'discord.py', 'click', 'daiquiri', 'yarl<1.0'],
    dependency_links=['http://github.com/Rapptz/discord.py/tarball/rewrite#egg=discord.py'],
    python_requires='~=3.6',
    extras_require={},
    entry_points={'console_scripts': ['Cipher=Cipher.core.cli:main'],
                  'Cipher.ConnectionTypes': ['tg=Cipher.conns.tg.connection:TGConnection',
                                             'discord_base=Cipher.conns.discord.connection:DiscordBaseConnection',
                                             'discord=Cipher.conns.discord.connection:DiscordConnection',
                                             'irc=Cipher.conns.irc.connection:IRCConnection'],
                  'Cipher.Plugins': ['CipherCore=Cipher.plugins.core:CorePlugin',
                                     'CipherRelay=Cipher.plugins.relay:RelayPlugin']},
    cmdclass=versioneer.get_cmdclass()
)
