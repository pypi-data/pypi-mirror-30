#!/usr/bin/python3

from setuptools import setup

home_page = 'https://github.com/luoyeah/github-console'

requires = [
    'github3.py>=1.0.1',
    'docopt>=0.6.2'
]

packages = [
    'github_console'
]

setup(
    name='github-console',
    version='1.0.7',
    keywords=(
        'github-console',
        'github',
        'git'
    ),
    author='luoyeah',
    author_email='luoyeah_ilku@foxmail.com',
    url=home_page,
    license='GPLv3',
    description='Github console tool.',
    long_description='HomePage: %s' % home_page,
    include_package_data=True,
    zip_safe=False,
    packages=packages,
    platforms='any',
    python_requires=">=3.0",
    install_requires=requires,
    entry_points={
        'console_scripts':[
            'github = github_console.github:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
