#from pathlib import Path
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import RPi.GPIO as GPIO 
from gpiozero import Button 
from time import sleep
import os
import datetime

csvFile = "/home/pi/testfrigo.csv"
htmlFile = "/home/pi/frigo/html/testfrigo.html"
#GPIO.setwarnings(False) 
#GPIO.setmode(GPIO.BOARD) # Use physical pin numbering

#relay = 14
#GPIO.setup(7, GPIO.OUT, initial=GPIO.LOW)
basic_sleep = 60 #normally 60 
bar_divider = 5
alertCeiling = 80

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


button = Button(2)
initRedLed()

status = 1 if button.is_pressed else 0
prevStatus = status 
turnRedLed(status)

f=open(csvFile,"a")

if not os.path.exists(htmlFile):
  fhtml=open(htmlFile,"a")
  fhtml.write("<html>")
  fhtml.write ("""\
  <style type="text/css">
   p {line-height: 2px;}
  </style>
  """)
else:
  fhtml=open(htmlFile,"a")
fhtml.flush()

iter=1
iterWithoutCompressor = 0 #nb of iteration since the fridge compress has been seen "ON"
while True:
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
  msg = str(iter) + ";" + now + ";" + str(status) + "; " + bartxt
  msghtml = "<p>" + str(iter) + ";" + now + ";" + str(status) + "; " + barhtml + "</p>"
  #msg = str(iter) + ";" + now + ";" + str(status) + ";" + GPIO.intput(relay)
  print (msg)
  f.write(msg+"\n")
  f.flush()
  fhtml.write(msghtml)
  fhtml.flush()
  if iterWithoutCompressor>alertCeiling:
    sendmail("problem")
    print("sending mail")
  iter+=1
  iterWithoutCompressor+=1
  sleep(1*basic_sleep)



