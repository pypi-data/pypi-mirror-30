#!/usr/bin/python3
"""github key

Usage: 
 key add    <username> <password> <title> [<key>]
 key remove <username> <password> <title>
 key list   <username> <password>
 key -h | --help

Examples:
 key add  luoyeah 12345678 root@forks.club < ~/.ssh/id_rsa.pub
 key list luoyeah 12345678
"""
from docopt import docopt
import github3
import sys

class Key:
    def __init__(self,username, password):
        self.username = username
        self.gh = github3
        try:
            self.gh = github3.login(username, password)
            self.gh.me()
        except github3.exceptions.AuthenticationFailed as e:
            exit('[-]Username or password error.')
            
    def list(self):
        for i in self.gh.keys():
            print('[*]%s:\n%s\n' % (i.title, i.key))
                    
    def add(self, title, ssh_key):
        try:
            self.gh.create_key(title, ssh_key)
            self.list()
        except github3.exceptions.UnprocessableEntity as e:
            print('[-]This key-title or key is existence.')
                    
    def remove(self, title):
        for i in self.gh.keys():
            if i.title==title:
                i.delete()
                self.list()
                return
        print('[-]Key %s is not existence.' % title)
        
def main(args):
    args = docopt(__doc__,argv=args)
    #print(args)
    if args['list'] == True:
        Key(args['<username>'], args['<password>']).list()
    elif args['add'] == True:
        ssh_key = args['<key>']
        if not ssh_key:
            ssh_key = sys.stdin.read()
        if ssh_key:
            Key(args['<username>'], args['<password>']).add(args['<title>'], ssh_key)
    elif args['remove'] == True:
        Key(args['<username>'], args['<password>']).remove(args['<title>'])
    else:
        print(__doc__)