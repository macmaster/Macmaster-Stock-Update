#!/usr/bin/env python
# notify.cgi
# Alert users when it's time to buy or sell.
# modified to run on python 2.4 for ece 32bit servers
#
# Author: Ronald Macmaster
# Date: 2/07/16

import re
import sys
import time
import urllib
import smtplib

# poll the ticker list every 60 secs and make a feed
# email user at certain threshold

# ticker data
bb_low = {}
bb_high = {}
tickers = ["gdx", "goog", "aapl", "sbux", "yhoo", "ibm", "wdfc", "ha"]

# setup email
email = "macmaster.stocks@gmail.com"
pword = "Physics17"
notify_period = 480 # in minutes (24hrs = 1440mins)

################### Utility Functions ###############################

''' get bollinger band thresholds '''
def set_bollinger():		
	try:
		for tick in tickers:
			# grab json data
			bburl = urllib.urlopen(
				"http://www.bollingeronbollingerbands.com/common/getjson.php?"
				"xml=price&i=price&l1=0&ct=0&ov=0-20-2-0-0-0-0-0-0-0-0&pc=0&pp=&m=&s="
				+ tick +"&w=800&t=0&g=5&q=60"
			)

			bbdata = bburl.read()
			bbdata = bbdata[bbdata.rfind('"date":'):] # extract today's bb data
			regex_low = '"bb_middle1":([0-9.]+)'
			regex_high = '"bb_upper1":([0-9.]+)'
			
			# parse bb prices  
			bb_low[tick] = float(re.findall(re.compile(regex_low), bbdata)[0])
			bb_high[tick] = float(re.findall(re.compile(regex_high), bbdata)[0])
		
		# log bb data
		print "\n\nlow:"
		for low in bb_low:
			print bb_low[low]
		print "\nhigh:"
		for high in bb_high:
			print bb_high[high]

	except:
		print "failed to get bollinger band data!"
		sys.exit()
	# finally: 
	bburl.close()

''' email the notification to the reciever list '''
def email_user(msg):
	#build email content
	rcverlist = open("rcverlist")
	for rcver in rcverlist:
		header = "From: %s\r\n" % ("Ronny's Stock Update")
		header += "To: %s\r\n" % (rcver)
		header += "Subject: Stock Price Update\r\n\r\n"
		msg = header + msg
		try: # send the email
			mail = smtplib.SMTP('smtp.gmail.com', 587)
			mail.ehlo()
			mail.starttls()
			mail.ehlo()
			mail.login(email, pword)
			mail.sendmail(email, rcver, msg)
			print "email sent to : " + rcver
		except:
			print("Failed to send e-mail!")
		# finally:
		mail.close()
	rcverlist.close()


################## notify loop ############################

# poll stock list
txtclock = 0 # email timer
bolclock = 0 # bollinger band timer
set_bollinger()

while True:
	try:
		while True:
			notify = False
			emailmsg = ""
			for tick in tickers:			
				# get raw data & parse price
				stockurl = urllib.urlopen(
					'http://download.finance.yahoo.com/d/quotes.csv?'
					's=' +tick +'&f=l1'
				)
				price = stockurl.read().rstrip()
		
				# send email?
				if txtclock <= 0 and bb_low[tick] > float(price):
					#email
					print(tick+" is getting cheap!\t" + "price: " + price)
					emailmsg += tick+" is getting cheap!\t\tprice: " + price + "\n"
					notify = True
				elif txtclock <= 0 and bb_high[tick] < float(price):
					#email
					print(tick+" is getting expensive!\t" + "price: " + price)
					emailmsg += tick+" is getting expensive!\t\tprice: " + price + "\n"
					notify = True
		
			# maintence branches
			if notify is True:
				print " send emails to rcver list"
				email_user(emailmsg)
				txtclock = notify_period
				emailmsg = ""
				notfiy = False
			if bolclock <= 0:
				bolclock = 1440 # every 24hrs
				set_bollinger()

			txtclock -= 1
			bolclock -= 1
			time.sleep(60)

	except:
		print "failed in the main loop!! "
		print time.asctime()
