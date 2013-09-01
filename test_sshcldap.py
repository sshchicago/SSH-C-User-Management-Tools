#!/usr/bin/env python2.6

# Tests for the sshcldap class.

# Depends on a file named "ldapcreds.cfg" being in the current working
# directory, formatted as:
#   [ldap]
#   user=eidle
#   passwd=spam


import unittest
from ConfigParser import RawConfigParser as cparser
import sshcldap

config = cparser()
config.read('ldapcreds.cfg')

uid=config.get('ldap','user')
passwd=config.get('ldap','passwd')

l = sshcldap.sshcldap(uid, passwd)

class ldapUnitTests(unittest.TestCase):

    def testBind(self):
        self.failUnless(l.is_connection_valid())

def main():
    unittest.main()

if __name__ == '__main__':
    main()
