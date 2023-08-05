#!/usr/bin/python3
"""github repo

Usage: 
 repo add    <username> <password> <name>
 repo remove <username> <password> <name>
 repo list   <username> [<name>] [--password=<password>]
 repo -h | --help

"""
from docopt import docopt
import github3

class Repo:
    def __init__(self,username, password=None):
        self.username = username
        self.gh = github3
        if password:
            try:
                self.gh = github3.login(username, password)
                self.gh.me()
            except github3.exceptions.AuthenticationFailed as e:
                exit('[-]Username or password error.')
    
    def list_repo(self, repo_name):
        if repo_name:
            try:
                r = self.gh.repository(self.username, repo_name)
                master = r.branch('master')
                for i in master.commit.commit.tree.to_tree().recurse().tree:
                    print(i.path)
            except github3.exceptions.NotFoundError as e:
                exit('[-]Repository %s is not existence.' % repo_name)            
        else:
            try:
                for i in self.gh.repositories_by(self.username):
                    print(i.name)
            except github3.exceptions.NotFoundError as e:
                exit('[-]User %s is not existence.' % self.username)
                
    def add(self, repo_name):
        try:
            if self.gh.create_repository(repo_name):
                print('[+]Success.')
        except github3.exceptions.UnprocessableEntity as e:
            exit('[-]Repository %s is existence.' % repo_name)
        
    def remove(self, repo_name):
        try:
            r = self.gh.repository(self.username, repo_name)
            if r.delete():
                print('[+]Success.')
        except github3.exceptions.NotFoundError as e:
            exit('[-]Repository %s is not existence.' % repo_name)
    
def main(args):
    args = docopt(__doc__,argv=args)
    #print(args)
    if args['list'] == True:
        Repo(args['<username>'], args['--password']).list_repo(args['<name>'])
    elif args['add'] == True:
        Repo(args['<username>'], args['<password>']).add(args['<name>'])
    elif args['remove'] == True:
        Repo(args['<username>'], args['<password>']).remove(args['<name>'])
    else:
        print(__doc__)