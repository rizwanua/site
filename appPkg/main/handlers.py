"""
Description:
    - Get stock ticker price when user is setting up an alert
    - Scheduler runs here to email users if their alert has been triggered.
    - Send issue emails when YahooFinance fails to retrieve stock data
"""
from appPkg import db
from flask import render_template, current_app
from appPkg.email import send_email
from appPkg.models import User, Stock, alertTracker
from threading import Thread
from datetime import datetime, timedelta
from yahoofinancials import YahooFinancials
    
    
def tickerInfo(symbol):
    """
    Query YahooFinance for current stock ticker price

    Parameters
    ----------
    symbol : string
        Stock symbol/ticker.

    Returns
    -------
    integer
        Current price of the stock symbol

    """
    
    stock = Stock.query.filter_by(symbol=symbol).first()

    # Query Y.F. if the stock's last update time is greater than the defined frequency
    if (datetime.utcnow() - stock.lastUpdateTime) > timedelta(minutes=current_app.config['PRICE_CHECK_FREQUENCY']):
        price = YahooFinancials(symbol).get_current_price() # This can take upto 5 seconds per call
        
        # Check if Y.F returns valid data
        if not price:
            sendIssueEmail(stock)
            return None
        
        # Update the stock DB table
        stock.lastPrice = price
        stock.lastUpdateTime = datetime.utcnow() 
        db.session.commit()

    return stock.lastPrice


def sendIssueEmail(stock):
    """
    Use this when Yahoo Finance does not return valid data for a stock in the DB

    Parameters
    ----------
    stock : stock instance

    Returns
    -------
    None.
    """
    
    print('Sending issue email')
    send_email('[StockPriceAlert] Issue with YahooFinance',
               sender=current_app.config['ADMINS'][0],
               recipients=[current_app.config['ADMINS'][0]],
               text_body=render_template('email/issue_with_stock.txt',
                                         stock=stock),
               html_body=render_template('email/issue_with_stock.html',
                                         stock=stock))
    
def sendAlertEmail(alert, stock, user):
    """
    Send an email to the user indicating their alert has been triggered.

    Parameters
    ----------
    alert : alert instance
    stock : stock instance
    user : user instance

    Returns
    -------
    None.

    """
    
    print('Sending alert email')
    alert.status = 'ALERT TRIGGERED' # Update alert in the DB as its now processed
    db.session.commit()

    send_email('[StockPriceAlert] Alert Notification',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/alert_notification.txt',
                                         user=user, stock=stock, 
                                         alert=alert),
               html_body=render_template('email/alert_notification.html',
                                         user=user, stock=stock, 
                                         alert=alert))

    
def async_checkAlerts(app):
    """
    Go through all the alerts to check if any alert has been trigerred 

    Parameters
    ----------
    app : Flask instance

    Returns
    -------
    None.

    """
    
    with app.app_context():
        inProgressAlerts = alertTracker.query.filter_by(status='IN PROGRESS').all()
        for alert in inProgressAlerts:
            
            # Get the stock and user data based off the Alert table.
            stock = Stock.query.filter_by(id=alert.stockID).first()
            user = User.query.filter_by(id=alert.userID).first()

            # Update stock prices if needed
            price = tickerInfo(stock.symbol)

            if price and alert: # Prevents execution if stock symbol is not available on YahooFinance, or alert deleted in DB by user in main thread (race condition)
                # Check if any alerts should be triggered and send notification email to user
                if alert.priceAtUserInput - alert.desiredPrice >= 0: # User is checking for falling stock price
                    if stock.lastPrice <= alert.desiredPrice: # Check if current stock price has fallen to or below alert price
                        sendAlertEmail(alert, stock, user)
                elif alert.priceAtUserInput - alert.desiredPrice < 0: # User is checking for increasing stock price
                    if stock.lastPrice >= alert.desiredPrice: # Check if current stock price has increased to or above alert price
                        sendAlertEmail(alert, stock, user)
                    
    
def checkAlerts(app):
    """
    Based off scheduler. Checks if there are any 'IN PROGRESS' alerts that need to be checked

    Parameters
    ----------
    app : Flask instance
        
    Returns
    -------
    None.

    """
    with app.app_context():
        
        # Only trigger if there are any alerts 'IN PROGRESS' 
        if alertTracker.query.filter_by(status='IN PROGRESS').count() > 0:
            Thread(target=async_checkAlerts, args=[current_app._get_current_object()]).start()
        
        
