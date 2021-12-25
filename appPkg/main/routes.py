from appPkg import db
from appPkg.main import bp
from appPkg.models import Stock
from flask import render_template, flash, redirect, url_for, current_app, request, session
from appPkg.main.forms import SelectStockForm, EnterPriceForm, DeleteStockForm
from datetime import datetime, timedelta
from flask_login import current_user, login_required
from appPkg.models import User, Stock, alertTracker
from yahoofinancials import YahooFinancials



@bp.route('/')
@bp.route('/index')
def index():
    return render_template("index.html")


@bp.route('/managealerts/<userid>', methods=['GET', 'POST'])
@login_required
def manage_alerts(userid):
    formSelectStock = SelectStockForm()
    formDeleteStock = DeleteStockForm()
    userAlertCounts = alertTracker.query.filter_by(userID=current_user.id).count()
    userStocks = [] 
    
    if userAlertCounts > 0:
        userAlertsDB = alertTracker.query.filter_by(userID=current_user.id)
        strAlertsList = ''
        
        for x in userAlertsDB:
            stockTicker = Stock.query.filter_by(id=x.stockID).first().symbol
            strAlertsList += '\n- Alert set for ' + str(stockTicker) + ' at $' + str(x.desiredPrice) + '. Current Alert Status: ' + str(x.status)
            userStock = {
                "alertTrackerID": x.id, 
                "symbol": stockTicker,
                "alertPrice": x.desiredPrice
            }
            userStocks.append(userStock) 
    else:
        strAlertsList = 'There are currently no stock alerts set for this user.'            
        
    if request.method == 'POST':
        if request.form.get('userAddStock'):
            selectedStock = request.form.get('userAddStock')
            lastPrice = tickerInfo(selectedStock.split(' ')[0])
            session["selectedStock"] = selectedStock.split(' ')[0] # prevent stock from being modified in URL parameter
            session["lastPrice"] = round(float(lastPrice),2)
            return redirect(url_for('main.enter_price', userid=userid)) 
        elif request.form.get('deleteUserAlert[]'):
            selectedStock = request.form.get('deleteUserAlert[]')
            deleteAlertID = int(selectedStock.split(':')[1].split(')')[0])
            deleteThis = alertTracker.query.filter_by(userID=current_user.id, id=deleteAlertID).first()
            db.session.delete(deleteThis)
            db.session.commit()
            flash(f'Deleted {selectedStock}.')
            return redirect(url_for('main.manage_alerts', userid=current_user.id))
        else:
            return redirect(url_for('main.manage_alerts', userid=current_user.id))
        
    else: # GET
        
        allStocks = set()
        if userAlertCounts < current_app.config['ALERTS_PER_USER']:
            stocks = Stock.query.all()
            for x in stocks:
                allStocks.add(str(x.symbol) + ' - ' + str(x.name))
                
        return render_template("manage_alerts.html", allStocks = allStocks, formSelectStock=formSelectStock, formDeleteStock=formDeleteStock,
                               userid=current_user.id, strAlertsList=strAlertsList, userStocks=userStocks, userAlertCounts=userAlertCounts )

@bp.route('/enterprice/<userid>', methods=['GET', 'POST'])
@login_required
def enter_price(userid):
    selectedStock = session.get("selectedStock")
    lastPrice = session.get("lastPrice")
    formUserPrice = EnterPriceForm()
    
    if formUserPrice.validate_on_submit():            
        newAlert = alertTracker(userID = current_user.id, 
                                stockID = Stock.query.filter_by(symbol=selectedStock).first().id,
                                priceAtUserInput = lastPrice,
                                desiredPrice = formUserPrice.desiredPrice.data,
                                status = 'IN PROGRESS',
                                lastCheckTime = datetime.utcnow())
        db.session.add(newAlert)
        db.session.commit()
        flash(f'Alert is now active for {selectedStock}.')
        return redirect(url_for('main.manage_alerts', userid=current_user.id))
    
    return render_template("enter_price.html", userid=current_user.id, formUserPrice=formUserPrice,
                           selectedStock=selectedStock, lastPrice=lastPrice)
    
    
@login_required
def tickerInfo(symbol):
    currStock = Stock.query.filter_by(symbol=symbol).first()
    
    if (datetime.utcnow() - currStock.lastUpdateTime) > timedelta(minutes=10):
        price = YahooFinancials(symbol).get_current_price() # Upto 5 seconds per call
        
        currStock.lastPrice = price
        currStock.lastUpdateTime = datetime.utcnow() 
        db.session.commit()

    return currStock.lastPrice
    
