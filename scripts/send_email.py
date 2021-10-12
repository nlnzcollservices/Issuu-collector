import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# import socks
# import sys
# print(sys.path)

#'proxy_port' should be an integer
#'PROXY_TYPE_SOCKS4' can be replaced to HTTP or PROXY_TYPE_SOCKS5



def send_email(mail_content):

	#proxies = proxies = {"http": "wlgproxyforservers.dia.govt.nz:8080", "https": "wlgproxyforservers.dia.govt.nz:8080", "ftp": "wlgproxyforservers.dia.govt.nz:8080"}
	# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, "wlgproxyforservers.dia.govt.nz", 8080)
	# socks.wrapmodule(smtplib)

	print(mail_content)
	mail_content = "test"
	#The mail addresses and password
	sender_address = 'collect.podcasts@gmail.com'
	sender_pass = 'podcasts'
	receiver_address = 'svetlana.koroteeva@dia.govt.nz'
	#Setup the MIME
	message = MIMEMultipart()
	message['From'] = sender_address
	message['To'] = receiver_address
	message['Subject'] = 'A test mail with not enabled publications .'   #The subject line
	#The body and the attachments for the mail
	message.attach(MIMEText(mail_content, 'plain'))
	#Create SMTP session for sending the mail
	session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
	session.starttls() #enable security
	session.login(sender_address, sender_pass) #login with mail_id and password
	text = message.as_string()
	session.sendmail(sender_address, receiver_address, text)
	session.quit()
	print('Mail Sent')
if __name__ == '__main__':
	send_email("test")