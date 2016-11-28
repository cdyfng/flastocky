import smtplib
import string
import os


class warningEmail():

    def send(self, sub, content):
     HOST = os.environ.get('MAIL_HOST')
     SUBJECT = sub
     #"Test email from Python"
     TO = os.environ.get('MAIL_TO')
     FROM = os.environ.get('MAIL_FROM')
     #text = "Second Python rules them all!"
     text = content
     BODY = string.join((
 	"From: %s" % FROM,
	"To: %s" % TO,
	"Subject: %s" % SUBJECT ,
	"",
	text
	), "\r\n")
     server = smtplib.SMTP(HOST)
     server.login(os.environ.get('MAIL_USERNAME'), os.environ.get('MAIL_PASSWORD'))
     #server = smtplib.SMTP()
     server.sendmail(FROM, [TO], BODY)
     server.quit()


if __name__ == "__main__":
    print "MAIL_HOST: ", os.environ.get('MAIL_HOST')
    print "MAIL_FROM: ", os.environ.get('MAIL_FROM')
    print "MAIL_TO: ", os.environ.get('MAIL_TO')
    print "MAIL_USERNAME: ", os.environ.get('MAIL_USERNAME')
    print "MAIL_PASSWORD: ", os.environ.get('MAIL_PASSWORD')
    print "XUEQIU_USERNAME: ", os.environ.get('XUEQIU_USERNAME')
    print "XUEQIU_PASSWORDHASH: ", os.environ.get('XUEQIU_PASSWORDHASH')
    print "FLASKY_ADMIN: ", os.environ.get('FLASKY_ADMIN')
