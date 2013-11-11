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

    # Ldap credentials:
    ldapuser = None
    ldappass = None
    ldapServerUrl = None
    l = None


    # Each list that we're playing with
    toAddList = []
    toDeactivateList = []
    toReactivateList = []
    toProtectList = []
    toUnchangedList = []


    # To save us some LDAP queries (created at instantiation)
    existingUserList = []

    # And the list of users who have paid in this CSV load:
    payingUserList = []

    def __init__(self, username, password, serverUrl=None):
        """
        Creates an account_creator object.
        """
        self.ldapuser = username
        self.ldappass = password
        self.ldapserver = serverUrl

        self.l = sshcldap.sshcldap(self.ldapuser, self.ldapppass, self.ldapServerUrl)
        logger.debug("Created a LDAP server connection. Status is %s" % str(l.is_connection_valid))
        # May as well populate the exiting_user_list, it's not going to change until we're done.
        self.existingUserList = self.l.list_people()
    
    def __does_user_exist(self, email):
        """
        Given an email address, check if a user exists.
        """
        email = email.lower()
        for user in self.existingUserList:
            if user[1]['mail'].lower() == email:
                return true
        return false

    def build_change_lists(self, csvname):
        """
        Takes a filename in csvname, opens it, and then populates four lists as 
        members of the ldap_account_manager class
            * Users to add toAddList
            * Users to deactivate toDeactivateList
            * Users to reactivate toRectivateList
            * Protected users (would have been deactivated but are somehow excepted)
                toProtectList
        """
        # For user in active users:
            # Check against each row in payingAccount.
            # If not there, add to deActivateList
            # If protected, add to toProtectList
            # If there, check if active.
            # If active, add to toUnchangedList
            # If inactive, add to toReactivateList
        for existingUser in self.existingUserList:
            if self.__paying_user(existingUser[1]['mail']) == true:
                if (l.is_user_active(existingUser[1]['uid']) == true):
                    # Existing, active. Do nothing.
                    self.toUnchangedList += existingUser
                    break
                if (l.is_user_active(existingUser[1]['uid']) == false):
                    # An inactive user paid thier dues! Activate them.
                    self.toReactivateList += existingUser
                    break
            else:
                # We've made it through the paying user list without 
                if (l.is_member_of_group(existingUser[1]['uid'], l.PROTECTED_USER_GROUPS[0])):
                    # User is protected, put them in that list.
                    self.toProtectList += existingUser
                    break
                else:
                    # Someone didn't pay their dues. Deactivate them if they're inactive, 
                    # otherwise do nothing.
                    if (l.is_user_active(existingUser[1]['uid'] == true)):
                        self.toDeactivateList += existingUser
                    else:
                        self.toUnchangedList += existingUser



                
        
        # For user in paying users:
            # Check against each Active User.
            # If present, do nothing.
            # If not present, add them to toAddList


    def populate_paying_users(self, csvfile):
        """
        Populates self.payingUsersList
        """
        infile = open(csvname,'r')
        csvreader = csv.DictReader(infile)
        for row in csvreader:
            if row['Status'] == 'Active':
                userAccount = {}
                profileId = row['Profile ID']
                description = row['Description']
                payerName = row['PayerName']
                mail = row['Email']
                status = row['Status']
                amountLast = row['Amount Last']
                nextBillDate = row['Next Bill Date']
                self.payingUserList += userAccount

    def __paying_user(self, email):
        """
        Checks if email matches against an entry in self.payingUserList
        """
        for user in self.payingUserList:
            if user['mail'].lower() == email.lower():
                return true
        return false

    def create_user(self, givenName, surname, emailAddr, doEmail = true):
        """
        Creates a new user and puts them in the default groups.
        Sends out an email to them about their new account (unless doEmail = false)
        """
        pass

    def deactivate_user(self, uid, doEmail = false, specialReason = None):
        """
        Deactivates an existing user. 
        Sends out an email to tell them that their account has been deactivated
        if doEmail = True, and allows a special reason to be attached by passing specialReason
        Returns true if a deactivation worked. Returns false if the user is already deactivated.
        Skips doEmail if activation state doesn't change.
        """
        pass

    def activate_user(self, uid, doEmail = false, specialReason = None):
        """
        Reactivates a previously deactivated user.
        Sends out an email to tell them that their account has been reactivated
        if doEmail = True, and allows for a reason.
        Returns true if an activation worked. Returns false if the user is already active
        Skips doWmail if activation state hasn't changed.
        """
        pass

    def __send_mail(self, toAddress, subject, body, ccAddress=None, bccAddress=None):
        """
        Sends out an email.
        """
        pass




