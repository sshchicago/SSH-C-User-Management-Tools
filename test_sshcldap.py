#!/usr/bin/env python

# Tests for the sshcldap class.
# It's very safe to say I haven't used python's unittest framework much :)

# Depends on a file named "ldapcreds.cfg" being in the current working
# directory, formatted as:
#   [ldap]
#   user=eidle
#   passwd=spam

import os
import random
import unittest
from ConfigParser import RawConfigParser as cparser
import sshcldap
import string

config = cparser()
config.read('ldapcreds.cfg')

uid=config.get('ldap','user')
passwd=config.get('ldap','passwd')

l = sshcldap.sshcldap(uid, passwd)


def genName():
    """
    Randomly picks a word to use as a name. Returns
    a tuple containing the full name, as well as
    an expected uid.
    """
    # Presuming you have a dictfile on your system.
    import os
    import random
    wordfile = '/usr/share/dict/words'
    wf_len = os.path.getsize(wordfile)
    words = open(wordfile,'r')
    words.seek(random.randint(0,wf_len - 100)) # Try not to EOF 
    words.readline()
    fname = words.readline().title().strip()
    lname = words.readline().title().strip()
    fullName = "%s %s" % (fname, lname)
    uid = fname[0].lower() + lname.lower()
    return (fullName, uid)

def genPass():
    """
    Generates a string of random characters to be used as
    a (testing) password.
    """
    characters = string.ascii_letters + string.punctuation  + string.digits
    password =  "".join(random.choice(characters) for x in range(random.randint(8, 16)))
    return password


generatedName, generatedUid = genName()

class ldapUnitTests(unittest.TestCase):


    def testBind(self):
        self.failUnless(l.is_connection_valid())

    def testFindAttempt(self):
        # May as well search for ourselves :)
        result = l.find_user(uid)
        self.failUnless(result[0][0].find(uid) > -1)

    def testActive(self):
        #result = l.is_user_active('rbak')
        self.failUnless(l.is_user_active(uid))

    def testCreateUserAndCheckIfExist(self):
        # Creates a user, checks if it exists
        # Generate a user
        name, newUid = generatedName, generatedUid
        print "Creating user %s : %s" % (name, newUid)
        createdUid, createdPass = l.create_user(name.split()[0], name.split()[1], '%s%s@example.com' % (name.split()[0], name.split()[1]))
        print "Generated password is: %s" % createdPass
        # Make sure the createdUid contains our newUid (the class caluclated it successfully)
        self.failUnless(createdUid == newUid)
        # Search for the user
        result = l.find_user(newUid)
        self.failUnless(result[0][0].find(newUid) > -1)
        print "newUid: %s" % newUid
        self.__createdUid = newUid
        print "__createdUid: %s" % self.__createdUid
      
    def testDeactivateUser(self):
        print "__createdUid: %s" % generatedUid

        l.deactivate_user(generatedUid)
        self.failIf(l.is_user_active(generatedUid))

    def testReactivateUser(self):
        l.activate_user(generatedUid)
        self.failUnless(l.is_user_active(generatedUid))
    
    def testZDeleteUser(self):
        l.delete_user(generatedUid)
        self.failUnless(l.is_user_active(uid))

#     def deleteUser(self):
#         # Delets a user, checks if the user is now gone.
#         pass

def main():
    unittest.main(verbosity=2)

if __name__ == '__main__':
    main()
