#1/usr/bin/env python

# Mass-add a bunch of users into the SSHC LDAP server.

# This will:
    # Take a CSV as a parameter.
    # Open a log file.
    # For each entry in the CSV, either:
        # Create a new accont, and dispatch an email to the account holder
        # Find that the user exists, and do nothing (but log it)
    # Show a summary of what's been done.

__author__ = "Christopher Swingler"
__copyright__ = "Copyright 2013, South Side Hackerspace Chicago"
__license__ = "tbd"
__email__ = "chris@chrisswingler.com"
__status__ = "Development"

import sys
import csv
import logging
import config
import sshcldap

logger = logging.getLogger(__name__)

class ldap_account_manager:

    ldapuser = None
    ldappass = None
    ldapServerUrl = None
    l = None

    def __init__(self, username, password, serverUrl=None):
        """
        Creates an account_creator object.
        """
        self.ldapuser = username
        self.ldappass = password
        self.ldapserver = serverUrl

        self.l = sshcldap.sshcldap(self.ldapuser, self.ldapppass, self.ldapServerUrl)
        logger.debug("Created a LDAP server connection. Status is %s" % str(l.is_connection_valid))
    
    def build_change_lists(self, csvname):
        """
        Takes a filename in csvname, opens it, and then returns four lists:
            * Users to add
            * Users to deactivate
            * Users to reactivate
            * Protected users (would have been deactivated but are somehow excepted
        """
        pass

    def create_user(self, givenName, surname, emailAddr, doEmail = true):
        """
        Creates a new user and puts them in the default groups.
        Sends out an email to them about their new account (unless doEmail = false)
        """
        pass

    def deactiavte_user(self, uid, doEmail = false, specialReason = None):
        """
        Deactivates an existing user. 
        Sends out an email to tell them that their account has been deactivated
        if doEmail = True, and allows a special reason to be attached by passing specialReason
        """
        pass

    def activate_user(self, uid, doEmail = false, specialReason = None):
        """
        Reactivates a previously deactivated user.
        Sends out an email to tell them that their account has been reactivated
        if doEmail = True, and allows for a reason.
        """
        pass

    def __send_mail(self, toAddress, subject, body, ccAddress=None, bccAddress=None):
        """
        Sends out an email.
        """
        pass




