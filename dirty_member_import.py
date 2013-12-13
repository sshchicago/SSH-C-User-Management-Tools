#!/usr/bin/env python

# A really hackish way to add LDAP members.
# Takes a CSV with this format:
# FullName, EmailAddress, Password
# EmailAddress can be blank.
# Outputs an LDIF to stdout that can then be used by ldapadd or ldapmodify:
# ldapadd -x -D uid=username,ou=people,dc=sshchicago,dc=org -W -f

import csv
import sys
from time import strftime

csvfile = sys.argv[1]

with open(csvfile, 'rU') as csvfile:
    member_rdr = csv.reader(csvfile)
    for row in member_rdr:
        cn=row[0]
        mail=row[1]
        userpassword=row[2]
        givenname=cn.split()[0]
        sn=cn.split()[1]
        uid=givenname[0].lower() + sn.lower()
        template="""dn: uid=%s,ou=People,dc=sshchicago,dc=org
objectclass: top
objectclass: person
objectclass: inetorgperson
cn: %s
sn: %s
givenname: %s
mail: %s
userpassword: %s
"""
        userldif = template % (uid, cn, sn, givenname, mail, userpassword)
        print userldif
