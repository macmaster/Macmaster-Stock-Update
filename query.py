import urllib

tickers = open('tickers.txt')
for tick in tickers:
    stockurl =
        urllib.urlopen('http://download.finance.yahoo.com/d/quotes.csv?s='+tick+'&f=j3')
    price = stockurl.read().rstrip()
    print tick + "\t" + price


