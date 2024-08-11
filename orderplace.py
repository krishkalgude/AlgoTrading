from SmartApi import SmartConnect,SmartWebSocket
import xlwings as xw
import pandas as pd
import pyotp
from logzero import logger
obj=SmartConnect(api_key="lHD****A")
data=obj.generateSession("R****70","****",pyotp.TOTP("75JKO2ZF32KHDGRVD*******M").now())
refreshToken=data['data']['refreshToken']
feedToken=obj.getfeedToken()
print(feedToken)


try:
    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": "SBIN-EQ",
        "symboltoken": "3045",
        "transactiontype": "BUY",
        "exchange": "NSE",
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "19500",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": "1"
        }
    orderId=obj.placeOrder(orderparams)
    print("The order ID is :{}".format(orderId))
except Exception as e:
    print("Order placement Failed:{}".format(e.message))
    