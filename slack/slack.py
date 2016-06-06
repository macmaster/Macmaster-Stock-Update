# slack.py
# 
# quick python script to send the
# slack group stock updates
#
# Author: Ronald Macmaster
# Date: 6/5/16

import re
import sys
import time
import urllib
import requests

notify_period = 360 # in minutes (12hrs = 720mins)
bb_low = {}
bb_high = {}
emoji = [":pride:", ":sob:", ":open_mouth:", ":sleeping:"]
def notify_slack(msg):
    # slack json and url data
    edx = time.asctime().__hash__() % len(emoji)
    print "edx: ", edx
    slack_remote = "https://hooks.slack.com/services/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"
    update = {"username": "ronny-script", "icon_emoji": emoji[edx], "text": msg}

    # http request
    response = requests.post(slack_remote, json=update)

    # read response
    data = response.content
    print response.status_code
    print data
    response.close()

# scrape bollinger band thresholds
def set_bollinger():		
    try:
        tickers = open("tickers")
        for tick in tickers:
            # json data
            tick = tick.rstrip()
            bburl = urllib.urlopen("http://www.bollingeronbollingerbands.com/common/getjson.php?xml=price&i=price&l1=0&ct=0&ov=0-20-2-0-0-0-0-0-0-0-0&pc=0&pp=&m=&s="
                                   +tick+"&w=800&t=0&g=5&q=60")
            bbdata = bburl.read()
            bbdata = bbdata[bbdata.rfind('"date":'):] # extract today's bb data
            regex_low = '"bb_middle1":([0-9.]+)'
            regex_high = '"bb_upper1":([0-9.]+)'
            # parse bb prices
            print float(re.findall(re.compile(regex_low), bbdata)[0])
            bb_low[tick] = float(re.findall(re.compile(regex_low), bbdata)[0])
            bb_high[tick] = float(re.findall(re.compile(regex_high), bbdata)[0])
            bburl.close()

        tickers.close()
        print "\n\nlow:"
        for low in bb_low:
            print bb_low[low]
        print "\nhigh:"
        for high in bb_high:
            print bb_high[high]
        
    except:
        print "failed to get bollinger band data!"
        sys.exit()

# begin workflow
txtclock = 0 # notify timer
bolclock = 0 # bollinger band timer
set_bollinger()
while True:
    notify = False
    slackmsg = ""
    tickers = open("tickers")
    for tick in tickers:        
        # get raw data & parse price
        tick = tick.rstrip()
        stockurl = urllib.urlopen('http://download.finance.yahoo.com/d/quotes.csv?s='+tick+'&f=l1')
        price = stockurl.read().rstrip()
        
        # send email?
        if txtclock <= 0 and bb_low[tick] > float(price):
            #email
            print(tick+" is getting cheap!\t" + "price: " + price)
            slackmsg += time.asctime()+"\t\t*"+tick+"* is getting cheap!\t\tprice: `"+price+"`\n"
            notify = True
        elif txtclock <= 0 and bb_high[tick] < float(price):
            #email
            print(tick+" is getting expensive!\t" + "price: " + price)
            slackmsg += time.asctime()+"\t\t*"+tick+"* is getting expensive!\t\tprice: `"+price+"`\n"
            notify = True

    # maintence branches
    if notify is True:
            print " send notfications to slack channel"
            notify_slack(slackmsg)
            txtclock = notify_period
            slackmsg = ""
            notfiy = False
    if bolclock <= 0:
            bolclock = 1440 # every 24hrs
            set_bollinger()

    # update CLK
    txtclock -= 1
    bolclock -= 1
    time.sleep(60)
