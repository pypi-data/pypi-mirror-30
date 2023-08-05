#!/usr/bin/python3

from setuptools import setup

setup(
    name='github-console',
    version='1.0.4',
    keywords=(
        'github-console',
        'github',
        'git'
    ),
    author='luoyeah',
    author_email='luoyeah_ilku@foxmail.com',
    url='https://github.com/luoyeah/github-console',
    license='GPLv3',
    description='Github console tool.',
    long_description=open('README.md', 'r').read(),
    include_package_data=True,
    packages=[
        'github_console'
    ],
    platforms='any',
    install_requires=[
        'github3.py>=1.0.1',
        'docopt>=0.6.2'
    ],
    entry_points={
        'console_scripts':[
            'github = github_console.github:main'
        ]
    },
    classifiers=[
        'License :: OSI Approved',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',        
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent'
    ]
)
