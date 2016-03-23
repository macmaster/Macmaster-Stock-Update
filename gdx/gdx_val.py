# gdx_val.py
# 
# Author: Ronny Macmaster
# Date: 3/23/2016
# 
# logs the valuation ratio between
# the price of gold futures and GDX etf
# saves as gdx.csv


# poll goog stock
try:
    txtclock = 0
    while True:
        
        # open log
        pricelog = open("gdx.log", "a")
        
        # get raw data & parse price
        stockurl = urllib.urlopen('http://download.finance.yahoo.com/d/quotes.csv?s=gdx&f=l1')
        price = stockurl.read().rstrip()
        
        # send email?
        if txtclock <= 0 and bb_low > float(price):
            #email
            print("Gold is getting cheap!\t" + "price: " + price)
            email_user("Gold is getting cheap!\n\nprice: " + price)
            txtclock = notif_period * 10
        elif txtclock <= 0 and bb_high < float(price):
            #email
            print("Gold is getting expensive!\t" + "price: " + price)
            email_user("Gold is getting expensive!\n\nprice: " + price)
            txtclock = notif_period * 10
        
        # log & delay
        pricestr = time.asctime() + "\tPrice: " + price + "\n"
        pricelog.write(pricestr)
        time.sleep(6)
        txtclock -= 1
        pricelog.close()
        
finally:
    print("finished execution!")
    pricelog.close()
    

