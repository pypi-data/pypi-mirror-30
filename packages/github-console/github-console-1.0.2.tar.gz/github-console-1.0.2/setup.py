#!/usr/bin/python3

from setuptools import setup

setup(
    name = 'github-console',
    version = '1.0.2',
    keywords = (
        'github',
        'git'
    ),
    author = 'luoyeah',
    author_email = '1403287193@qq.com',
    url = 'https://github.com/luoyeah/github',
    license = 'GPLv3',
    description = 'github console tools',
    long_description = 'github console tools',
    include_package_data = True,
    packages = [
        'github_console'
    ],
    platforms = 'any',
    install_requires = [
        'github3.py>=1.0.1',
        'docopt>=0.6.2'
    ],
    entry_points = {
        'console_scripts':[
            'github = github_console.github:main'
        ]
    }
)
