#!/usr/bin/python3
"""Github console tools.

Usage:
 github <command> [<args> ...]
 github -h | --help
 
Commands:
 repo       Repository.
 key        SSH Key.
"""
from docopt import docopt
from . import key
from . import repo

def main():
    args = docopt(__doc__, help=True, options_first=True)
    if args['<command>'] == 'repo':
        repo.main(args['<args>'])
    elif args['<command>'] == 'key':
        key.main(args['<args>'])
    else:
        print(__doc__)