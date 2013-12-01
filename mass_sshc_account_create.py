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
import sshcldap

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

logger.addHandler(ch)

class ldap_account_manager:

    # Ldap credentials:
    ldapuser = None
    ldappass = None
    ldapServerUrl = None
#    l = None

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

        self.l = sshcldap.sshcldap(self.ldapuser, self.ldappass, self.ldapServerUrl)
        logger.debug("Created a LDAP server connection. Status is %s" % str(self.l.is_connection_valid()))
        # May as well populate the exiting_user_list, it's not going to change until we're done.
        self.existingUserList = self.l.list_people()
        logger.debug("existingUserList contains %s people " % len(self.existingUserList))
    
    def __does_user_exist(self, email):
        """
        Given an email address, check if a user exists.
        """
        email = email.lower()
        for user in self.existingUserList:
            if user[1]['mail'].lower() == email:
                return True
        return False

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
        self.populate_paying_users(csvname)
        # For user in active users:
            # Check against each row in payingAccount.
            # If not there, add to deActivateList
            # If protected, add to toProtectList
            # If there, check if active.
            # If active, add to toUnchangedList
            # If inactive, add to toReactivateList
        for existingUser in self.existingUserList:
            if self.__paying_user(existingUser[1]['mail']) == True:
                if (self.l.is_user_active(existingUser[1]['uid']) == True):
                    # Existing, active. Do nothing.
                    self.toUnchangedList += existingUser
                    break
                if (self.l.is_user_active(existingUser[1]['uid']) == False):
                    # An inactive user paid thier dues! Activate them.
                    self.toReactivateList += existingUser
                    break
            else:
                # We've made it through the paying user list without finding them.
                if (self.l.is_member_of_group(existingUser[1]['uid'], self.l.PROTECTED_USER_GROUPS[0])):
                    # User is protected, put them in that list.
                    self.toProtectList += existingUser
                    break
                else:
                    # Someone didn't pay their dues. Deactivate them if they're inactive, 
                    # otherwise do nothing.
                    if (self.l.is_user_active(existingUser[1]['uid'] == True)):
                        self.toDeactivateList += existingUser
                    else:
                        self.toUnchangedList += existingUser

        # For user in paying users:
        # Check against each Active User.
        # If present, do nothing.
        # If not present, add them to toAddList
        for payingUser in self.payingUserList:
            logger.debug("Going to do things with %s" % payingUser)
            pass



    def populate_paying_users(self, csvfile):
        """
        Populates self.payingUsersList
        """
        infile = open(csvfile,'r')
        csvreader = csv.DictReader(infile)
        for row in csvreader:
            logger.debug("Parsing row %s " % row)
            if row['Status'] == 'Active':
                logger.debug("Found active user %s " % row)
                userAccount = {}
                userAccount['profileId'] = row['Profile ID']
                userAccount['description'] = row['Description']
                userAccount['payerName'] = row['Payer Name']
                userAccount['mail'] = row['Email']
                userAccount['status'] = row['Status']
                userAccount['amountLast'] = row['Amount Last Paid']
                userAccount['nextBillDate'] = row['Next Bill Date']
                self.payingUserList.append(userAccount)
        logger.debug("Paying users is %s " % self.payingUserList)

    def __paying_user(self, email):
        """
        Checks if email matches against an entry in self.payingUserList
        """
        for user in self.payingUserList:
            logger.debug("Checking email %s against paying user %s " % (email,user))
            if user['mail'].lower() == email[0].lower():
                return True
        return False

    def create_user(self, givenName, surname, emailAddr, doEmail = True):
        """
        Creates a new user and puts them in the default groups.
        Sends out an email to them about their new account (unless doEmail = False)
        """
        logger.debug("create_user: %s | %s | %s | %s" % (givenName, surname, emailAddr, doEmail ))
        pass

    def deactivate_user(self, uid, doEmail = False, specialReason = None):
        """
        Deactivates an existing user. 
        Sends out an email to tell them that their account has been deactivated
        if doEmail = True, and allows a special reason to be attached by passing specialReason
        Returns True if a deactivation worked. Returns False if the user is already deactivated.
        Skips doEmail if activation state doesn't change.
        """
        logger.debug("deactivate_user: %s | %s | %s" % (uid, doEmail, specialReason))
        pass

    def activate_user(self, uid, doEmail = False, specialReason = None):
        """
        Reactivates a previously deactivated user.
        Sends out an email to tell them that their account has been reactivated
        if doEmail = True, and allows for a reason.
        Returns True if an activation worked. Returns False if the user is already active
        Skips doWmail if activation state hasn't changed.
        """
        logger.debug("activate_user: %s | %s | %s" % (uid, doEmail, specialReason))
        pass

    def __send_mail(self, toAddress, subject, body, ccAddress=None, bccAddress=None):
        """
        Sends out an email.
        """
        logger.debug("__send_email: %s | %s | %s | %s | %s" % (toAddress, subject, body, ccAddress, bccAddress))
        pass




