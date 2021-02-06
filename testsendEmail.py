#  !/usr/bin/env python
#

import sendmail
import datetime

now1=datetime.datetime.now()
nowStr = now1.strftime('%Y-%m-%d %H:%M:%S')

user_name = "toto240325mailer@gmail.com"
passwd = "Toto060502!n"
from_email = "toto240325@gmail.com"
to_email = "toto240325@gmail.com"
subject = "Watchdog on " + nowStr + " from Raspberry 90"
body = "body"
htmlbody = "htmlbody"

myTmpFile = "/home/toto/projects/watchdog/watchdog.tmp"
tmpfile=open(myTmpFile,"w")
tmpfile.write("msg")
tmpfile.close()

print ("test10")
sendmail.mySend(user_name, passwd, from_email, to_email, subject, body, htmlbody, myTmpFile)
print ("test11")




