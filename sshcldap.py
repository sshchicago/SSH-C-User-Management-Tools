#!/usr/bin/env python2.6

"""
sshcldap.py: A class of useful tools for working with LDAP servers.
Tested with 389 Directory Server against the SSH:Chicago user database;
probably works with other directories, but you'll have to try to find
out. :-)
"""

__author__ = "Christopher Swingler"
__copyright__ = "Copyright 2013, South Side Hackerspace Chicago"
__license__ = "tbd"
__email__ = "chris@chrisswingler.com"
__status__ = "Development"

import ldap

class sshcldap:
    """
    A class with LDAP tools for interacting with our repository.
    """

    BASEDN="dc=sshchicago,dc=org"
    URL="ldap://dir.sshchicago.org:389"

    STANDARD_USER_GROUPS=[('cn','SSHC Members')]
    ADMIN_USER_GROUPS=[('cn','Administrative Members')] + STANDARD_USER_GROUPS
    OFFICER_USER_GROUPS=[('cn','Officers')] + ADMIN_USER_GROUPS

    __lconn = None

     def __init__(self, uid, password, url=None, basedn=None):
        """
        Initializes the connection using uid and password. 
        A fully qualified cn is constructed by combining uid and basedn.
        """
        if (basedn != None):
            self.BASEDN = basedn
        if (url != None):
            self.URL = url

        self.__lconn = ldap.initialize(self.URL)
        self.__lconn.simple_bind_s(self.__fquid(uid), password)

     def __delete__(self):
         """
         Deconstructor, just unbinds the connection.
         """
         try:
             __lconn.unbind()
         except:
             # Eh, who cares.
             pass

     def __fquid(self, uid):
         """
         Returns the fully-qualified dn of a uid.
         """
         return "uid=%s,ou=people,%s" % (uid, self.BASEDN)

     def is_connection_valid(self):
         """
         Checks if the LDAP bind is working. Returns true/false.
         """
         # Ideally, we'd use python-ldap's whoami_s() to see who we are and if we've
         # bound, but 389 doesn't implement RFC 4532. In that case, we're
         # going to do a search, and if we get more than 1 result, consider it good.
         r = __lconn.search_s(self.BASEDN, ldap.SCOP_SUBTREE, '(cn=*)',['mail'])
         if (len(r) > 1):
             return True
         return False

     def create_user(self, givenName, sn, mail, uid=None, password=None):
         """
         Creates a user under basedn. If not specified, uid will be 
         the first letter of givenName + sn (lower case), and
         password will be randomly generated.

         Retruns a tuple containing (uid, password); password in cleartext.
         """
         pass

     def delete_user(self, uid):
         """
         Deletes a user. Should not be used much, in favor of deactivate_user.
         """
         pass

     def deactivate_user(self, uid):
         """
         Deactivates a user; preventing them from logging in. Leaves the entry
         in the database.
         """
         pass

     def add_to_groups(self, uid, groups):
         """
         Adds the uid to the list of groups.
         """
         pass

     def set_standard_user_groups(self, uid):
         """
         Adds the uid to the list of standard groups defined by 
         STANDARD_USER_GROUPS
         """
         pass

    def set_admin_user_groups(self, uid):
        """
        Adds the uid to the list of groups defined by
        ADMIN_USER_GROUPS
        """
        pass

    def set_officer_user_groups(self, uid):
        """
        Adds the uid to the list of groups defined by
        OFFICER_USER_GROUPS
        """
        pass

    def reset_password(self, uid):
        """
        Sets the password of uid to a random value. Returns a tuple of uid, new password. 
        """
