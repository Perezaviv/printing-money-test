from datetime import datetime
from telegram_bot import send_telegram_message
from flask import jsonify

START_BALANCE = 514.69  # global variable to hold the starting balance

def daily_report(flask_app, app):
    @flask_app.route('/daily_report', methods=['GET'])
    def daily():

        # Get the current portfolio value
        account = app.client.account()
        portfolio_value = float(account['totalWalletBalance'])
        available_balance = float(account['availableBalance'])

        # Check if there is an open trade
        if portfolio_value == available_balance:
            open_trade = "No"
            current_pnl = 0
            current_pnl_percent = 0
        else:
            open_trade = "Yes"
            for position in account['positions']:
                if position['symbol'] == 'BTCUSDT':  
                    current_pnl = float(position['unrealizedProfit'])
            current_pnl_percent = round((current_pnl/portfolio_value)*100, 2)

        # Calculate the daily P&L
        global START_BALANCE  # declare the variable as global to update it
        daily_pnl = portfolio_value - START_BALANCE
        daily_pnl_percent = round((daily_pnl/portfolio_value)*100, 2)
        START_BALANCE = portfolio_value

        # Send the report
        send_report(round(portfolio_value, 1), open_trade, round(daily_pnl,1), daily_pnl_percent, round(available_balance, 1), round(current_pnl, 1), current_pnl_percent)

        response = {
            'portfolio_value': round(portfolio_value, 1),
            'open_trade': open_trade,
            'daily_pnl': round(daily_pnl, 1),
            'daily_pnl_percent': daily_pnl_percent,
            'current_pnl': round(current_pnl, 1),
            'current_pnl_percent': current_pnl_percent
            }

        return jsonify(response), 200

    return daily

def send_report(portfolio_value, open_trade, daily_pnl, daily_pnl_percent, available_balance, current_pnl, current_pnl_percent):
    report_date = datetime.now().strftime("%d/%m/%Y")
    if(open_trade == "Yes"):
        current_pnl_values = (
            f"Current P&L: {current_pnl}$ \n"
            f"Current P&L percent: {current_pnl_percent}%"
        )
    else:
        current_pnl_values =""
    report = '\n'.join([
        f"Daily report {report_date}:",
        f"Portfolio value: {portfolio_value}",
        f"Available balance: {available_balance}",
        f"Daily P&L: {daily_pnl}$",
        f"Daily P&L percent: {daily_pnl_percent}%",
        f"Open trade: {open_trade}",
        current_pnl_values
    ]) 
    send_telegram_message(report)
        