import json 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

msg = MIMEMultipart()
message = "This is an email"

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



