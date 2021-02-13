#from pathlib import Path
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

csvFile = "/home/pi/frigo.csv"
htmlFile = "/home/pi/frigo/html/frigo.html"
#GPIO.setwarnings(False) 
#GPIO.setmode(GPIO.BOARD) # Use physical pin numbering

#relay = 14
#GPIO.setup(7, GPIO.OUT, initial=GPIO.LOW)
basic_sleep = 60 #normally 60 
bar_divider = 5
alertCeiling = 80

def lineQuality():
  cmd="iwconfig  2> /dev/null | awk '/Qual/ {print $2}'"
  str=subprocess.check_output(cmd, shell=True).rstrip()
  result = (str[8:])[:-4]
  return result

def sendmail(message):
  msg = MIMEMultipart()

  password = "Toto060502!n"
  msg['From'] = "toto240325mailer@gmail.com"
  msg['To'] = "toto2403252@gmail.com"
  msg['Subject'] = "Title of email"

  msg.attach(MIMEText(message, 'plain'))
  server = smtplib.SMTP('smtp.gmail.com: 587')
  server.starttls()
  server.login(msg['From'], password)
  server.sendmail(msg['From'], msg['To'], msg.as_string())
  server.quit()


def bar(j):
  if j<alertCeiling*0.75:
    str = ''
    strhtml = '<span style="color:black;">'
  else:
    str = ''
    strhtml = '<span style="color:red;">'
  for k in range(j / bar_divider):
    str = str + "-"
    strhtml = strhtml + "-"
  strhtml =  strhtml + "</span>"

  return str,strhtml

def initRedLed():
  cmd = 'echo gpio | sudo dd status=none of=/sys/class/leds/led1/trigger'
  print('ready to do this : '+cmd)
  os.system(cmd)

def turnRedLed(onOff):
  cmd = 'echo ' + str(onOff) + ' | sudo dd status=none of=/sys/class/leds/led1/brightness > /dev/null 2>&1' # red led on or off
  print('ready to do this : '+cmd)
  os.system(cmd)

def openfiles():
  f=open(csvFile,"a")

  if not os.path.exists(htmlFile):
    fhtml=open(htmlFile,"a")
    fhtml.write("<html>")
    fhtml.write ("""\
    <style type="text/css">
    body { font-family: 'Courier New', monospace; font-size: 12px; }
    p    { line-height: 2px;}
    </style>
    """)
  else:
    fhtml=open(htmlFile,"a")
  fhtml.flush()
  return (f,fhtml)

def closefiles(f,fhtml):
  f.flush()
  fhtml.flush()
  f.close()
  fhtml.close()

def restartNetworking():
  cmd = 'sudo service networking restart'
  #print('ready to do this : '+cmd)
  os.system(cmd)
  
#-main---------------------------------------------
button = Button(2)
initRedLed()

status = 1 if button.is_pressed else 0
prevStatus = status 
turnRedLed(status)


iter=1
iterWithoutCompressor = 0 #nb of iteration since the fridge compress has been seen "ON"
while True:
  (f,fhtml)=openfiles()
  x = datetime.datetime.now()
  now = x.strftime("%d/%m/%Y %H:%M:%S")
  if iter % 1 == 0:
    if button.is_pressed:
      status = 1
    else:
      status = 0
    if prevStatus != status:
        turnRedLed(status)
    prevStatus = status
  if iter % 3 == 0:
    #toggle relay state
    #GPIO.output(relay,abs(GPIO.input(relay)-1))
    pass
  if button.is_pressed:
    turnRedLed(1)
    iterWithoutCompressor = 0
  bartxt,barhtml = bar(iterWithoutCompressor)
  lineQual = lineQuality()
  msg = "{0:<3};{1:>19};{2};{3:>3};".format((iter),now,status,lineQual)
  msgtxt = msg + bartxt
  msghtml = "<p>" + msg  + barhtml + "</p>"
  #msg = str(iter) + ";" + now + ";" + str(status) + ";" + GPIO.intput(relay)
  print (msgtxt)
  f.write(msgtxt+"\n")
  fhtml.write(msghtml)

  if lineQual == "":
    msg = "Wifi seems down; restarting networking service"
    print (msg)
    f.write(msg+"\n")
    fhtml.write("<p>"+msg+"</p>")
    restartNetworking()

  closefiles(f,fhtml)
  if iterWithoutCompressor>alertCeiling:
    sendmail("problem with the fridge ! "+ now)
    print("sending mail")
  iter+=1
  iterWithoutCompressor+=1
  sleep(1*basic_sleep)


