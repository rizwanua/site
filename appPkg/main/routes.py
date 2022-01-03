"""
Description:
    Routes for main app (Manage Stock Alerts) 
"""


from flask import render_template, flash, redirect, url_for, current_app, request, session
from flask_login import current_user, login_required
from appPkg import db
from appPkg.main import bp
from appPkg.models import Stock
from appPkg.main.forms import SelectStockForm, EnterPriceForm, DeleteStockForm
from appPkg.models import User, Stock, alertTracker
from appPkg.main.handlers import tickerInfo
from appPkg.main.syslog import logInfo
from datetime import datetime, timedelta

@bp.route('/')
@bp.route('/index')
def index():
    """
    Route to Index webpage.

    Returns
    -------
    HTML template
    """       
    return render_template("index.html")

@bp.route('/about')
def about():
    """
    Route to About webpage.

    Returns
    -------
    HTML template
    """
    if current_user.is_authenticated:
        logInfo(f'About as user {current_user.id}') # Log client information
    else:
        logInfo(f'About as anonymous') # Log client information
        
    return render_template("about.html")

@bp.route('/managealerts', methods=['GET', 'POST'])
@login_required
def manage_alerts():
    """
    Description:
        Manage alerts page can be both GET and POST requests. Both will display existing alerts for user.
        POST - user can add or delete existing alerts.
        GET - Display relevant data on initial page load
        
    High level:
        If POST:
            Check if user is adding or deleting stock alerts
        Else (GET):
            Display a dropdown fo all stocks for the user to add an alert

    Returns
    -------
    HTML template
    Redirect webpage
    """   
    logInfo(f'ManageAlerts as user {current_user.id}') # Log client information
    formSelectStock = SelectStockForm()
    formDeleteStock = DeleteStockForm()
    strAlertsList, userStocks, userAlertCounts = getUserData() # Get user related alerts data. See "getUserData" for more info

    if request.method == 'POST': # POST request
        
        if request.form.get('userAddStock'): # User is adding an alert
            # Get the symbol and run it through tickerInfo
            selectedStock = request.form.get('userAddStock')
            lastPrice = tickerInfo(selectedStock.split(' ')[0])
            
            if lastPrice:
                # For a valid price, send the user over to the "enter price" page
                # Using Flask session variable as a way to send user data over, instead of using URL which can be modified. Limits errors and security issues
                session["selectedStock"] = selectedStock.split(' ')[0] # prevent stock from being modified in URL parameter
                session["lastPrice"] = round(float(lastPrice),2)
                return redirect(url_for('main.enter_price', userid=current_user.id)) 
            else:
                # Invalid price, display an eerror.
                flash(f'ERROR: There is an issue accessing data for {selectedStock.split(" ")[0]}. Please try another stock.')
                return redirect(url_for('main.manage_alerts', userid=current_user.id))
            
        elif request.form.get('deleteUserAlert'): # User is deleting an alert
            # Parse the field to isolate the stock symbol
            # Delete the stock from the DB.
            selectedStock = request.form.get('deleteUserAlert')
            deleteAlertID = int(selectedStock.split(':')[1].split(')')[0])
            deleteThis = alertTracker.query.filter_by(userID=current_user.id, id=deleteAlertID).first()
            db.session.delete(deleteThis)
            db.session.commit()
            flash(f'Deleted {selectedStock}.')
            return redirect(url_for('main.manage_alerts', userid=current_user.id))
        else:
            return redirect(url_for('main.manage_alerts', userid=current_user.id))
        
    else: # GET request
        
        allStocks = set()
        if userAlertCounts < current_app.config['ALERTS_PER_USER']:
            # If the user has not reached their max number of alerts, display a dropdown of all stocks in the stocks table
            stocks = Stock.query.all()
            for x in stocks:
                allStocks.add(str(x.symbol) + ' - ' + str(x.name))
                
        return render_template("manage_alerts.html", allStocks = allStocks, formSelectStock=formSelectStock, formDeleteStock=formDeleteStock,
                               userid=current_user.id, strAlertsList=strAlertsList, userStocks=userStocks, userAlertCounts=userAlertCounts )


@bp.route('/enterprice', methods=['GET', 'POST'])
@login_required
def enter_price():
    """
    Route to new page for user to enter price when setting an alert. 
    Eventually to be transitioned off via AJAX onto the main "manage_alerts" page

    Returns
    -------
    HTML template
    """
    logInfo(f'EnterPrice as user {current_user.id}') # Log client information
    selectedStock = session.get("selectedStock")
    lastPrice = session.get("lastPrice")
    formUserPrice = EnterPriceForm()
    
    if formUserPrice.validate_on_submit():            
        newAlert = alertTracker(userID = current_user.id, 
                                stockID = Stock.query.filter_by(symbol=selectedStock).first().id,
                                priceAtUserInput = lastPrice,
                                desiredPrice = formUserPrice.desiredPrice.data,
                                status = 'IN PROGRESS')
        db.session.add(newAlert)
        db.session.commit()
        flash(f'Alert is now active for {selectedStock}.')
        return redirect(url_for('main.manage_alerts', userid=current_user.id))
    
    return render_template("enter_price.html", userid=current_user.id, formUserPrice=formUserPrice,
                           selectedStock=selectedStock, lastPrice=lastPrice)
    
    
@login_required
def getUserData():
    """
    Get user related alerts data.
    userAlertCounts - Number of alerts the user has currently set
    userStocks - Alert info (stock symbol, price). Will be displayed in the "Delete alert" section  of the page
    strAlertsList - String containing data to display in "current alerts for user" sction of the page
    
    ***FUTURE IMPROVEMENT: Use userStocks instead of strAlertsList to populate the "current alerts" section as well.

    Returns
    -------
    strAlertsList : list
        User alerts data.
    userStocks : list
        List of dictionary containing data for each alert
    userAlertCounts : integer
        Number of alerts per user

    """

    userAlertCounts = alertTracker.query.filter_by(userID=current_user.id).count()
    userStocks = [] 
    
    if userAlertCounts > 0:
        strAlertsList = ''
        userAlerts = alertTracker.query.filter_by(userID=current_user.id)
        
        for alert in userAlerts:
            stockSymbol = Stock.query.filter_by(id=alert.stockID).first().symbol
            
            # Append the string with information
            strAlertsList += '\n' + str(stockSymbol) + ' - Alert set for $' + str(alert.desiredPrice) + \
                            '. Stock price when alert set was $' + str(alert.priceAtUserInput) + \
                                '. Current Status: ' + str(alert.status)
                                
            # Add similar data to a list 
            userStock = {
                "alertTrackerID": alert.id, 
                "symbol": stockSymbol,
                "alertPrice": alert.desiredPrice
            }
            userStocks.append(userStock) 
    else:
        userStocks = [] 
        strAlertsList = 'There are currently no stock alerts set for this user.'   
        
    return strAlertsList, userStocks, userAlertCounts
