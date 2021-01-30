//ED 2021-01-29
//
from gpiozero import Button 
from time import sleep
import datetime

button = Button(2)
f=open("/home/pi/testfrigo.csv","a")
i=1
while True:
    x = datetime.datetime.now()
    now = x.strftime("%d/%m/%Y %H:%M:%S")
    if button.is_pressed:
        status = "1"
    else:
        status = "0"
    msg = str(i) + ";" + now + ";" + status
    print (msg)
    f.write(msg+"\n")
    f.flush()
    sleep(1*60)
    i+=1



