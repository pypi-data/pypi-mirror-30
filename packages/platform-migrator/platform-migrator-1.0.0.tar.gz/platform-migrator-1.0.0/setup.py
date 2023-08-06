"""
Setup script for the library
"""

from codecs import open
import os
import platform
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

if platform.system() == 'Windows':
    home = os.getenv('homedrive') + os.getenv('homepath')
else:
    home = os.getenv('HOME')

setup(
    name='platform-migrator',
    version='1.0.0',
    description='Migrate software from one system to another',
    long_description=long_description,
    url='https://gitlab.com/mmc691/platform-migrator',
    author='Munir Contractor',
    author_email='mmc691@nyu.edu',
    download_url='https://gitlab.com/mmc691/platform-migrator/',
    platforms=['Linux'],
    license='MIT',
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=['pyyaml'],
    data_files=[
        (os.path.join(home, '.platform_migrator', 'config'),
         ['config/package-managers.ini']
        ),
    ],
    entry_points={
        'console_scripts': [
            'platform-migrator=platform_migrator.main:main'
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Software Distribution',
        'Topic :: Utilities'
    ]
)
