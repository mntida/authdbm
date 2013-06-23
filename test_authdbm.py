import os
import tempfile
import shutil
import unittest
from authdbm import AuthDbm, AuthGroup

def make_dbm():
    _, tmpfname = tempfile.mkstemp(dir=os.getcwd())
    shutil.copyfile('group', tmpfname)
    return tmpfname


class TestAuthDbm(unittest.TestCase):

    def setUp(self):
        self.tempfile = make_dbm()

    def tearDown(self):
        os.remove(self.tempfile)

        
    def check_user1(self, users):
        self.assertIn('user1', users)
        self.assertEquals('~', users['user1']['passwd'])
        self.assertEquals(set(['group1','group2','group3',]),
                          users['user1']['groups'])
        self.assertEquals('stupid_comment', users['user1']['comment'])
        self.assertEquals(sorted(['passwd','groups','comment']),
                          sorted(users['user1'].keys()))

    def check_user2(self, users):
        self.assertIn('user2', users)
        self.assertEquals('~', users['user2']['passwd'])
        self.assertEquals(set(['group1','group2','group11','group22','group33']),
                          users['user2']['groups'])
        self.assertEquals(None, users['user2']['comment'])
        self.assertEquals(sorted(['passwd','groups','comment']),
                          sorted(users['user2'].keys()))

    def check_user3(self, users):
        self.assertIn('user3', users)
        self.assertEquals('~', users['user3']['passwd'])
        self.assertEquals(set(['group3','group33']),
                          users['user3']['groups'])
        self.assertEquals(None, users['user3']['comment'])
        self.assertEquals(sorted(['passwd','groups','comment']),
                          sorted(users['user3'].keys()))

    def check_user4(self, users):
        self.assertIn('user4', users)
        self.assertEquals('~', users['user4']['passwd'])
        self.assertEquals(set([]), users['user4']['groups'])
        self.assertEquals(None, users['user4']['comment'])
        self.assertEquals(sorted(['passwd','groups','comment']),
                          sorted(users['user4'].keys()))

    def test_read_file(self):
        users = AuthDbm.read_file(self.tempfile)
        self.check_user1(users)
        self.check_user2(users)
        self.check_user3(users)
        self.check_user4(users)


    def test_write_file(self):
        users = AuthDbm.read_file(self.tempfile)
        AuthDbm.write_file(self.tempfile, users)
        users_written = AuthDbm.read_file(self.tempfile)
        self.assertEquals(users, users_written)

    def test_write_file2(self):
        users = AuthDbm.read_file(self.tempfile)
        del users['user1']
        AuthDbm.write_file(self.tempfile, users)
        users_written = AuthDbm.read_file(self.tempfile)
        self.assertEquals(users, users_written)

    def test_write_file3(self):
        users = AuthDbm.read_file(self.tempfile)
        del users['user2']
        AuthDbm.write_file(self.tempfile, users)
        users_written = AuthDbm.read_file(self.tempfile)
        self.assertEquals(users, users_written)

    def test_write_file4(self):
        users = AuthDbm.read_file(self.tempfile)
        del users['user3']
        AuthDbm.write_file(self.tempfile, users)
        users_written = AuthDbm.read_file(self.tempfile)
        self.assertEquals(users, users_written)

    def test_write_file5(self):
        users = AuthDbm.read_file(self.tempfile)
        users['user1']['groups'].remove('group1')
        users['user2']['groups'].remove('group22')
        users['user3']['groups'].add('group666')
        users['user4']['groups'].add('group99')
        AuthDbm.write_file(self.tempfile, users)
        users_written = AuthDbm.read_file(self.tempfile)
        self.assertEquals(users, users_written)


class TestAuthGroup(unittest.TestCase):

    def setUp(self):
        self.tempfile = make_dbm()
        self.users = AuthDbm.read_file(self.tempfile)
        self.groups = AuthGroup(self.users)

    def tearDown(self):
        os.remove(self.tempfile)

    def test_users_in_group(self):
        self.assertEquals(set(['user1','user2']),
                          self.groups.users_in_group('group1'))
        self.assertEquals(set(['user1','user2']),
                          self.groups.users_in_group('group2'))
        self.assertEquals(set(['user1','user3']),
                          self.groups.users_in_group('group3'))
        self.assertEquals(set(['user2']),
                          self.groups.users_in_group('group11'))
        self.assertEquals(set(['user2']),
                          self.groups.users_in_group('group22'))
        self.assertEquals(set(['user2','user3']),
                          self.groups.users_in_group('group33'))

    def test_get_users(self):
        self.assertEquals(set(['user1','user2','user3','user4']),
                          self.groups.get_users())

    def test_get_groups(self):
        self.assertEquals(set(['group1','group2','group3',
                               'group11','group22','group33']),
                          self.groups.get_groups())

    def test_users_in_group(self):
        self.assertEquals(set(['user1','user2']),
                          self.groups.users_in_group('group1'))
        self.assertEquals(set(['user1','user2']),
                          self.groups.users_in_group('group2'))
        self.assertEquals(set(['user1','user3']),
                          self.groups.users_in_group('group3'))
        self.assertEquals(set(['user2']),
                          self.groups.users_in_group('group11'))
        self.assertEquals(set(['user2']),
                          self.groups.users_in_group('group22'))
        self.assertEquals(set(['user2','user3']),
                          self.groups.users_in_group('group33'))
        self.assertEquals(set([]),
                          self.groups.users_in_group('nosuchgroup'))
        
    def test_user_exists(self):
        self.assertTrue(self.groups.user_exists('user1'))
        self.assertTrue(self.groups.user_exists('user2'))
        self.assertTrue(self.groups.user_exists('user3'))
        self.assertTrue(self.groups.user_exists('user4'))
        self.assertFalse(self.groups.user_exists('nosuchuser'))
        
    def test_add_user(self):
        self.groups.add_user('user5')
        self.assertTrue(self.groups.user_exists('user5'))
        self.assertEquals(set(['user1','user2','user3',
                               'user4','user5']),
                          self.groups.get_users())

    def test_remove_user1(self):
        self.groups.add_user('user5')
        self.assertTrue(self.groups.user_exists('user5'))
        self.groups.remove_user('user5')
        self.assertFalse(self.groups.user_exists('user5'))
        self.assertEquals(set(['user1','user2','user3','user4']),
                          self.groups.get_users())

    def test_remove_user2(self):
        self.groups.remove_user('nosuchuser')
        self.assertEquals(set(['user1','user2','user3','user4']),
                          self.groups.get_users())


    def test_add_group(self):
        self.groups.add_group('user1','group11')
        self.assertEquals(set(['user1','user2']),
                          self.groups.users_in_group('group11'))
        self.groups.add_group('user1','newgroup')
        self.assertEquals(set(['user1']),
                          self.groups.users_in_group('newgroup'))
        self.assertEquals(set(['group1','group2','group3','group11','group22',
                               'group33','newgroup']), self.groups.get_groups())
        self.groups.add_group('newuser','newgroup')
        self.assertEquals(set(['user1','newuser']),
                          self.groups.users_in_group('newgroup'))

    def test_remove_group1(self):
        self.groups.remove_group('user1','group1')
        self.assertEquals(set(['user2']),
                          self.groups.users_in_group('group1'))
        self.groups.remove_group('user2','group1')
        self.assertEquals(set([]), self.groups.users_in_group('group1'))
        self.groups.remove_group('newuser','group2')
        self.assertEquals(set(['user1','user2']),
                          self.groups.users_in_group('group2'))
        self.groups.remove_group('newuser','newgroup')
        self.groups.remove_group('user1','newgroup')
        self.assertEquals(set([]), self.groups.users_in_group('newgroup'))
        self.assertFalse(self.groups.user_exists('newuser'))

    def test_remove_group2(self):
        self.groups.remove_group('user1','nosuchgroup')
        self.assertEquals(set(['group1','group2','group3']),
                          self.groups.groups_with_user('user1'))
