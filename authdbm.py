import sys
import os
import tempfile
from contextlib import contextmanager
import bsddb3

@contextmanager
def opendb(filename, mode):
    db = bsddb3.hashopen(filename, mode)
    try:
        yield db
    finally:
        db.close()

class AuthDbm(object):

    keys = ['passwd','groups','comment']

    @staticmethod
    def read_file(filename):
        users = {}
        with opendb(filename,'r') as db:
            for username, data in db.items():
                vals = data.split(':')
                userdict = dict(zip(AuthDbm.keys, vals))
                if 'passwd' not in userdict:
                    userdict['passwd'] = '~'
                if 'groups' in userdict:
                    userdict['groups'] = set(userdict['groups'].split(','))
                else:
                    userdict['groups'] = set()
                if 'comment' not in userdict:
                    userdict['comment'] = None
                users[username] = userdict
        return users

    @staticmethod
    def write_file(filename, users):
        tmpfd, tmpfname = tempfile.mkstemp()
        with opendb(tmpfname,'w') as db:
            db.clear()
            for username,userdict in users.items():
                data = ''
                if 'passwd' in userdict and userdict['passwd']:
                    data += userdict['passwd']
                else:
                    data += '~'
                data += ':'
                if 'groups' in userdict and userdict['groups']:
                    data += ','.join(userdict['groups'])
                data += ':'
                if 'comment' in userdict and userdict['comment']:
                    data += userdict['comment']
                data = data.rstrip(':')
                db[username] = data
        os.close(tmpfd)
        os.rename(tmpfname, filename)

class AuthGroup(object):

    def __init__(self, db={}):
        self.db = db

    def get_users(self):
        return set(self.db.keys())

    def get_groups(self):
        groups = set()
        for user, data in self.db.items():
            try:
                for group in data['groups']:
                    groups.add(group)
            except KeyError:
                pass
        return groups

    def users_in_group(self, groupname):
        users_in_group = set()
        for user, data in self.db.items():
            try:
                if groupname in data['groups']:
                    users_in_group.add(user)
            except KeyError:
                pass
        return users_in_group

    def groups_with_user(self, username):
        try:
            return self.db[username]['groups']
        except KeyError:
            pass

    def user_exists(self, username):
        return username in self.db

    def add_user(self, username):
        if username not in self.db:
            self.db[username] = {'passwd':'~','groups': set(),'comment': None}

    def remove_user(self, username):
        self.db.pop(username, None)

    def add_group(self, username, groupname):
        self.add_user(username)
        self.db[username]['groups'].add(groupname)

    def remove_group(self, username, groupname):
        try:
            self.db[username]['groups'].remove(groupname)
        except KeyError:
            pass
