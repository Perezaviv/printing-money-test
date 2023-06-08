from flask import request
from binance.error import ClientError
import logging
from telegram_bot import send_telegram_message

def process_alert(flask_app, app):
    @flask_app.route('/', methods=['POST'])
    def process():
        data = request.get_json()
        print("Received data:", data)

        symbol = data['symbol']
        side = (data['side']).upper()
        order_type = "MARKET"
        quantity = data['quantity']

        print(f"Extracted information - Symbol: {symbol}, Side: {side}, Order type: {order_type}, Quantity: {quantity}")
    
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity
        }


        print("Order parameters:", params)  # Print the order parameters

        order_response = order(app, params)

        if order_response:
            return {
                "code": "success",
                "message": "order executed"
            }
        else:
            print("order failed")

            return {
                "code": "error",
                "message": "order failed"
            }
    return process


def order(app, params):
    try:
        account = app.client.account()
        pnl = float(account['totalUnrealizedProfit'])
        port_value_before = float(account['totalWalletBalance']) 

        response = app.client.new_order(**params)
        logging.info(response)
        account = app.client.account()

        if float(account['totalWalletBalance'])  == float(account['availableBalance']):
            open_or_close = "Closed"
            pnl_percent = round((pnl/port_value_before)*100, 2)
            pnl_values_text = (
                f"Trade P&L: {round(pnl,1)}$ \n"
                f"Trade P&L percent: {pnl_percent}%"
            )
        else:
            open_or_close = "Opened"
            pnl_values_text = ""
        #status_update(open_or_close)
        
        msg = '\n'.join([
            f"Order executed:",
            f"Symbol: {response['symbol']}",
            f"Quantity: {params['quantity']}",
            f"Side: {params['side']}",
            f"Position: {open_or_close}",
            pnl_values_text
        ])
        send_telegram_message(msg)

        return {
            "code": "success",
            "message": "order executed"
        }
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        send_telegram_message('Order failed: {}'.format(error)) # Send a telegram message when order fails
        return {
            "code": "error",
            "message": "order failed"
        }

#def status_update(status):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(os.getenv('GCP_PROJECT_ID'), 'trade_status')

    try:
        if(status == "Opened"):
            data = 'trade_open'.encode('utf-8')
            publisher.publish(topic_path, data)
        elif(status == "Closed"):
            data = 'trade_close'.encode('utf-8')
            publisher.publish(topic_path, data)
    except Exception as e:
        print(f"Failed to publish {status} message: {e}")

