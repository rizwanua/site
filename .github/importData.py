import pandas as pd

from appPkg import create_app, db
from appPkg.models import Stock
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from datetime import datetime, timedelta

'''
In venv not shell:
    
First time initialize a DB: flask db init
Migrating a DB: flask db migrate -m "<comment here>"
Upgrade after migrate: flask db upgrade
'''

# https://www.nasdaq.com/market-activity/stocks/screener


# USE THIS INSTEAD?!
# http://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt
# http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs

url = 'http://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt'
dfInfo = pd.read_csv(url, sep='|')

cond1 = dfInfo['Symbol'] != 'Symbol' # Just in case headers pop in
cond2 = dfInfo['Symbol'] != 'File Creation' # End of file text
cond3 = dfInfo['Market Category'] == 'Q' # NASDAQ Global MarketSM only
cond4 = dfInfo['Test Issue'] == 'N' # Not a test issue
cond5 = dfInfo['Financial Status'] == 'N' # End of file text
cond6 = dfInfo['Symbol'] != 'File Creation' # Issuer not in delinquency/backruptcy/deficient in NASDAQ requirements

dfInfo = dfInfo[cond1 & cond2 & cond3].reset_index() # Apply filters to the df and reset index

# Database     
app = Flask (__name__) 
app.config.from_object(Config) 
db.init_app(app)

with app.app_context():
    print(Stock.query.count())
    
    for x in range(0,len(dfInfo)):
        s = Stock(symbol = dfInfo.loc[x,'Symbol'], 
                  name = dfInfo.loc[x,'Security Name'], 
                  active = True, 
                  lastPrice = float(0.0), 
                  lastUpdateTime = datetime.utcnow()-timedelta(hours=10))
        db.session.add(s)
        
    db.session.commit()
        

with app.app_context():
    print(Stock.query.count())
    # Delete stuff in database:
    st = Stock.query.all()
    for s in st:
        db.session.delete(s)
    db.session.commit()
    print(Stock.query.count())
'''


import time
import yfinance as yf
from yahoofinancials import YahooFinancials

start = time.time()
yf.Ticker("PFE").info['currentPrice'] # 3.6 seconds per call
end = time.time()
print(end - start) 

start = time.time()
YahooFinancials('NIO').get_current_price()
end = time.time()
print(end - start) 

start = time.time()
yf.Ticker("LCID").info['currentPrice'] # 3.6 seconds per call
end = time.time()
print(end - start) 

start = time.time()
YahooFinancials('JD').get_current_price()
end = time.time()
print(end - start) 

'''