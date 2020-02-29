import sys
import os
from datetime import datetime

import smtplib #library for smtp protocol
from email.mime.text import MIMEText #library for Multipurpose Internet Mail Extensions(MIME)
from email.mime.multipart import MIMEMultipart

os.environ['TZ']="Asia/Calcutta"
#**********email account credentials******************
login = "saurabhkmr70"
# Google's App specific password
password = "rovwvhyvtpcdximj"
from_addr = 'saurabhkmr70@gmail.com'     #mail from

def send_email(toaddr,subject, message):

	global login
	global password
	global from_addr

	fromaddr = "saurabhkmr70@gmail.com"
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = subject

	body = message #body of message
	msg.attach(MIMEText(body,'plain')) #attaching body to message

	server = smtplib.SMTP('smtp.gmail.com',587) #server name(eg:smtp.yahoo.com),port add(465 for yahoo)
	server.ehlo()#for esmtp server for non-ESMPT server use helo()
	server.starttls()#starts Transport Layer Security mode
	server.ehlo()
	server.login(login,password)#loging details
	text = msg.as_string()#converting smtp objest to string
	try:
		problem = server.sendmail(fromaddr,toaddr,text)
		print "\nMessage sent Successfully to ",toaddr
		sys.stdout.flush()
		server.quit()
	except:
		print"\nFailed to send mail:",problem
		sys.stdout.flush()
		server.quit()


if __name__ == '__main__':
    send_email("ykings.saurabh@gmail.com", "Hi, from pythonanywhere", "Hello world, Message sent at :" + str(datetime.now() ) )







