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
import string
import random
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

logger.addHandler(ch)

class sshcldap:
    """
    A class with LDAP tools for interacting with our repository.
    """

    BASEDN="dc=sshchicago,dc=org"
    URL="ldap://dir.sshchicago.org:389"


    STANDARD_USER_GROUPS=['SSHC Members']
    PROTECTED_USER_GROUPS=['Deactivation Protected Users'] + STANDARD_USER_GROUPS
    ADMIN_USER_GROUPS=['Administrative Members'] + PROTECTED_USER_GROUPS
    OFFICER_USER_GROUPS=['Officers'] + ADMIN_USER_GROUPS

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

    def __genPass(self):
        """
        Generates a string of random characters to be used as
        a (temporary) password.
        """
        characters = string.ascii_letters + string.punctuation  + string.digits
        password =  "".join(random.choice(characters) for x in range(random.randint(8, 16)))
        return password


    def is_connection_valid(self):
         """
         Checks if the LDAP bind is working. Returns true/false.
         """
         # Ideally, we'd use python-ldap's whoami_s() to see who we are and if we've
         # bound, but 389 doesn't implement RFC 4532. In that case, we're
         # going to do a search, and if we get more than 1 result, consider it good.
         r = self.__lconn.search_s(self.BASEDN, ldap.SCOPE_SUBTREE, '(cn=*)',['mail'])
         if (len(r) > 1):
             return True
         return False

    def find_user(self, uid):
        """
        Finds a user with the matching uid. Returns some information about that
        user.
        """
        r = self.__lconn.search_s(self.BASEDN, ldap.SCOPE_SUBTREE, '(uid=*%s*)' % uid, ['mail','cn'])
        return r

    def find_user_by_email(self, email):
        """
        Finds a user with the matching email address (case knocked down).
        Returns true if they exist, false otherwise.
        """
        result = self.__lconn.search_s(self.BASEDN, ldap.SCOPE_SUBTREE, '(mail=%s)' % email, ['mail','cn'])
        return (len(result) > 0)

    def is_user_active(self, uid):
        """
        Returns if a user is active, or inacitve.
        """
        # The active/inactive stuff is very much a 389 extension. 
        # nsAccountLock = True when an account is inactive. 
        # If it's false, or the attrib doesn't exist at all, the acount is active.
        r = self.__lconn.search_s(self.BASEDN, ldap.SCOPE_SUBTREE, '(uid=*%s*)' % uid, ['nsAccountLock'])
        logger.debug("%s's nsAccountLock is %s" % (uid, r))
        try:
            return not(bool(r[0][1]['nsAccountLock']))
        except KeyError:
            # Expected if the account is active.
            return True

        return True

    def create_user(self, givenName, sn, mail, uid=None, password=None):
         """
         Creates a user under basedn. If not specified, uid will be 
         the first letter of givenName + sn (lower case), and
         password will be randomly generated.

         Returns a tuple containing (uid, password); password in cleartext.
         """
         if (uid == None):
             # Create the UID
             uid = "%s%s" % (givenName.lower()[0], sn.lower())

         if (password == None):
             password = self.__genPass()

         addDn = "uid=%s,ou=People,%s" % (uid, self.BASEDN)
         addModList = [('userPassword', password), \
                       ('mail', mail), ("sn", sn), ("givenname",givenName), ("cn", "%s %s" % (givenName, sn)), \
                       ("objectclass","top"),("objectclass","person"),("objectclass","inetorgperson")]
         self.__lconn.add_s(addDn, addModList)
         return (uid, password)

    def delete_user(self, uid):
         """
         Deletes a user. Should not be used much, in favor of deactivate_user.
         """
         self.__lconn.delete_s("uid=%s,ou=People,%s" % (uid, self.BASEDN))

    def deactivate_user(self, uid):
         """
         Deactivates a user; preventing them from logging in. Leaves the entry
         in the database.
         """
         self.__lconn.modify_ext_s("uid=%s,ou=People,%s" % (uid, self.BASEDN), [(ldap.MOD_ADD,'nsAccountLock',"True")])

    def activate_user(self, uid):
        """
        Activates a user (by deleting the related attribute).
        """
        self.__lconn.modify_ext_s("uid=%s,ou=People,%s" % (uid, self.BASEDN), [(ldap.MOD_DELETE,'nsAccountLock',None)])

    def add_to_group(self, uid, group):
         """
         Adds the uid to a single group.
         """
         fquid = "uid=%s,ou=People,%s" % (uid, self.BASEDN)
         fqgrpid = "cn=%s,ou=Groups,%s" % (group, self.BASEDN)
         self.__lconn.modify_ext_s(fqgrpid, [(ldap.MOD_ADD,'uniqueMember',fquid)])

    def add_to_groups(self, uid, groups):
        """
        Adds a UID to the list of groups in group.
        """
        for group in groups:
            self.add_to_group(uid, group)

    def set_standard_user_groups(self, uid):
         """
         Adds the uid to the list of standard groups defined by 
         STANDARD_USER_GROUPS
         """
         self.add_to_groups(uid, self.STANDARD_USER_GROUPS)

    def set_admin_user_groups(self, uid):
        """
        Adds the uid to the list of groups defined by
        ADMIN_USER_GROUPS
        """
        self.add_to_groups(uid, self.ADMIN_USER_GROUPS)

    def set_officer_user_groups(self, uid):
        """
        Adds the uid to the list of groups defined by
        OFFICER_USER_GROUPS
        """
        self.add_to_groups(uid, self.OFFICER_USER_GROUPS)

    def reset_password(self, uid):
        """
        Sets the password of uid to a random value. Returns new password. 
        """
        newpass = self.__genPass()
        #self.__lconn.passwd_s(user="uid=%s,ou=People,%s" % (uid, self.BASEDN), oldpw=None, newpw=newpass)
        self.__lconn.modify_ext_s("uid=%s,ou=People,%s" % (uid, self.BASEDN), [(ldap.MOD_REPLACE,'userPassword',newpass)])
        return newpass

    def list_people(self):
        """
        Returns a list of all members of the ou=People ou.
        """
        logger.debug("Going to search (\"ou=People,%s\", scope=ldap.SCOPE_SUBTREE, filterstr='(objectClass=person)'" % self.BASEDN)
        people = self.__lconn.search_s("ou=People,%s" % (self.BASEDN), scope=ldap.SCOPE_SUBTREE, filterstr='(objectClass=person)')
        logger.debug("People is %s | %s | %s" % (type(people), len(people), people))
        logger.debug("People contains %s members" % len(people))
        return people

    def is_member_of_group(self, uid, groupCn):
        """
        Returns true if uid is a member of groupCn,
        otherwise return false.
        """
        if(type(uid) == list):
            uid = uid[0]
        uid = "uid=%s" % uid    
        # (&(objectClass=groupOfUniqueNames)(cn~="Deactivation Protected Users,ou=Groups,dc=sshchicago,dc=org"))
        groupItems = self.__lconn.search_s("ou=Groups,%s" % (self.BASEDN), scope=ldap.SCOPE_SUBTREE, filterstr='(&(objectClass=groupOfUniqueNames)(cn~=%s))' % groupCn)
        logger.debug("Members of %s are: %s" % (groupCn, groupItems))
        from pprint import pprint as pp
        pp(groupItems)
        for uniqueMember in groupItems[0][1]['uniqueMember']:
            logger.debug("Testing if %s == %s" % (uid, uniqueMember))
            if uniqueMember.find(uid) > -1:
                logger.debug("Found %s in %s" % (uid, uniqueMember))
                return True

        return False
