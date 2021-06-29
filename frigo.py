#!/usr/bin//env python
# -*- coding: UTF-8 -*-
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
import requests
import socket
import params


#subprocess.call(['modprobe', 'w1-gpio'])
#subprocess.call(['modprobe', 'w1-therm'])

#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')
os.system('/usr/sbin/modprobe w1-gpio')
os.system('/usr/sbin/modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def reportTemp(temp):
  try:
    hostname = socket.gethostname()
    r = requests.get("http://192.168.0.147/monitor/getEvent.php?eventFct=add&host={0}&type=tempFrigo&text={1}".format(hostname,temp))
  except Exception as error:
    print("there was an exception : " + str(error))


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    global f
    lines = read_temp_raw()
    try:
      while lines[0].strip()[-3:] != 'YES':
          time.sleep(0.2)
          lines = read_temp_raw()
      equals_pos = lines[1].find('t=')
      if equals_pos != -1:
          temp_string = lines[1][equals_pos+2:]
          temp_c = float(temp_string) / 1000.0
          temp_f = temp_c * 9.0 / 5.0 + 32.0
          return temp_c if temp_c < 25 else 25   # when Pi has just rebooted this value can be crazy, like 85
    except:
      return -2


def bar(x):
  t = ""
  for i in range(int(x*2)):
    t = t + "-"
  return t

def bar2(x):
  t = ""
  x2 = int(x)
  if x2 < 0:
    for i in range(-5,x2):
      t = t + " "
    for i in range(x2,0):
      t = t + "-"
  if x2 > 0:
    for i in range(-5,0):
      t = t + " "
    for i in range(0, x2):
      t = t + "+"
  return t


def lineQuality():
  global fhtml
  cmd="sudo /sbin/iwconfig wlan0 2> /dev/null > /tmp/a.txt && /usr/bin/awk '/Qual/ {print $2}' </tmp/a.txt"
  str=subprocess.check_output(cmd, shell=True).rstrip()
  msg = "Q:"+str+"<-Q"
  #print("lineQuality : "+msg)
  #fhtml.write(msg)
  result = (str[8:])
  return result

def statusHtml(status):
  if status == 1:
    return '<span style="color:red;font-weight:bold">1</span>'
  else:
    return '0'

def bar(j):
  if j<ceilingCompressorOFF*0.75:
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
   <table><tr><th>i<th>time<th>S<th>Q<th>t<th>temp<th>ON<th>NoCompressor</tr>
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


def checkWifi():
  global f,fhtml
  (f,fhtml)=openfiles()
  lineQual = lineQuality()
  if lineQual == "":
    msg = "Wifi seems down; restarting networking service "
    print (msg)
    f.write(msg+"\n")
    fhtml.write("<p>"+msg+"</p>")
    #restartNetworking()
  closefiles(f,fhtml)
  
def sendmail(subject,message):
  try:
    msg = MIMEMultipart()

    mailer = params.mailer
    mailer_pw = params.mailer_pw
    msg['From'] = params.from_email
    msg['To'] = params.to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()

    server.login(mailer, mailer_pw)
    server.sendmail(msg['From'],msg['To'], msg.as_string())
    server.close()


    #server = smtplib.SMTP('smtp.gmail.com: 587')
    #server.starttls()
    #server.login(msg['From'], password)
    #server.sendmail(msg['From'], msg['To'], msg.as_string())
    #server.quit()
  except Exception as error:
    msg = "there was an exception : " + str(error)
    print(msg)

def updateEmail():
  #global iterCompressorOFF,iterCompressorON,temp
  try:
    x = datetime.datetime.now()
    now = x.strftime("%H:%M:%S")
    toBeSent = False
    msg = now 
    if iterCompressorOFF > ceilingCompressorOFF:
      msg = msg + " - nb iter with compressor OFF : " + str(iterCompressorOFF)
      print ("Sending email : "+msg)
      toBeSent = True
    if iterCompressorON > ceilingCompressorON:
      msg = msg + " - nb iter with compressor ON : " + str(iterCompressorON)
      print ("Sending email : "+msg)
      toBeSent = True
    if temp > ceilingTemp:
      msg = msg + " - Temperature too high !!! : " + str(temp)
      print ("Sending email : "+msg)
      toBeSent = True
    if temp < floorTemp:
      msg = msg + " - Temperature too low !!! : " + str(temp)
      print ("Sending email : "+msg)
      toBeSent = True
    if toBeSent:
      sendmail("😬 😬Fridge problem" + msg,msg)
  except Exception as error:
    msg = "there was an exception : " + str(error)
    print(msg)
    sendmail("Problem with the fridge (exception !)",msg)
    triggerCompressor(0)
    turnRedLed(0)
  

def updateWeb():
  global iterCompressorOFF,f,fhtml,temp
  (f,fhtml)=openfiles()
  x = datetime.datetime.now()
  #now = x.strftime("%d/%m/%Y %H:%M:%S")
  now = x.strftime("%d/%m %H:%M:%S")

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

def checkCompressor():
  global button,status,prevStatus,iterCompressorOFF

  if button.is_pressed:
    status = 1
    iterCompressorOFF = 0
  else:
    status = 0
  if prevStatus != status:
    turnRedLed(status)
    prevStatus = status


def triggerCompressor(state):
    #toggle relay state
    GPIO.output(relayGPIO,state)
  
#-main---------------------------------------------
csvFile = "/home/pi/frigo.csv"
htmlFile = "/home/pi/frigo/html/frigo.html"
#GPIO.setwarnings(False) 
#GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setmode(GPIO.BCM) # logical GPIO numbering
relayGPIO =  23 # GPIO23 = pin 16
GPIO.setup(relayGPIO, GPIO.OUT, initial=GPIO.LOW)
basic_sleep = 60 #normally 60 
bar_divider = 5
ceilingCompressorON =  7   #max normal nb of iteration with compressor ON
ceilingCompressorOFF =  24 #max normal nb of iteration with compress OFF
ceilingTemp =  3           #max normal temperature
floorTemp =    1           #min normal temperature
fhtml = None
f = None

button = Button(2)
initRedLed()

status = 1 if button.is_pressed else 0
prevStatus = status 
turnRedLed(status)
lineQual = lineQuality()
f = None
fhtml = None
sec=0
iter = 0
iterCompressorON = 0
iterCompressorOFF = -1 #nb of iterations since the fridge compressor has been seen "ON"; initial value of -1 to force check after program restart 
while True:
  try:
    if sec % 1 == 0:
      temp = read_temp()

    if sec % 60 == 0:
      pass
      #reportTemp(temp)

    if sec % 20 == 0:
      checkWifi()

    if sec % 60 == 0:  #check every minute if temperature requires triggering the compressor
      if temp < 2.5:
        triggerCompressor(0)
      if (iterCompressorOFF >= 0) or (iterCompressorOFF == -1): # if the compressor has not been ON for more than X minutes or if the program has just been restarted
        if temp > 2.5:
          triggerCompressor(1)

    if sec % 2 == 0:
      checkCompressor()

    if sec % 60  == 0:
      updateWeb()

    if sec % 60  == 0:
      updateEmail()

    if sec % 60 == 0:
      iter += 1
      if status == 0:
        iterCompressorOFF += 1
        iterCompressorON = 0
      else:
        iterCompressorON += 1
        iterCompressorOFF = 0
    
  except Exception as error:
    msg = "there was an exception : " + str(error)
    print(msg)
    sendmail("Problem with the fridge (exception !)",msg)
    triggerCompressor(0)
    turnRedLed(0)

  sec += 1
  sleep(1)


