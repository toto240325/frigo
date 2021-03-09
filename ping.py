#https://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import RPi.GPIO as GPIO 
from gpiozero import Button 
from time import sleep
import datetime
import os
import datetime
import subprocess
import glob
import time



def checkPing():
  global fhtml
  cmd="/bin/ping -c google.com 2> /dev/null > /tmp/ping.txt && /usr/bin/awk '/0% packet loss/ {print $4}' </tmp/ping.txt"
  str=subprocess.check_output(cmd, shell=True).rstrip()
  msg = "Q:"+str+"/Q"
  #print(msg)
  #fhtml.write(msg)
  if str=="1":
    return "1"
  else:
    return "0"

def sendmail(subject,message):
  msg = MIMEMultipart()

  password = "Toto060502!n"
  msg['From'] = "toto240325mailer@gmail.com"
  msg['To'] = "toto2403252@gmail.com"
  msg['Subject'] = subject

  msg.attach(MIMEText(message, 'plain'))
  server = smtplib.SMTP('smtp.gmail.com: 587')
  server.starttls()
  server.login(msg['From'], password)
  server.sendmail(msg['From'], msg['To'], msg.as_string())
  server.quit()

def openfiles(fhtml):

  if not os.path.exists(htmlFile):
    fhtml=open(htmlFile,"a")
    fhtml.write("<html>")
    fhtml.write ("""\
  <head>
    <meta http-equiv="refresh" content="30">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"> </script>
    <script>
      $(document).ready(function(){
        $("html, body").animate({ scrollTop: 99999 },"slow");
        console.log("done");
      });
    </script>
    <style type="text/css">
      body { font-family: 'Courier New', monospace; font-size: 10px; }
      p    { line-height: 1px;}
      table, th, td { border: 1px solid black;border-collapse: collapse;}
    </style>
   </head>
   <html>
   <body>
   <table><tr><th>time<th>ping</tr>
    """)
  else:
    fhtml=open(htmlFile,"a")
  fhtml.flush()
  return (fhtml)

def closefile(fhtml):
  fhtml.flush()
  fhtml.close()

def updateEmail():
  global iterCompressorOFF,iterCompressorON,temp
  x = datetime.datetime.now()
  now = x.strftime("%H:%M:%S")
  if iterCompressorOFF>ceilingCompressorOFF:
    msg = now + "\n"
    msg = msg + "nb iter with compressor OFF : " + str(iterCompressorOFF) + "\n"
    print ("Sending email : "+msg)
    sendmail("Fridge problem (no compressor : "+str(iterCompressorOFF)+")",msg)
  if iterCompressorON>ceilingCompressorON:
    msg = now + "\n"
    msg = msg + "nb iter with compressor ON : " + str(iterCompressorON) + "\n"
    print ("Sending email : "+msg)
    sendmail("Fridge problem (compressor ON: "+str(iterCompressorON)+")",msg)


def updateWeb(res):
  (f,fhtml)=openfiles()
  x = datetime.datetime.now()
  #now = x.strftime("%d/%m/%Y %H:%M:%S")
  now = x.strftime("%H:%M:%S")

  bartxt,barhtml = bar(iterCompressorOFF)
  msg = "<td>{0}<td>{1}<td>{2}<td>{3}<td>{4}<td>{5}<td>{6}".format((iter),now,statusHtml(status),lineQual,str(temp),bar2(temp),"ON" if status else "")
  msgtxt = "{0:<3}; {1} ; {2} ; {3:>3} ; {4} ; {5} ; {6}".format((iter),now,status,lineQual,str(temp),bar2(temp),"ON" if status else "")
  msgtxt = msgtxt + bartxt
  msghtml = "<tr>" + msg  + "<td>" + barhtml + "</tr>"

  #msg = str(iter) + ";" + now + ";" + str(status) + ";" + GPIO.intput(relay)
  print (msgtxt)
  f.write(msgtxt+"\n")
  fhtml.write(msghtml)

  closefiles(f,fhtml)

 
#-main---------------------------------------------
htmlFile = "/home/pi/frigo/html/ping.html"
fhtml = None

openfiles(fhtml)

res=checkPing()
x = datetime.datetime.now()
#now = x.strftime("%d/%m/%Y %H:%M:%S")
now = x.strftime("%H:%M:%S")
msg = "<td>{0}<td>{1}".format(now,res)
msghtml = "<tr>" + msg  "</tr>"
print (msghtml)
fhtml.write(msghtml)

closefiles(fhtml)


