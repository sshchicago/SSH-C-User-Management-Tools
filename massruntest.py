#!/usr/bin/env python

# A small test run for creating a bunch of users.

from pprint import pprint as pp
import logging

from ConfigParser import RawConfigParser as cparser
config = cparser()
config.read('ldapcreds.cfg')

uid=config.get('ldap','user')
passwd=config.get('ldap','passwd')

url="ldap://dir.sshchicago.org:389"

csvfile="users_test.csv"

import mass_sshc_account_create

m = mass_sshc_account_create.ldap_account_manager(uid, passwd, url)
m.build_change_lists(csvfile)
