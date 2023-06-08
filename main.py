import configtest
from flask import Flask
from binance.um_futures import UMFutures
from order_module import process_alert
from daily_update_module import daily_report


class BinanceApp:
    def __init__(self, api_key, api_secret, base_url):
        self.client = UMFutures(key=api_key, secret=api_secret, base_url = base_url)
        self.positions = self.client.account()

url = "https://testnet.binancefuture.com"

api_key = configtest.API_KEY_TEST
api_secret = configtest.API_SECRET_TEST
app = BinanceApp(api_key, api_secret, url)

flask_app = Flask(__name__)

process_alert(flask_app, app)
daily_report(flask_app, app)


