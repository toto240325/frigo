import RPi.GPIO as GPIO 
from gpiozero import Button 
from time import sleep
import datetime

#GPIO.setwarnings(False) 
#GPIO.setmode(GPIO.BOARD) # Use physical pin numbering

#relay = 14
#GPIO.setup(7, GPIO.OUT, initial=GPIO.LOW)

button = Button(2)
f=open("/home/pi/testfrigo.csv","a")
i=1
j=0 #nb of iteration since the fridge compress has been seen "ON"
while True:
  x = datetime.datetime.now()
  now = x.strftime("%d/%m/%Y %H:%M:%S")
  if i % 1 == 0:
    if button.is_pressed:
      status = "1"
      j = 0
    else:
      status = "0"
  if i % 3 == 0:
    #toggle relay state
    #GPIO.output(relay,abs(GPIO.input(relay)-1))
    j=0
  msg = str(i) + ";" + now + ";" + status 
  #msg = str(i) + ";" + now + ";" + status + ";" + GPIO.intput(relay)
  print (msg)
  f.write(msg+"\n")
  f.flush()
  sleep(1*60)
  i+=1
  j+=1



